export type WeekendsValue = "YES" | "NO";

export interface TreeNode {
  type: "internal" | "leaf";
  samples: number;
  class_distribution: Record<string, number>;
  predicted_class: string;
  gini: number;
  feature?: string;
  operator?: string;
  threshold?: number | null;
  category_value?: string | null;
  left?: TreeNode;
  right?: TreeNode;
}

export interface PredictRequest {
  Sleep: number;
  Meetings: number;
  Weekends: WeekendsValue;
  Stress: number;
}

export interface PredictResponse {
  prediction: string;
  path: string[];
}

export interface TrainResponse {
  message: string;
  rows: number;
  features: string[];
  target_classes: string[];
  tree: TreeNode;
}

export interface BurnoutFormValues {
  sleep: number;
  meetings: number;
  weekends: WeekendsValue;
  stress: number;
}

export const DEFAULT_FORM_VALUES: BurnoutFormValues = {
  sleep: 7,
  meetings: 5,
  weekends: "NO",
  stress: 5,
};

export const SEVERITY_CLASSES: Record<string, string> = {
  healthy: "severity-healthy",
  "risk of burnout": "severity-risk",
  "vacation required": "severity-vacation",
  "critical condition": "severity-critical",
};

export function severityClass(label: string): string {
  return SEVERITY_CLASSES[label] ?? "severity-unknown";
}

/** Title-case display labels for burnout target classes. */
export const TARGET_LABELS: Record<string, string> = {
  healthy: "Healthy",
  "risk of burnout": "Risk of burnout",
  "vacation required": "Vacation required",
  "critical condition": "Critical condition",
};

export function formatTargetLabel(label: string): string {
  return TARGET_LABELS[label] ?? label;
}
