import { memo, useMemo } from "react";
import {
  Background,
  Controls,
  Handle,
  MiniMap,
  Position,
  ReactFlow,
  type Edge,
  type Node,
  type NodeProps,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import type { TreeNode } from "../types/tree";
import { formatTargetLabel, severityClass } from "../types/tree";

interface TreeVisualizerProps {
  tree: TreeNode | null;
}

interface TreeNodeData extends Record<string, unknown> {
  label: string;
  nodeType: "internal" | "leaf";
  samples: number;
  classDistribution: Record<string, number>;
  gini: number;
  predictedClass: string;
  severityClassName: string;
}

const HORIZONTAL_GAP = 220;
const VERTICAL_GAP = 140;

function formatSplit(node: TreeNode): string {
  if (node.type === "leaf") {
    return formatTargetLabel(node.predicted_class);
  }
  if (node.operator === "<=" && node.feature && node.threshold != null) {
    return `${node.feature} <= ${node.threshold}`;
  }
  if (node.operator === "==" && node.feature && node.category_value) {
    return `${node.feature} == ${node.category_value}`;
  }
  return node.feature ?? "split";
}

function distributionText(distribution: Record<string, number>): string {
  return Object.entries(distribution)
    .map(([label, count]) => `${formatTargetLabel(label)}: ${count}`)
    .join(", ");
}

function layoutTree(
  node: TreeNode,
  depth = 0,
  xOffset = 0,
): { nodes: Node<TreeNodeData>[]; edges: Edge[]; width: number } {
  const nodeId = `${node.feature ?? "leaf"}-${depth}-${xOffset}-${node.samples}-${node.predicted_class}`;

  if (node.type === "leaf" || !node.left || !node.right) {
    const flowNode: Node<TreeNodeData> = {
      id: nodeId,
      type: "treeNode",
      position: { x: xOffset, y: depth * VERTICAL_GAP },
      data: {
        label: formatSplit(node),
        nodeType: "leaf",
        samples: node.samples,
        classDistribution: node.class_distribution,
        gini: node.gini,
        predictedClass: node.predicted_class,
        severityClassName: severityClass(node.predicted_class),
      },
    };
    return { nodes: [flowNode], edges: [], width: 1 };
  }

  const leftLayout = layoutTree(node.left, depth + 1, xOffset);
  const rightLayout = layoutTree(
    node.right,
    depth + 1,
    xOffset + (leftLayout.width + 0.5) * HORIZONTAL_GAP,
  );

  const centerX =
    (leftLayout.nodes[0].position.x + rightLayout.nodes[0].position.x) / 2;

  const flowNode: Node<TreeNodeData> = {
    id: nodeId,
    type: "treeNode",
    position: { x: centerX, y: depth * VERTICAL_GAP },
    data: {
      label: formatSplit(node),
      nodeType: "internal",
      samples: node.samples,
      classDistribution: node.class_distribution,
      gini: node.gini,
      predictedClass: node.predicted_class,
      severityClassName: "severity-internal",
    },
  };

  const leftLabel = node.operator === "==" ? "yes" : "<=";
  const rightLabel = node.operator === "==" ? "no" : ">";

  const edges: Edge[] = [
    {
      id: `${nodeId}-left`,
      source: nodeId,
      target: leftLayout.nodes[0].id,
      label: leftLabel,
      type: "smoothstep",
    },
    {
      id: `${nodeId}-right`,
      source: nodeId,
      target: rightLayout.nodes[0].id,
      label: rightLabel,
      type: "smoothstep",
    },
    ...leftLayout.edges,
    ...rightLayout.edges,
  ];

  return {
    nodes: [flowNode, ...leftLayout.nodes, ...rightLayout.nodes],
    edges,
    width: leftLayout.width + rightLayout.width,
  };
}

function TreeFlowNode({ data }: NodeProps<Node<TreeNodeData>>) {
  const isLeaf = data.nodeType === "leaf";

  return (
    <div className={`tree-node ${isLeaf ? data.severityClassName : "tree-node-internal"}`}>
      <Handle type="target" position={Position.Top} />
      <div className="tree-node-label">{data.label}</div>
      <div className="tree-node-meta">{isLeaf ? "Leaf" : "Split"} ┬À n={data.samples}</div>
      <div className="tree-node-tooltip">
        <strong>{isLeaf ? "Predicted class" : "Majority class"}:</strong>{" "}
        {formatTargetLabel(data.predictedClass)}
        <br />
        <strong>Samples:</strong> {data.samples}
        <br />
        <strong>Distribution:</strong> {distributionText(data.classDistribution)}
        <br />
        <strong>Gini:</strong> {data.gini.toFixed(4)}
      </div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

const nodeTypes = { treeNode: memo(TreeFlowNode) };

export default function TreeVisualizer({ tree }: TreeVisualizerProps) {
  const { nodes, edges } = useMemo((): { nodes: Node<TreeNodeData>[]; edges: Edge[] } => {
    if (!tree) {
      return { nodes: [], edges: [] };
    }
    return layoutTree(tree);
  }, [tree]);

  if (!tree) {
    return (
      <section className="panel tree-panel empty-tree">
        <h2>Decision Tree</h2>
        <p>Train the model to visualize the decision tree.</p>
      </section>
    );
  }

  return (
    <section className="panel tree-panel">
      <h2>Decision Tree</h2>
      <p className="panel-description">
        Hover a node to inspect sample count, class distribution, Gini impurity, and predicted class.
      </p>
      <div className="tree-flow-wrapper">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          fitView
          minZoom={0.2}
          maxZoom={1.5}
          nodesDraggable={false}
          nodesConnectable={false}
          elementsSelectable
        >
          <MiniMap pannable zoomable />
          <Controls />
          <Background gap={16} size={1} />
        </ReactFlow>
      </div>
    </section>
  );
}
