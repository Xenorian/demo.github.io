<template>
  <div class="flow-node-card content-node" :class="data.className">
    <Handle type="target" :position="Position.Left" />
    
    <div class="flow-node-header">
      <span class="icon">📄</span> 条件描述
      <div class="flow-node-delete" @click.stop="data.deleteNode(id)">×</div>
    </div>

    <div class="flow-node-body nodrag">
      <textarea 
        class="content-textarea"
        v-model="data.label" 
        placeholder="请输入详细条件..." 
        rows="3"
        @mousedown.stop 
      ></textarea>
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

/* 1. 尺寸与基础边框色 (灰色/标准系) */
.content-node {
  width: 220px;       /* 保持原有的宽度 */
  border-color: #dcdfe6;
}

.content-node.is-hovered,
.content-node:hover {
  border-color: #409eff; /* 悬停变蓝 */
  /* 阴影效果已由 flow-node-card 自动处理 */
}

/* 2. 头部配色 (素雅灰) */
.flow-node-header {
  background: #f5f7fa;
  color: #606266;
  border-bottom-color: #ebeef5;
}

/* 3. 内部元素样式 (Textarea) */
.content-textarea {
  width: 100%;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 8px;
  font-size: 12px;
  color: #303133;
  line-height: 1.5;
  outline: none;
  background-color: #fff;
  resize: vertical; 
  min-height: 60px;
  font-family: inherit;
  transition: border-color 0.2s, background-color 0.2s;
  display: block;
}

.content-textarea:focus {
  border-color: #409eff;
  background-color: #f9fcff;
}

.content-textarea::placeholder {
  color: #c0c4cc;
}
</style>