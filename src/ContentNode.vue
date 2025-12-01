<template>
  <div class="content-node">
    <Handle type="target" :position="Position.Left" />
    
    <div class="node-header">条件描述</div>
    <div class="node-content nodrag">
      <textarea v-model="data.label" placeholder="输入条件..." rows="3"></textarea>
    </div>
    
    <div class="delete-handle" @click.stop="data.deleteNode(id)">×</div>
    </div>
</template>

<script setup lang="ts">
import { Handle, Position } from '@vue-flow/core'; // 修复 TS 错误
defineProps(['id', 'data']);
defineEmits(['delete-node']);
</script>

<style scoped>
/* 保持原有样式，增加定位和删除按钮 */
.content-node {
  padding: 10px;
  border-radius: 8px;
  background: #f5f5f5;
  border: 2px solid #9e9e9e;
  min-width: 180px;
  position: relative;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}
.node-header { font-size: 12px; color: #666; margin-bottom: 5px; }
.node-content textarea { width: 100%; resize: vertical; padding: 5px; border-radius: 4px; border: 1px solid #ccc; font-family: inherit; }

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
.content-node:hover .delete-handle { display: block; }
</style>