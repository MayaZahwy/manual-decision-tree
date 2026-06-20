import type {
  PredictRequest,
  PredictResponse,
  TrainResponse,
  TreeNode,
} from "../types/tree";

const API_BASE = import.meta.env.VITE_API_URL ?? "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init);
  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = (await response.json()) as { detail?: string | { msg: string }[] };
      if (typeof body.detail === "string") {
        detail = body.detail;
      } else if (Array.isArray(body.detail) && body.detail[0]?.msg) {
        detail = body.detail[0].msg;
      }
    } catch {
      // keep default message
    }
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

export async function checkHealth(): Promise<{ status: string }> {
  return request("/health");
}

export async function trainModel(file?: File | null): Promise<TrainResponse> {
  const formData = new FormData();
  if (file) {
    formData.append("file", file);
  }

  return request<TrainResponse>("/train", {
    method: "POST",
    body: formData,
  });
}

export async function predict(payload: PredictRequest): Promise<PredictResponse> {
  return request<PredictResponse>("/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function fetchTree(): Promise<TreeNode> {
  return request<TreeNode>("/tree");
}
