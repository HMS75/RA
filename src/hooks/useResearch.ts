"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { API_URL, getHealth, getReview, startResearch } from "@/lib/api";
import type { ResearchResult, TimedStep } from "@/lib/types";

export type Status = "idle" | "running" | "done" | "error" | "stopped";

/** All the state for one research run: status, live steps, final result, error. */
export function useResearch() {
  const [status, setStatus] = useState<Status>("idle");
  const [steps, setSteps] = useState<TimedStep[]>([]);
  const [result, setResult] = useState<ResearchResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const stopRef = useRef<(() => void) | null>(null);

  const stop = useCallback(() => {
    stopRef.current?.();
    stopRef.current = null;
  }, []);

  const start = useCallback(
    async (topic: string, expand: boolean) => {
      stop();
      setSteps([]);
      setResult(null);
      setError(null);
      setStatus("running");
      const startedAt = Date.now();

      // Check first, so we can show a clear message (EventSource can't read HTTP error codes)
      try {
        const health = await getHealth();
        if (health.busy) {
          setError("The agent is busy with another run. Try again in a few minutes.");
          setStatus("error");
          return;
        }
      } catch {
        setError(`Can't reach the backend at ${API_URL}. Is uvicorn running?`);
        setStatus("error");
        return;
      }

      stopRef.current = startResearch(topic, expand, {
        onStep: (s) =>
          setSteps((prev) => [...prev, { ...s, t: Math.round((Date.now() - startedAt) / 1000) }]),
        onResult: (r) => setResult(r),
        onError: (message) => {
          setError(message);
          setStatus("error");
        },
        onEnd: () => setStatus((prev) => (prev === "error" ? prev : "done")),
      });
    },
    [stop],
  );

  const cancel = useCallback(() => {
    stop();
    setStatus("stopped");
  }, [stop]);

  /** Open a review that was saved earlier (no agent run needed). */
  const loadReview = useCallback(
    async (slug: string) => {
      stop();
      setSteps([]);
      setError(null);
      try {
        setResult(await getReview(slug));
        setStatus("done");
      } catch {
        setError("Could not load that review.");
        setStatus("error");
      }
    },
    [stop],
  );

  useEffect(() => stop, [stop]); // stop listening if the page is closed

  return { status, steps, result, error, start, cancel, loadReview };
}
