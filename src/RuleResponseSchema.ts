/**
 * NodeData: 逻辑节点或内容节点的负载数据
 */
interface NodeData {
    /**
     * logicType: 仅当 type 为 'logic' 时为 'AND' 或 'OR'，否则为 ''。
     */
    logicType: 'AND' | 'OR' | '';
    
    /**
     * label: 规则内容（content）。
     * 对于逻辑节点（logic），通常为空或作为调试标签。
     */
    label: string;
}

/**
 * Node: 逻辑图中的节点
 */
interface Node {
    /**
     * id: 节点的唯一编号。
     */
    id: string;
    
    /**
     * type: 节点类型：'logic' 用于 AND/OR, 'content' 用于规则内容。
     */
    type: 'logic' | 'content'; 
    
    /**
     * data: 节点数据负载。
     */
    data: NodeData;
}

/**
 * Edge: 逻辑图中的边
 */
interface Edge {
    /**
     * id: 边的唯一编号。
     */
    id: string;
    
    /**
     * source: 源节点 ID。
     */
    source: string;
    
    /**
     * target: 目标节点 ID。
     */
    target: string;
}

interface VisualDetection {
    /**
     * target_objects: 视觉模型需要聚焦的对象列表。必须是详细、准确、可区分的自然语言描述。
     */
    target_objects: string[];
}

interface TriggerLogic {
    /**
     * nodes: 逻辑图中的节点列表。
     */
    nodes: Node[];
    
    /**
     * edges: 逻辑图中的边列表。
     */
    edges: Edge[];
    
    /**
     * temporal_threshold_seconds: 持续多少秒则认为违反规则。
     * -1 表示时长信息在 required_attributes 中或规则中没有明确要求时长。
     * > 0 表示推荐的秒数阈值。
     */
    temporal_threshold_seconds: number;
}

export interface RuleOutputSchema {
    /**
     * visual_detection: 视觉检测部分。
     */
    visual_detection: VisualDetection;
    
    /**
     * trigger_logic: 规则触发逻辑图部分。
     */
    trigger_logic: TriggerLogic;
    
    /**
     * alert_message: 当规则被违反后，提示给用户或管理员的告警信息和建议。
     */
    alert_message: string;
}