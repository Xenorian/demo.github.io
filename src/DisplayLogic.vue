<template>
  <div class="expression-sidebar">
    <div class="sidebar-header">
      <h3>逻辑预览</h3>
      <el-tag type="info" size="small">Expression</el-tag>
    </div>

    <el-scrollbar class="expression-block" always>
      <div v-if="expressionList.length === 0" class="expression-content">
        <el-empty description="暂无逻辑流" :image-size="60" />
      </div>

      <div v-else class="expression-content">

        <div v-for="(token, idx) in expressionList[0].tokens" :key="idx" :class="[
          'token',
          token.type,
          { 'is-hovered': currentHoverId === token.nodeId }
        ]" @mouseenter="handleMouseEnter(token)" @mouseleave="handleMouseLeave(token)">
          {{ token.value }}
        </div>

      </div>

    </el-scrollbar>
  </div>
</template>

<script setup lang="ts">
import { ref, toRef } from 'vue';
import { useExpressionGenerator } from './DisplayLogic.ts'; // 引入上面的逻辑
import type { ExprToken } from './DisplayLogic.ts';

// 接收父组件传来的数据
const props = defineProps<{
  nodes: any[];
  edges: any[];
}>();

const nodesRef = toRef(props, 'nodes');
const edgesRef = toRef(props, 'edges');

// 1. 生成逻辑表达式
const { expressionList } = useExpressionGenerator(nodesRef, edgesRef);
// console.log(expressionList)

// 2. 交互逻辑
const currentHoverId = ref<string | null>(null);

// 定义 Emits，通知父组件高亮画布中的节点
const emit = defineEmits(['node-hover']);

const handleMouseEnter = (token: ExprToken) => {
    // console.log(token)
    currentHoverId.value = token.nodeId;
    emit('node-hover', token.nodeId, true); // true = 开始 hover
};

const handleMouseLeave = (token: ExprToken) => {
    currentHoverId.value = null;
    emit('node-hover', token.nodeId, false); // false = 结束 hover
};
</script>

<style scoped lang="scss">
.expression-sidebar {
  border: 2px solid var(--el-border-color);
  border-left: 0px solid var(--el-border-color);
  background-color: var(--el-bg-color);
  display: flex;
  flex-direction: row;
  margin-top: auto;
  height: 20%;
}

.sidebar-header {
  padding: 16px;
  border-right: 1px solid var(--el-border-color-lighter);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;

  h3 {
    margin: 0 0 10px 0px;
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }
}

.expression-block {
  flex-grow: 1;
  height: 100%;
  border-bottom: 1px dashed var(--el-border-color-lighter);
  
  // **重点修改 1: 移除这里的 flex 居中，让 ElScrollbar 内部的容器负责**
  // display: flex;
  // flex-direction: row;
  // justify-content: center;
  // align-items: center;

  // 针对 El-Scrollbar 内部的 Viewport 进行居中处理
  :deep(.el-scrollbar__view) {
    // 确保内部的 Viewport 占据全部空间
    height: 100%; 
    // 将 Viewport 设置为 Flex 容器，用于居中其子元素 expression-content
    display: flex; 
    justify-content: center; // 水平居中
    align-items: center;     // 垂直居中
  }
}

.expression-content {
  // **重点修改 2: expression-content 自身不需要再次设置居中**
  // 它的父容器 (.el-scrollbar__view) 已经在做居中工作
  display: flex;
  flex-direction: row;
  // justify-content: center; // 移除
  // align-items: center;     // 移除
  white-space: nowrap;
  
  font-family: 'Microsoft YaHei', monospace;
  font-size: 14px;
  line-height: 1.8;
  color: var(--el-text-color-regular);
  word-break: break-word;
  padding: 0 10px; // 增加左右内边距，防止内容贴边
}

/* Token 样式保持不变 */
.token {
  color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
  padding: 2px 6px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;

  margin-right: 8px; /* 根据需要调整这个数值，比如 8px */

  // 如果想去掉最后一个 token 的右侧间距（推荐）：
  &:last-child {
      margin-right: 0;
  }

  &:hover,
  &.is-hovered {
    background: var(--el-color-primary);
    color: white;
    transform: translateY(-1px);
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  }

}
</style>