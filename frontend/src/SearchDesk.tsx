import React, { useState } from "react";
import { SourceDialog } from "./SourceDialog";
export type Requester = (path: string, init?: RequestInit) => Promise<any>;
export function SearchDesk({
  request,
  denseAvailable,
}: {
  request: Requester;
  denseAvailable: boolean;
}) {
  const [question, setQuestion] = useState(""),
    [mode, setMode] = useState("lexical"),
    [hits, setHits] = useState<any[]>([]),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [searched, setSearched] = useState(false),
    [answer, setAnswer] = useState<any>(null),
    [action, setAction] = useState("search"),
    [source, setSource] = useState<any>(null),
    [feedback, setFeedback] = useState(""),
    [answeredQuestion, setAnsweredQuestion] = useState("");
  async function search(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    setFeedback("");
    setAnsweredQuestion(question);
    try {
      if (action === "ask") {
        const data = await request("/api/ask", {
          method: "POST",
          body: JSON.stringify({ question, mode }),
        });
        setAnswer(data);
        setHits(
          data.citations.map((c: any) => ({
            ...c,
            id: c.document_id + ":" + c.number,
          }))
        );
      } else {
        const data = await request(
          "/api/search?" + new URLSearchParams({ q: question, mode })
        );
        setHits(data.hits);
        setAnswer(null);
      }
      setSearched(true);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function sendFeedback(rating: string) {
    try {
      await request("/api/feedback", {
        method: "POST",
        body: JSON.stringify({
          question: answeredQuestion,
          rating,
          comment: "",
        }),
      });
      setFeedback("Thank you. Your feedback is recorded.");
    } catch (e) {
      setError((e as Error).message);
    }
  }
  async function openSource(hit: any) {
    try {
      setSource(
        await request(
          `/api/documents/${hit.document_id}/revisions/${hit.revision}`
        )
      );
    } catch (e) {
      setError((e as Error).message);
    }
  }
  return (
    <section className="search-desk" aria-label="Knowledge search">
      <form onSubmit={search}>
        <label htmlFor="question">What would you like to know?</label>
        <div className="question-row">
          <input
            id="question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            required
            maxLength={1000}
            placeholder="How long do we retain database backups?"
          />
          <button className="primary" disabled={busy}>
            {busy
              ? "Working…"
              : action === "ask"
              ? "Ask knowledge"
              : "Search sources"}
          </button>
        </div>
        <div className="controls">
          <label htmlFor="action">I want to</label>
          <select
            id="action"
            value={action}
            onChange={(e) => setAction(e.target.value)}
          >
            <option value="search">Find documents</option>
            <option value="ask">Get a supported answer</option>
          </select>
          <label htmlFor="retrieval">Find sources using</label>
          <select
            id="retrieval"
            value={mode}
            onChange={(e) => setMode(e.target.value)}
          >
            <option value="lexical">Keyword matching</option>
            <option value="dense" disabled={!denseAvailable}>
              Semantic matching
            </option>
            <option value="fusion" disabled={!denseAvailable}>
              Combined matching
            </option>
            <option value="rerank" disabled={!denseAvailable}>
              Combined + relevance check
            </option>
          </select>
        </div>
      </form>
      {error && (
        <p role="alert" className="notice error">
          {error}
        </p>
      )}
      {busy && (
        <p role="status" className="quiet">
          Looking through your accessible documents…
        </p>
      )}
      {answer && !busy && (
        <article
          className={"answer-card " + (answer.abstained ? "abstained" : "")}
          aria-label="Answer"
        >
          <p className="eyebrow">
            {answer.abstained ? "MORE EVIDENCE NEEDED" : "SUPPORTED ANSWER"}
            {answer.cached ? " · SAVED RESULT" : ""}
          </p>
          <p className="answer-text">{answer.answer}</p>
          <p className="quiet">
            {answer.abstained
              ? "Search sources or refine your question."
              : "Check the cited passages before relying on the answer."}
          </p>
          <div className="feedback">
            <span>Was this useful?</span>
            <button onClick={() => sendFeedback("helpful")}>Helpful</button>
            <button onClick={() => sendFeedback("incorrect")}>Incorrect</button>
            <button onClick={() => sendFeedback("missing_source")}>
              Missing a source
            </button>
          </div>
          {feedback && (
            <p role="status" className="quiet">
              {feedback}
            </p>
          )}
        </article>
      )}
      {searched && !busy && (
        <div className="result-heading">
          <h2>Sources</h2>
          <span>{hits.length} relevant passages</span>
        </div>
      )}
      {searched && !busy && !hits.length && (
        <div className="empty">
          <h3>No accessible sources matched.</h3>
          <p>
            Try a specific term from the document, or ask an administrator to
            check its access and indexing status.
          </p>
        </div>
      )}
      <div className="source-grid">
        {hits.map((h) => (
          <article className="source-card" key={h.id}>
            <p className="eyebrow">
              {h.source} · PAGE {h.page}
            </p>
            <h3>
              <button className="source-link" onClick={() => openSource(h)}>
                {h.title} <span aria-hidden="true">↗</span>
              </button>
            </h3>
            <p>{h.text}</p>
            <span className="quiet">
              Revision {h.revision} · source characters {h.start}–{h.end}
            </span>
          </article>
        ))}
      </div>
      {source && (
        <SourceDialog source={source} onClose={() => setSource(null)} />
      )}
    </section>
  );
}
