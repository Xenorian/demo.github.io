<template>
  <div class="flow-node-card todo-node" :class="data.className">
    <Handle type="target" :position="Position.Left" />
    
    <div class="flow-node-header">
      <span class="icon">✨</span> 请选择类型
      <div class="flow-node-delete" @click.stop="data.deleteNode(id)">×</div>
    </div>

    <div class="flow-node-body nodrag">
      <button 
        class="choice-btn logic flow-node-btn" 
        @click="data.changeType({ id, type: 'logic' })"
      >
        <span class="btn-icon">🔀</span> 逻辑分叉
      </button>
      
      <button 
        class="choice-btn content flow-node-btn" 
        @click="data.changeType({ id, type: 'content' })"
      >
        <span class="btn-icon">📄</span> 内容节点
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Handle, Position } from '@vue-flow/core';
defineProps(['id', 'data']);
</script>

<style scoped>
/* 引入公共样式 */
@import url('@/flow-node-base.css');

/* === 组件特定样式 (Theme) === */

/* 1. 尺寸与基础边框色 (橙色系) */
.todo-node {
  width: 180px;
  /* border-color: #e6a23c; */
  border-color: #ffd597;
}

.todo-node.is-hovered,
.todo-node:hover {
  /* 悬停时加深阴影颜色 */
  border-color: #ffa216;
}

/* 2. 头部配色 (橙色系) */
.flow-node-header {
  background: #fdf6ec;
  color: #e6a23c;
  border-bottom-color: #faecd8;
}

/* 3. 内部按钮样式 */
.choice-btn {
  width: 100%;
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s;
}

.choice-btn.logic {
  background: #ecf5ff;
  color: #409eff;
  border: 1px solid #d9ecff;
}
.choice-btn.logic:hover {
  background: #409eff;
  color: white;
}

.choice-btn.content {
  background: #f4f4f5;
  color: #909399;
  border: 1px solid #e9e9eb;
}
.choice-btn.content:hover {
  background: #909399;
  color: white;
}
</style>