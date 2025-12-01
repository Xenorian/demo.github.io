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
    <div class="flow-container" ref="flowWrapper">
      <VueFlow
        v-model:nodes="nodes"
        v-model:edges="edges"
        :node-types="nodeTypes"
        :nodes-draggable="false" 
        :default-viewport="{ zoom: 1 }"
        fit-view-on-init
        @pane-ready="onPaneReady"
      >
        <Background pattern-color="#aaa" :gap="16" />
        <Controls />
      </VueFlow>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, markRaw } from 'vue';
import { VueFlow, useVueFlow, type Node, type Edge, type VueFlowStore, Position } from '@vue-flow/core';
import { Background } from '@vue-flow/background';
import { Controls } from '@vue-flow/controls';
import { nanoid } from 'nanoid';

// 导入自定义节点
import LogicNode from './LogicNode.vue';
import ContentNode from './ContentNode.vue';
import TodoNode from './TodoNode.vue'; // 新增

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
  instance.fitView();
};

// --- 核心辅助函数 ---

const getId = (prefix: string) => `${prefix}-${nanoid(6)}`;

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
    type: 'bezier', // 横向布局用贝塞尔曲线更美观
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

  let centerPos = { x: 100, y: 300 }; // 默认靠左居中
  
  // 创建根节点
  const rootNode = createNode('todo', centerPos);
  nodes.value.push(rootNode);

  setTimeout(() => vueFlowInstance?.fitView({ duration: 800 }), 50);
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
    const spacingX = 250;
    const spacingY = 100;
    
    const child1Pos = { x: node.position.x + spacingX, y: node.position.y - spacingY };
    const child2Pos = { x: node.position.x + spacingX, y: node.position.y + spacingY };
    
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

  const SPACING_X = 250; // 水平间距
  const SPACING_Y = 120; // 垂直间距
  
  // 简单算法：新节点放在最下方
  // 更好的算法是重新计算所有兄弟节点的Y坐标，这里用增量法简化
  // 为了不重叠，我们根据子节点数量，交替在上下方，或者直接往下堆叠
  // 这里采用：基准线是父节点Y，根据数量 * 间距 偏移
  
  // 计算所有现有子节点的Y范围，放到最下面
  let nextY = parentNode.position.y + SPACING_Y;
  if (childrenCount > 0) {
     // 找到当前子节点中最大的Y
     // 注意：这里需要遍历edge找到target node。
     // 为简化，直接按数量往下排，可能重叠，需要用户手动删或者更复杂的布局算法。
     // 优化方案：交替排列 (上 下 上 下)
     const sign = childrenCount % 2 === 0 ? -1 : 1;
     const multiplier = Math.ceil((childrenCount + 1) / 2);
     nextY = parentNode.position.y + (sign * multiplier * SPACING_Y);
  }

  const newPosition = {
    x: parentNode.position.x + SPACING_X,
    y: nextY
  };

  const newNode = createNode('todo', newPosition); // 新增子项默认为 TODO
  const newEdge = createEdge(parentNodeId, newNode.id);

  nodes.value.push(newNode);
  edges.value.push(newEdge);
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
}

</script>

<style>
/* 样式保持不变，略微调整布局 */
html, body, #app { height: 100%; margin: 0; }
.layout-container { display: flex; height: 100vh; width: 100vw; }
.sidebar { width: 250px; background: #f0f2f5; border-right: 1px solid #dcdfe6; padding: 20px; display: flex; flex-direction: column; z-index: 10; }
.sidebar button { padding: 10px 15px; background-color: #409eff; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; margin-bottom: 10px; }
.sidebar button:hover { background-color: #66b1ff; }
.tips { margin-top: auto; font-size: 12px; color: #909399; }
.tips ul { padding-left: 20px; }
.flow-container { flex-grow: 1; height: 100%; background:#fff; }
</style>