<template>
  <div class="todo-node">
    <Handle type="target" :position="Position.Left" />
    
    <div class="title">请选择节点类型</div>
    <div class="actions nodrag">
      <button class="btn-logic" @click="data.changeType({ id, type: 'logic' })">
        逻辑节点 (分叉)
      </button>
      <button class="btn-content" @click="data.changeType({ id, type: 'content' })">
        内容节点 (终点)
      </button>
    </div>
    <div class="delete-handle" @click.stop="data.deleteNode(id)">×</div>
  </div>
</template>

<script setup lang="ts">
import { Handle, Position } from '@vue-flow/core';

defineProps(['id', 'data']);
defineEmits(['change-type', 'delete-node']);
</script>

<style scoped>
.todo-node {
  padding: 15px;
  border-radius: 8px;
  background: #fff;
  border: 2px dashed #ff9800; /* 虚线表示待定 */
  min-width: 180px;
  text-align: center;
  position: relative;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}

.title {
  font-size: 12px;
  color: #666;
  margin-bottom: 10px;
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

button {
  border: none;
  padding: 6px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: opacity 0.2s;
}
button:hover { opacity: 0.8; }

.btn-logic { background: #e3f2fd; color: #1565c0; }
.btn-content { background: #f5f5f5; color: #333; }

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
  display: none; /* 悬停显示 */
}
.todo-node:hover .delete-handle { display: block; }
</style>