export type ReviewDecision = "approve" | "reject" | "escalate";
export type Confidence = "low" | "medium" | "high";

export type EvidenceItem = {
  source: string;
  detail: string;
};

export type AgentResponse = {
  answer: string;
  confidence: Confidence;
  decision: ReviewDecision;
  evidence: EvidenceItem[];
  exceptions: string[];
  requires_human_review: boolean;
  next_actions: string[];
};

export type ChatRequest = {
  message: string;
  company_id: string;
  transaction_id?: string | null;
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

export async function sendChat(request: ChatRequest): Promise<AgentResponse> {
  const response = await fetch(`${API_BASE_URL}/agent/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(request)
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed with ${response.status}`);
  }

  return response.json() as Promise<AgentResponse>;
}
