<template>
  <div class="layout-container">
    <div class="sidebar">
      <h3>逻辑树设计器</h3>
      <p>点击下方按钮开始。</p>
      <button @click="addRootTodo">新建根节点 (TODO)</button>
      <div class="tips">
        提示：
        <ul>
          <li>画布可拖拽，节点<b>不可拖拽</b></li>
          <li>TODO节点需选择类型</li>
          <li>逻辑节点自动生成子TODO</li>
          <li>悬停节点右上角可删除</li>
        </ul>
      </div>
    </div>

    <div class="right-content">
      <div class="flow-container" ref="flowWrapper">
        <VueFlow v-model:nodes="nodes" v-model:edges="edges" :node-types="nodeTypes" :nodes-draggable="false"
          :default-viewport="{ zoom: 1 }" :zoom-on-double-click="false" fit-view-on-init @pane-ready="onPaneReady">
          <Background pattern-color="#aaa" :gap="16" />
          <!-- <Controls /> -->
        </VueFlow>
      </div>

      <DisplayLogic class="logic-container" :nodes="nodes" :edges="edges" @node-hover="onSidebarHover" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, markRaw, nextTick } from 'vue';
import { VueFlow, useVueFlow, type Node, type Edge, type VueFlowStore, Position } from '@vue-flow/core';
import { Background } from '@vue-flow/background';
import { Controls } from '@vue-flow/controls';
import { nanoid } from 'nanoid';
import dagre from 'dagre';

// 导入自定义节点
import LogicNode from './LogicNode.vue';
import ContentNode from './ContentNode.vue';
import TodoNode from './TodoNode.vue'; // 新增
import DisplayLogic from './DisplayLogic.vue';

import '@vue-flow/core/dist/style.css';

// 注册节点
const nodeTypes = {
  logic: markRaw(LogicNode),
  content: markRaw(ContentNode),
  todo: markRaw(TodoNode),
};

const nodes = ref<Node[]>([]);
const edges = ref<Edge[]>([]);

const { findNode, getEdges, removeNodes } = useVueFlow();
let vueFlowInstance: VueFlowStore | null = null;
const flowWrapper = ref<HTMLElement | null>(null);

const onPaneReady = (instance: VueFlowStore) => {
  vueFlowInstance = instance;
  instance.fitView({ duration: 300, padding: 0.5, maxZoom: 1.5 });
};

// --- 逻辑表达式hover对flow node高亮
const currentHoverNodeId = ref<string | null>(null);
const HOVER_CLASS = 'is-hovered';

const onSidebarHover = (nodeId: string, isHovering: boolean) => {
  if (!nodes.value) return;

  currentHoverNodeId.value = isHovering ? nodeId : null;
  // console.log(isHovering ? 'Highlight Node:' : 'Restore Node:', nodeId);

  nodes.value = nodes.value.map(n => {
    if (n.id === nodeId) {
      // 1. 读取：依然从 n.data.className 读取 (正确)
      const currentClass = n.data.className || '';
      let newClass = currentClass;

      if (isHovering) {
        // 逻辑：添加 'is-hovered' class
        if (!currentClass.includes(HOVER_CLASS)) {
          newClass = `${currentClass} ${HOVER_CLASS}`.trim();
        }
      } else {
        // 逻辑：移除 'is-hovered' class
        newClass = currentClass.replace(new RegExp(`\\s*${HOVER_CLASS}`), '').trim();
      }

      return {
        ...n,
        // 2. 关键修改：更新整个 data 对象，并在其中设置 className
        data: {
          ...n.data, // 保留 data 中所有其他属性
          className: newClass, // 仅更新 data 中的 className
        },
        // 移除原有的: className: newClass,
      };
    }
    // 其他节点保持不变
    return n;
  });
};

// --- 核心辅助函数 ---

const getId = (prefix: string) => `${prefix}-${nanoid(6)}`;

// --- 自动布局辅助函数 ---

