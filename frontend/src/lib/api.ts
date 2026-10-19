import type { AgentStep, Health, Overview, ResearchResult } from "./types";

export const API_URL =  process.env.NEXT_PUBLIC_API_URL ?? (process.env.NODE_ENV === "development" ? "http://localhost:8000" : "");


async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`);
  if (!res.ok) throw new Error(`${path} failed with status ${res.status}`);
  return res.json() as Promise<T>;
}

export const getHealth = () => getJson<Health>("/api/health");
export const getOverview = () => getJson<Overview>("/api/overview");

export type ResearchHandlers = {
  onStep: (step: AgentStep) => void;
  onResult: (result: ResearchResult) => void;
  onError: (message: string) => void;
  onEnd: () => void;
};

/**
 * Starts a research run and listens to the live stream (Server-Sent Events).
 * Returns a function that stops listening.
 *
 * Important: if the connection drops, the browser's EventSource silently reconnects,
 * and that would START A SECOND AGENT RUN. So we always close it ourselves.
 */
export function startResearch(topic: string, expand: boolean, handlers: ResearchHandlers): () => void {
  const url = `${API_URL}/api/research/stream?topic=${encodeURIComponent(topic)}&expand=${expand}`;
  const source = new EventSource(url);
  let finished = false;

  const close = () => {
    finished = true;
    source.close();
  };

  source.addEventListener("step", (e) => handlers.onStep(JSON.parse((e as MessageEvent).data)));
  source.addEventListener("result", (e) => handlers.onResult(JSON.parse((e as MessageEvent).data)));
  source.addEventListener("end", () => {
    if (finished) return;
    close();
    handlers.onEnd();
  });

  // "error" fires for TWO different reasons:
  //  1) our server sent an "error" event (has data), 2) the connection itself failed (no data)
  source.addEventListener("error", (e) => {
    if (finished) return;
    const data = (e as MessageEvent).data;
    close();
    if (data) {
      handlers.onError(JSON.parse(data).message ?? "The agent failed.");
    } else {
      handlers.onError("Lost the connection to the backend. Check that it is still running.");
    }
  });

  return close;
}
