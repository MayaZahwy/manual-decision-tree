import { useState } from "react";
import Dashboard from "./components/Dashboard";
import TreeVisualizer from "./components/TreeVisualizer";
import type { TreeNode } from "./types/tree";

function App() {
  const [tree, setTree] = useState<TreeNode | null>(null);
  const [trainMeta, setTrainMeta] = useState<{ rows: number; message: string } | null>(null);

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">Home Assignment ┬À Manual CART Decision Tree</p>
          <h1>Developer Burnout Analysis</h1>
          <p className="subtitle">
            Predict burnout levels and explore the decision path through an interactive tree.
          </p>
        </div>
        {trainMeta && (
          <div className="header-meta">
            <span>{trainMeta.message}</span>
            <span>{trainMeta.rows} training rows</span>
          </div>
        )}
      </header>

      <Dashboard
        tree={tree}
        onTreeUpdated={(nextTree, meta) => {
          setTree(nextTree);
          setTrainMeta(meta);
        }}
      />

      <TreeVisualizer tree={tree} />
    </div>
  );
}

export default App;
