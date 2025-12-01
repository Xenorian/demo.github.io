<template>
  <div class="logic-node">
    <Handle type="target" :position="Position.Left" />
    
    <div class="node-header">逻辑关系</div>
    <div class="node-content nodrag">
       <select v-model="data.logicType">
        <option value="AND">且 (AND)</option>
        <option value="OR">或 (OR)</option>
      </select>
    </div>

    <button class="add-btn nodrag" @click="data.addChild(id)">
      + 添加分支
    </button>
    
    <Handle type="source" :position="Position.Right" />

    <div class="delete-handle" @click.stop="data.deleteNode(id)">×</div>
  </div>
</template>

<script setup lang="ts">
import { Handle, Position } from '@vue-flow/core';

defineProps(['id', 'data']);
defineEmits(['add-child', 'delete-node']);
</script>

<style scoped>
/* 保持原有样式基础，增加 delete-handle */
.logic-node {
  padding: 10px;
  border-radius: 8px;
  background: #e3f2fd; 
  border: 2px solid #2196f3;
  min-width: 150px;
  text-align: center;
  position: relative;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}
.node-header { font-weight: bold; margin-bottom: 8px; font-size: 12px; color: #1565c0; }
.node-content select { width: 100%; padding: 4px; border-radius: 4px; border: 1px solid #ccc; }
.add-btn { margin-top: 10px; width: 100%; background: #2196f3; color: white; border: none; border-radius: 4px; padding: 4px; cursor: pointer; font-size: 12px; }
.add-btn:hover { background: #1976d2; }

.delete-handle {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 20px;
  height: 20px;
  background: #ff4d4f;
  color: white;
  border-radius: 50%;
  text-align: center;
  line-height: 18px;
  font-size: 14px;
  cursor: pointer;
  display: none;
}
.logic-node:hover .delete-handle { display: block; }
</style>