const getLayoutedElements = (
  _nodes: Node[],
  _edges: Edge[],
  direction = 'LR'
) => {
  // 1. 每次计算都必须新建 Graph 实例，防止状态污染
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));

  // 设置布局方向和间距
  const isHorizontal = direction === 'LR';
  dagreGraph.setGraph({
    rankdir: direction,
    ranksep: 80,  // 层级之间的距离 (横向则是列距)
    nodesep: 40,  // 同层节点之间的距离
  });

  // 2. 将节点添加到 dagre
  _nodes.forEach((node) => {
    // 关键点：如果节点已经渲染过，Vue Flow 会有 dimensions 属性
    // 如果是新节点，dimensions 可能为空，需要给一个基于 CSS 的预估值
    // 这里根据 node.type 给定不同的预估宽高，防止重叠
    // console.log(node, node.dimensions)
    const width = node.dimensions?.width || 250;
    const height = node.dimensions?.height || 150;

    dagreGraph.setNode(node.id, { width, height });
  });

  // 3. 将边添加到 dagre
  _edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  // 4. 执行计算
  dagre.layout(dagreGraph);

  // 5. 将计算出的坐标回填给节点
  return _nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);

    // 容错处理：万一 dagre 没算出位置（极少情况）
    if (!nodeWithPosition) return node;

    return {
      ...node,
      // 显式设置锚点位置，保证连线美观 (左进右出)
      targetPosition: isHorizontal ? Position.Left : Position.Top,
      sourcePosition: isHorizontal ? Position.Right : Position.Bottom,
      // Dagre 返回的是中心点，Vue Flow 需要左上角坐标
      position: {
        x: nodeWithPosition.x - nodeWithPosition.width / 2,
        y: nodeWithPosition.y - nodeWithPosition.height / 2,
      },
    };
  });
};

const layoutGraph = async (fit = false) => {
  // 停止现有动画（如果有）
  // 重新计算位置
  const layoutedNodes = getLayoutedElements(nodes.value, edges.value);

  // 更新节点
  nodes.value = [...layoutedNodes];

  // 如果需要适应视图
  if (fit) {
    await nextTick();
    vueFlowInstance?.fitView({ duration: 300, padding: 0.5, maxZoom: 1.5 });
  }
};


// 通用创建节点函数 (节点不可拖拽)
const createNode = (
  type: 'logic' | 'content' | 'todo',
  position: { x: number; y: number },
  data = {}
): Node => {
  return {
    id: getId(type),
    type,
    position,
    draggable: false, // 禁止拖拽
    data: {
      className: '',
      logicType: 'AND',
      label: '',
      ...data,
      // 传递函数引用
      changeType: handleChangeType,  // 用于 TodoNode
      addChild: handleAddChild,      // 用于 LogicNode
      deleteNode: handleDeleteNode   // 用于所有节点
    },
  };
};

const createEdge = (sourceId: string, targetId: string): Edge => {
  return {
    id: getId('edge'),
    source: sourceId,
    target: targetId,
    type: '', // 横向布局用贝塞尔曲线更美观
    style: { stroke: '#555', strokeWidth: 2 },
  };
};

// --- 业务逻辑 ---

/**
 * 3.2 添加根 TODO 节点
 */
const addRootTodo = () => {
  console.log('addRootTodo')
  // 清空现有画布（如果需要单根模式）
  nodes.value = [];
  edges.value = [];

  let centerPos = { x: 0, y: 0 }; // 不需要指定位置，任意给一个初始值或 (0, 0)

  // 创建根节点
  const rootNode = createNode('todo', centerPos);
  nodes.value.push(rootNode);

  layoutGraph(true)
};

/**
 * 3.3 处理类型选择 (TODO -> Logic/Content)
 */
