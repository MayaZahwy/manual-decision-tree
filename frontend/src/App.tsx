import { useEffect, useState } from "react";
import { checkHealth, fetchTree } from "./api/client";
import Dashboard from "./components/Dashboard";
import TreeVisualizer from "./components/TreeVisualizer";
import type { TreeNode } from "./types/tree";

function App() {
  const [tree, setTree] = useState<TreeNode | null>(null);
  const [trainMeta, setTrainMeta] = useState<{ rows: number; message: string } | null>(null);
  const [backendStatus, setBackendStatus] = useState<"checking" | "online" | "offline">("checking");

  useEffect(() => {
    let cancelled = false;

    async function bootstrap() {
      try {
        await checkHealth();
        if (cancelled) return;
        setBackendStatus("online");

        try {
          const existingTree = await fetchTree();
          if (!cancelled) {
            setTree(existingTree);
            setTrainMeta({ rows: existingTree.samples, message: "Model loaded from backend." });
          }
        } catch {
          // No trained model yet ÔÇö Dashboard will train on first load.
        }
      } catch {
        if (!cancelled) setBackendStatus("offline");
      }
    }

    void bootstrap();
    return () => {
      cancelled = true;
    };
  }, []);

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
        <div className="header-side">
          <span className={`backend-status backend-status-${backendStatus}`}>
            Backend: {backendStatus === "checking" ? "connectingÔÇª" : backendStatus}
          </span>
          {trainMeta && (
            <div className="header-meta">
              <span>{trainMeta.message}</span>
              <span>{trainMeta.rows} training rows</span>
            </div>
          )}
        </div>
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
