<template>
  <div class="flow-node-card logic-node" :class="data.className">
    <Handle type="target" :position="Position.Left" />
    
    <div class="flow-node-header">
      <span class="icon">🔀</span> 逻辑关系
      <div class="flow-node-delete" @click.stop="data.deleteNode(id)">×</div>
    </div>

    <div class="flow-node-body nodrag">
       <el-select 
       v-model="data.logicType"
       class="logic-select"
       ref="logicSelectRef">
         <el-option value="AND">且 (AND)</el-option>
         <el-option value="OR">或 (OR)</el-option>
       </el-select>

      <button class="add-btn flow-node-btn" @click="data.addChild(id)">
        <span class="plus">+</span> 添加分支
      </button>
    </div>
    
    <Handle type="source" :position="Position.Right" />
  </div>
</template>

<script setup lang="ts">
import { Handle, Position, useVueFlow } from '@vue-flow/core';
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
defineProps(['id', 'data']);


const logicSelectRef = ref(null); // 1. 定义 ref
const { onMove, onPaneReady } = useVueFlow(); // 2. 引入 useVueFlow

let isDropdownOpen = false;

// 监听 el-select 自身的打开/关闭状态
function handleVisibleChange(visible: boolean) {
  isDropdownOpen = visible;
}

// 3. 核心逻辑：监听画布移动
// onMove 在画布平移或缩放时触发
onMove(() => {
  (logicSelectRef.value as any).blur(); 

});
</script>

<style scoped>
/* 引入公共样式 */
@import url('@/flow-node-base.css');

/* === 组件特定样式 (Theme) === */

/* 1. 尺寸与基础边框色 */
.logic-node {
  width: 200px;
  border-color: #dcdfe6;
}
.logic-node.is-hovered,
.logic-node:hover {
  border-color: #409eff; /* 悬停变为蓝色 */
}

/* 2. 头部配色 (绿色系) */
.flow-node-header {
  background: #cbe6ff;
  color: #409eff;
  border-bottom-color: #e1f3d8;
}

/* 3. 组件内部特定元素的样式 */
.logic-select {
  width: 100%;
  /* border: 1px solid #e4e7ed;
  border-radius: 4px; */
  /* padding: 6px 8px; */
  font-size: 12px;
  color: #606266;
  outline: none;
  background-color: #fff;
  transition: border-color 0.2s;
}
.logic-select:focus {
  border-color: #409eff;
  background-color: #f9fcff;
}

.add-btn {
  width: 100%;
  background: #ecf5ff;
  color: #409eff;
  border: 1px dashed #409eff;
  border-radius: 4px;
  padding: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: background 0.2s;
}
.add-btn:hover {
  background: #409eff;
  color: white;
  border-style: solid;
}
</style>