function handleChangeType({ id, type }: { id: string, type: 'logic' | 'content' }) {
  console.log('handleChangeType')
  const node = findNode(id);
  if (!node) return;

  // 1. 修改当前节点类型
  node.type = type;

  // 2. 如果转为逻辑节点，自动添加2个 TODO 子项
  if (type === 'logic') {
    // 强制更新一下 data，确保视图刷新
    node.data = { ...node.data, logicType: 'AND' };

    // 添加两个子节点
    // 布局算法：父节点右侧，Y轴上下分散
    const child1Pos = { x: 0, y: 0 };
    const child2Pos = { x: 0, y: 0 };

    const child1 = createNode('todo', child1Pos);
    const child2 = createNode('todo', child2Pos);

    const edge1 = createEdge(node.id, child1.id);
    const edge2 = createEdge(node.id, child2.id);

    nodes.value.push(child1, child2);
    edges.value.push(edge1, edge2);
  } else {
    // 如果转为内容节点，初始化label
    node.data = { ...node.data, label: '' };
  }

  // 🆕 调用布局，更新所有节点位置
  layoutGraph(true)
}

/**
 * 手动添加子节点 (点击逻辑节点的 + 号)
 * 布局：横向排列
 */
function handleAddChild(parentNodeId: string) {
  console.log('handleAddChild')
  const parentNode = findNode(parentNodeId);
  if (!parentNode) return;

  const currentChildrenEdges = getEdges.value.filter(e => e.source === parentNodeId);
  const childrenCount = currentChildrenEdges.length;

  const newPosition = {
    x: 0,
    y: 0
  };

  const newNode = createNode('todo', newPosition); // 新增子项默认为 TODO
  const newEdge = createEdge(parentNodeId, newNode.id);

  nodes.value.push(newNode);
  edges.value.push(newEdge);

  layoutGraph(true)
}

/**
 * 4. 删除节点 (递归删除子树)
 */
function handleDeleteNode(nodeId: string) {
  console.log('handleDeleteNode')
  const nodesToDelete = new Set<string>();
  const edgesToDelete = new Set<string>();

  // 递归查找所有后代
  const findDescendants = (parentId: string) => {
    nodesToDelete.add(parentId);

    // 找到所有从 parentId 出发的边
    const connectedEdges = getEdges.value.filter(e => e.source === parentId);

    connectedEdges.forEach(edge => {
      edgesToDelete.add(edge.id);
      // 递归处理目标节点
      findDescendants(edge.target);
    });
  };

  findDescendants(nodeId);

  // 还要删除连接到该节点（作为target）的父级边
  const parentEdges = getEdges.value.filter(e => e.target === nodeId);
  parentEdges.forEach(e => edgesToDelete.add(e.id));

  // 执行删除
  // 使用 filter 重新赋值数组来实现删除，或者用 removeNodes
  nodes.value = nodes.value.filter(n => !nodesToDelete.has(n.id));
  edges.value = edges.value.filter(e => !edgesToDelete.has(e.id));

  layoutGraph(true)
}

</script>

<style>
/* 样式保持不变，略微调整布局 */
html,
body,
#app {
  height: 100%;
  margin: 0;
  overflow-x: hidden;
  overflow-y: hidden; /* 确保不会出现水平滚动条 */
}

.layout-container {
  display: flex;
  height: 100%;
  width: 100%;
}

.sidebar {
  width: 250px;
  background: #f0f2f5;
  padding: 20px;
  display: flex;
  flex-direction: column;
  z-index: 10;
  border-right: 1px solid var(--el-border-color-lighter);
}

.sidebar button {
  padding: 10px 15px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  margin-bottom: 10px;
}

.sidebar button:hover {
  background-color: #66b1ff;
}

.tips {
  margin-top: auto;
  font-size: 12px;
  color: #909399;
}

.tips ul {
  padding-left: 20px;
}

.right-content {
    flex-grow: 1; /* 占据所有剩余宽度 */
    display: flex; /* 再次启用 Flexbox */
    flex-direction: column; /* **关键：将主轴方向改为垂直 (从上到下)** */
}

.flow-container {
  display: flex;
  flex-grow: 1;
  height: 80%;
  background: #fff;
}

.logic-container {
  /* 您的原有样式略作修改 */
  width: 100%; /* 宽度占满父容器 */
  height: 15%;
  background-color: var(--el-bg-color);
  display: flex; 
}
</style>