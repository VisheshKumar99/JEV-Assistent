import { useRef, useState } from "react";
import ModelPanel from "./ModelPanel.jsx";

const WS_URL = "ws://localhost:8765";

const CATEGORIES = [
  "Praise", "Criticism", "Question", "Suggestion", "Spam / Promotion",
  "Toxicity", "Humor", "Personal Story", "Technical Issue", "Other",
];

const MAX_FEED = 8; // how many recent classifications to keep per model

// A fresh, empty snapshot for one model. The backend fills these in.
function emptyModel() {
  const counts = {};
  CATEGORIES.forEach((c) => (counts[c] = 0));
  return { counts, processed: 0, time_seconds: 0, speed: 0, feed: [] };
}

export default function App() {
  const [laya, setLaya] = useState(emptyModel);
  const [llm, setLlm] = useState(emptyModel);
  const [total, setTotal] = useState(0);
  const [status, setStatus] = useState("Idle");
  const [running, setRunning] = useState(false);
  const wsRef = useRef(null);

  // Merge a backend snapshot into the model state, keeping a rolling feed of
  // the most recent classifications so the UI can show live activity.
  function applySnapshot(prev, msg) {
    let feed = prev.feed || [];
    if (msg.last_comment) {
      feed = [
        {
          id: msg.processed,
          comment: msg.last_comment,
          category: msg.last_category || "Other",
          ms: msg.last_ms,
        },
        ...feed,
      ].slice(0, MAX_FEED);
    }
    return { ...msg, feed };
  }

  function start() {
    setLaya(emptyModel());
    setLlm(emptyModel());
    setRunning(true);
    setStatus("Connecting...");

    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => ws.send(JSON.stringify({ action: "start" }));

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);

      if (msg.type === "start") {
        setTotal(msg.total);
        setStatus(`0 / ${msg.total}`);
      } else if (msg.type === "stats") {
        if (msg.model === "laya") setLaya((prev) => applySnapshot(prev, msg));
        else setLlm((prev) => applySnapshot(prev, msg));
      } else if (msg.type === "done") {
        setStatus(`Done — ${msg.total} comments`);
        setRunning(false);
        ws.close();
      }
    };

    ws.onerror = () => {
      setStatus("Connection error — is the backend running?");
      setRunning(false);
    };
  }

  const done = Math.min(laya.processed, llm.processed);
  const pct = total ? (done / total) * 100 : 0;

  // Speed comparison uses the speeds the backend sent.
  let winner = null;
  if (laya.speed && llm.speed) {
    const faster = laya.speed >= llm.speed ? "LAYA" : "LLM";
    const factor = (Math.max(laya.speed, llm.speed) / Math.min(laya.speed, llm.speed)).toFixed(1);
    winner = { faster, factor };
  }

  return (
    <div className="app">
      <header>
        <h1>LAYA vs LLM — Live Comment Classifier</h1>
        <p>Each comment is sent to both models in parallel. Watch the counts, the live feed, and the speed race update in real time.</p>
      </header>

      <div className="bar">
        <button onClick={start} disabled={running}>
          {running ? "Processing..." : "Start Process"}
        </button>
      </div>

      <div className="progress">
        <div style={{ width: `${pct}%` }} />
      </div>
      <div className="progress-label">
        {status !== "Idle" && total ? `${done} / ${total}` : status}
      </div>

      <div className="grid">
        <ModelPanel
          className="laya"
          title="LAYA Model"
          tag="Typed decision model"
          model={laya}
          categories={CATEGORIES}
        />
        <ModelPanel
          className="llm"
          title="LLM Model"
          tag="LLM provider"
          model={llm}
          categories={CATEGORIES}
        />
      </div>

      <div className="winner">
        {winner && (
          <>
            Speed race: <b>{winner.faster}</b> is about <b>{winner.factor}x</b> faster right now.
          </>
        )}
      </div>
    </div>
  );
}
