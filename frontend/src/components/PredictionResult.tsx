import { severityClass, formatTargetLabel } from "../types/tree";

interface PredictionResultProps {
  prediction: string | null;
  path: string[];
}

export default function PredictionResult({ prediction, path }: PredictionResultProps) {
  if (!prediction) {
    return (
      <section className="prediction-result empty">
        <h2>Prediction</h2>
        <p>Submit the form to see the predicted burnout level and decision path.</p>
      </section>
    );
  }

  return (
    <section className="prediction-result">
      <h2>Prediction</h2>
      <p className={`prediction-badge ${severityClass(prediction)}`}>
        {formatTargetLabel(prediction)}
      </p>

      <h3>Decision path</h3>
      <ol className="decision-path">
        {path.map((step, index) => (
          <li key={`${step}-${index}`}>{step}</li>
        ))}
      </ol>
    </section>
  );
}
