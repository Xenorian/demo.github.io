// useExpressionGenerator.ts
import { computed } from 'vue';

// 定义 Token 结构，用于渲染
export interface ExprToken {
  type: 'logic' | 'content' | 'todo';
  value: string;
  nodeId?: string; // 只有 type 为 node 时才有
}

export function useExpressionGenerator(nodes: any, edges: any) {
  // 辅助：构建邻接表，方便查找子节点
  const adjacencyList = computed(() => {
    const map = new Map<string, string[]>();
    edges.value.forEach((edge: any) => {
      if (!map.has(edge.source)) map.set(edge.source, []);
      map.get(edge.source)?.push(edge.target);
    });
    return map;
  });

  // 辅助：查找节点对象
  const getNode = (id: string) => nodes.value.find((n: any) => n.id === id);

  // 核心递归函数
  const generateTokens = (nodeId: string): ExprToken[] => {
    const node = getNode(nodeId);
    if (!node) return [];

    // 情况 A: 叶子节点 (Content 或 Todo)
    if (node.type === 'content') {
      return [{ 
        type: 'content', 
        value: node.data?.label || '未输入规则', // 根据你实际数据结构调整
        nodeId: node.id 
      }];
    }else if(node.type === 'todo'){
      return [{ 
        type: 'todo', 
        value: '未选择类型', // 根据你实际数据结构调整
        nodeId: node.id 
      }];
    }else if (node.type === 'logic') {
      const childrenIds = adjacencyList.value.get(node.id) || [];
      
      if (childrenIds.length === 0) return []; // 逻辑节点没有子节点，忽略

      // 假设 logic 节点的数据里存了是 AND 还是 OR
      // 请根据你实际的业务字段调整这里，例如 node.data.operator
      const operatorText = node.data.logicType; 
      
      const result: ExprToken[] = [];
      
      result.push({ type: 'logic', value: '(' , nodeId: node.id}); // 左括号

      childrenIds.forEach((childId, index) => {
        const childTokens = generateTokens(childId);
        result.push(...childTokens);
        
        // 如果不是最后一个子节点，添加操作符
        if (index < childrenIds.length - 1) {
          result.push({ type: 'logic', value: operatorText , nodeId: node.id});
        }
      });

      result.push({ type: 'logic', value: ')' , nodeId: node.id }); // 右括号
      return result;
    }

    return [];
  };

  // 计算属性：生成最终的表达式数组
  const expressionList = computed(() => {
    // 1. 找到所有根节点 (没有作为 target 出现过的节点)
    const safeNodes = nodes.value ?? [];
    const safeEdges = edges.value ?? [];

    // console.log(safeNodes,safeEdges)
    // console.log('nodes',JSON.stringify(safeNodes))
    // console.log('edges',JSON.stringify(safeEdges))

    const targetIds = new Set(safeEdges.map((e: any) => e.target));
    const rootNodes = safeNodes.filter((n: any) => !targetIds.has(n.id));

    // 2. 为每个根节点生成表达式树
    return rootNodes.map((root: any) => {
        return {
            rootId: root.id,
            tokens: generateTokens(root.id)
        };
    });
  });

  return { expressionList };
}