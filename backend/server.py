from pydantic import BaseModel, Field

import os
import uvicorn
import shutil
import base64
from typing import List, Dict, Any, Optional,Literal

from fastapi import FastAPI, HTTPException, UploadFile, File, Form 
from fastapi.middleware.cors import CORSMiddleware
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain.chains.openai_functions import create_structured_output_runnable

import logging
# --- 启用 LangChain 调试日志 ---
logging.basicConfig(level=logging.DEBUG)

origins = [
    "http://127.0.0.1:5173",  # 您的前端开发服务器地址
    "http://localhost:5173",   # 另一个可能的本地地址
    "http://localhost:5173",   # 另一个可能的本地地址
    # "https://your-production-frontend.com", # 如果未来有生产环境，也需要添加
]

# --- 辅助结构定义 ---
class NodeData(BaseModel):
    """content节点数据负载，用于存储解析后的规则内容，使用index索引required_attributes数组。"""
    
    # logicType 仅当 type 为 'logic' 时为 'AND' 或 'OR'，否则为空字符串
    logicType: Literal['AND', 'OR', ''] = Field(
        ..., 
        description="仅当type为'logic'时为'AND'或'OR'，否则为''。"
    ) 
    
    # label 仅当 type 为 'content' 时有效
    label: str = Field( 
        description="规则内容。仅当type为'content'时有效。默认为''。每一项的主语或宾语尽量需要存在于target_objects中，用于表达具体的违规状态。每一条规则需要尽可能原子化。"
    )

class Node(BaseModel):
    """逻辑图中的节点。"""
    id: str = Field(..., description="节点唯一编号。")
    type: Literal['logic', 'content'] = Field(..., description="节点类型：'logic'用于AND/OR, 'content'用于规则内容")
    data: NodeData

class Edge(BaseModel):
    """逻辑图中的边。"""
    id: str = Field(..., description="边的唯一编号。")
    source: str = Field(..., description="源节点ID。")
    target: str = Field(..., description="目标节点ID。")


# --- 最终输出 Schema ---
class VisualDetection(BaseModel):
    target_objects: List[str] = Field(
        ..., 
        description="后续进行规则判断时，视觉模型需要聚焦的对象列表。必须是详细、准确、可区分的自然语言描述，指导视觉模型进行检测。"
    )

class TriggerLogic(BaseModel):
    nodes: List[Node] = Field(..., description="逻辑图中的节点列表。")
    edges: List[Edge] = Field(..., description="逻辑图中的边列表。")
    temporal_threshold_seconds: int = Field(
        ..., 
        description="持续多少秒则认为违反规则。如果监管意图中显式规定了时长，则值为-1，并将时长信息放在required_attributes中；否则，这里给出一个推荐的秒数阈值（> 0）。"
    )

class RuleOutputSchema(BaseModel):
    """最终模型输出的完整结构。"""
    visual_detection: VisualDetection
    trigger_logic: TriggerLogic
    alert_message: str = Field(
        ..., 
        description="当规则被违反后，提示给用户或管理员的告警信息和建议，应清晰指导下一步操作。"
    )
    
    
# Server part
# --- 配置 ---
# 存储上传文件的目录
UPLOAD_DIR = "uploaded_files" 
os.makedirs(UPLOAD_DIR, exist_ok=True) # 确保目录存在

# --- 1. 初始化 FastAPI 应用 ---
app = FastAPI(
    title="LLM 规则生成代理服务",
    description="安全地代理 LangChain 结构化输出调用。",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 设置允许的源列表
    allow_credentials=True,  # 允许携带 cookie/授权头
    allow_methods=["*"],  # 允许所有 HTTP 方法 (GET, POST, PUT, DELETE, OPTIONS, etc.)
    allow_headers=["*"],  # 允许所有请求头
)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL") # 兼容 API 的 URL
OPENAI_MODEL = os.environ.get("OPENAI_MODEL")
if not OPENAI_API_KEY:
    print("🚨 警告: OPENAI_API_KEY 环境变量未设置。")

# 初始化模型
# 使用 create_structured_output_runnable 方法，它会使用 OpenAI 的 Function Calling 或 JSON Mode
llm = ChatOpenAI(
    model=OPENAI_MODEL, # 确保模型支持多模态和JSON模式
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL, # 用于兼容 API
    temperature=0.3,
    frequency_penalty=0.1
)

# 使用 Pydantic 模型创建结构化输出链
structured_chain = llm.with_structured_output(
    schema=RuleOutputSchema,
    method='json_schema'
)

# structured_chain = create_structured_output_runnable(
#     output_schema=RuleOutputSchema,
#     llm=llm,
# )

# --- 辅助函数：将文件转换为 Base64 ---
def file_to_base64_data_uri(file_path: str, mime_type: str) -> str:
    """读取文件内容，编码为 Base64 并返回 data URI 格式。"""
    try:
        with open(file_path, "rb") as f:
            encoded_content = base64.b64encode(f.read()).decode("utf-8")
        return f"data:{mime_type};base64,{encoded_content}"
    except Exception as e:
        print(f"Error encoding file {file_path}: {e}")
        return ""

