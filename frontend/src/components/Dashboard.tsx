import { useCallback, useEffect, useState } from "react";
import { predict, trainModel } from "../api/client";
import type { BurnoutFormValues, TreeNode } from "../types/tree";
import { DEFAULT_FORM_VALUES } from "../types/tree";
import BurnoutForm from "./BurnoutForm";
import PredictionResult from "./PredictionResult";

interface DashboardProps {
  tree: TreeNode | null;
  onTreeUpdated: (tree: TreeNode, meta: { rows: number; message: string }) => void;
}

export default function Dashboard({ tree, onTreeUpdated }: DashboardProps) {
  const [formValues, setFormValues] = useState<BurnoutFormValues>(DEFAULT_FORM_VALUES);
  const [prediction, setPrediction] = useState<string | null>(null);
  const [path, setPath] = useState<string[]>([]);
  const [predictLoading, setPredictLoading] = useState(false);
  const [trainLoading, setTrainLoading] = useState(false);
  const [trainFile, setTrainFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [trainInfo, setTrainInfo] = useState<string | null>(null);

  const isTrained = tree !== null;

  const handleTrain = useCallback(async () => {
    setTrainLoading(true);
    setError(null);
    try {
      const result = await trainModel(trainFile);
      onTreeUpdated(result.tree, { rows: result.rows, message: result.message });
      setTrainInfo(`${result.message} (${result.rows} rows)`);
      setPrediction(null);
      setPath([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Training failed.");
    } finally {
      setTrainLoading(false);
    }
  }, [onTreeUpdated, trainFile]);

  useEffect(() => {
    if (!isTrained) {
      void handleTrain();
    }
  }, [handleTrain, isTrained]);

  const handlePredict = async () => {
    setPredictLoading(true);
    setError(null);
    try {
      const result = await predict({
        Sleep: formValues.sleep,
        Meetings: formValues.meetings,
        Weekends: formValues.weekends,
        Stress: formValues.stress,
      });
      setPrediction(result.prediction);
      setPath(result.path);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Prediction failed.");
    } finally {
      setPredictLoading(false);
    }
  };

  return (
    <div className="dashboard-grid">
      <section className="panel training-panel">
        <h2>Train Model</h2>
        <p className="panel-description">
          Upload your CSV dataset, use the sample file at{" "}
          <code>backend/data/sample_burnout.csv</code>, or train with the built-in fallback data.
        </p>
        <div className="form-field">
          <label htmlFor="train-csv">Training CSV file</label>
          <input
            id="train-csv"
            type="file"
            accept=".csv,text/csv"
            onChange={(event) => setTrainFile(event.target.files?.[0] ?? null)}
          />
        </div>
        <button
          type="button"
          className="secondary-button"
          onClick={() => void handleTrain()}
          disabled={trainLoading}
        >
          {trainLoading ? "TrainingÔÇª" : "Train Model"}
        </button>
        {trainInfo && <p className="info-text">{trainInfo}</p>}
      </section>

      <section className="panel form-panel">
        <h2>Developer Profile</h2>
        <BurnoutForm
          values={formValues}
          onChange={setFormValues}
          onSubmit={() => void handlePredict()}
          loading={predictLoading}
          disabled={!isTrained}
        />
      </section>

      <section className="panel result-panel">
        <PredictionResult prediction={prediction} path={path} />
      </section>

      {error && (
        <div className="error-banner" role="alert">
          {error}
        </div>
      )}
    </div>
  );
}