# --- 3. 定义路由 ---
@app.post("/api/generate-rule", response_model=RuleOutputSchema)
async def generate_rule(
    rule_name: str = Form(..., description="监管规则名称"),
    rule_intent: str = Form(..., description="监管意图的自然语言描述"),
    # 接收多个文件：图片和视频
    files: Optional[List[UploadFile]] = File(None, description="图片或视频文件列表")):
    """
    接收监管规则输入和图片，调用 LLM 生成结构化的视觉检测规则。
    """
    files = files if files is not None else []
    
    if not OPENAI_API_KEY:
         raise HTTPException(status_code=503, detail="API 服务未配置。")
         
    # 构造多模态消息内容
    uploaded_paths = []
    base64_parts = []
    
    try:
        # 1. 文件存储和 Base64 编码
        for file in files:
            file_extension = file.filename.split(".")[-1].lower()
            mime_type = file.content_type
            
            # 创建存储路径
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            uploaded_paths.append(file_path)

            # 将文件内容流式写入硬盘
            with open(file_path, "wb") as buffer:
                # 使用 shutil.copyfileobj 进行流式写入，防止大文件占用过多内存
                shutil.copyfileobj(file.file, buffer)
            
            # 仅将图片转换为 Base64 供 LLM 使用
            # 视频文件不进行 Base64 转换，因为太大，且 LLM 依赖关键帧
            if mime_type.startswith("image/"):
                base64_uri = file_to_base64_data_uri(file_path, mime_type)
                if base64_uri:
                    base64_parts.append({
                        "type": "image_url",
                        "image_url": {"url": base64_uri}
                    })
            elif mime_type.startswith("video/"):
                print(f"INFO: 视频文件 '{file.filename}' 已存储。")
                base64_uri = file_to_base64_data_uri(file_path, mime_type)
                if base64_uri:
                    base64_parts.append({
                        "type": "video_url",
                        "video_url": {"url": base64_uri}
                    })


        # 2. 构造多模态消息内容 (与之前逻辑相同)
        prompt_text = f"""
        你是一名专业的规则引擎配置专家。请严格分析以下监管意图和视觉参考。
        请严格根据以下输入信息和 Pydantic Schema 生成视觉检测规则的结构化 JSON 输出。
        
        1. 监管规则名称: {rule_name}
        2. 监管意图: {rule_intent}
        3. 视觉参考(可选)：已在消息中提供图片和视频关键帧。
        
        **重要提示**: temporal_threshold_seconds 的逻辑如下：如果监管意图中显式规定了时长，则将 'temporal_threshold_seconds' 设为 -1，并将时长信息放入 required_attributes 中；否则，给出一个推荐的秒数阈值（> 0）。
        """ + r"""
        例如：检测工人是否玩手机，是否佩戴黄色安全帽
        EXAMPLE_JSON_OUTPUT = 
{
"visual_detection": {
    "target_objects": ["工人","手机","黄色安全帽"],
},
"trigger_logic": {
    "edges": [
        {
          "id": "0",
          "source": "0",
          "target": "1"
        },
        {
          "id": "1",
          "source": "0",
          "target": "2"
        }
    ],
    "nodes": [
        {
          "data": {
            "label": "",
            "logicType": "OR"
          },
          "id": "0",
          "type": "logic"
        },
        {
          "data": {
            "label": "工人正在玩手机",
            "logicType": ""
          },
          "id": "1",
          "type": "content"
        },
        {
          "data": {
            "label": "工人未佩戴黄色安全帽",
            "logicType": ""
          },
          "id": "2",
          "type": "content"
        }
      ],
    
},
"alert_message": "检测到工人不在场或未佩戴黄色安全帽"
}

注意：如果不需要拆分逻辑则单独一个conten node即可，不需要edge或logic node。
如：检测工人是否玩手机，
...
"trigger_logic": {
    "edges": [
    ],
    "nodes": [
        {
          "data": {
            "label": "工人正在玩手机",
            "logicType": ""
          },
          "id": "0",
          "type": "content"
        }
    ],
    ...
}
...

        """
        
        # 组合文本和 Base64 图片内容
        content = [
            {"type": "text", "text": prompt_text},
            *base64_parts, 
        ]
        
        # 3. 调用结构化输出链
        print(content)
        messages = [HumanMessage(content=content)]
        print(messages)
        result = await structured_chain.ainvoke(messages)
        print(result)
        
        return result

    except Exception as e:
        print(f"处理文件或 LLM 调用失败: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"处理请求时发生错误: {e}"
        )
    # finally:
    #     # TODO: 文件处理完成后，您可以选择删除文件，或者保留它们以供后续的视觉模型使用
    #     # ⚠️ 注意：如果后续视觉模型还需要文件，请勿删除。
    #     # for path in uploaded_paths:
    #     #     if os.path.exists(path):
    #     #         os.remove(path)
    #     pass
    
        
# --- 4. 运行服务 ---
if __name__ == "__main__":
    # 在生产环境中，请使用 gunicorn 或其他生产级 ASGI 服务器
    uvicorn.run(app, host="0.0.0.0", port=8000)