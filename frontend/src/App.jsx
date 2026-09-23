import { useRef, useState } from "react";
import ModelPanel from "./ModelPanel.jsx";

const WS_URL = "ws://localhost:8765";

const CATEGORIES = [
  "Praise", "Criticism", "Question", "Suggestion", "Spam / Promotion",
  "Toxicity", "Humor", "Personal Story", "Technical Issue", "Other",
];

// A fresh, empty snapshot for one model. The backend fills these in.
function emptyModel() {
  const counts = {};
  CATEGORIES.forEach((c) => (counts[c] = 0));
  return { counts, processed: 0, time_seconds: 0, speed: 0 };
}

export default function App() {
  const [jev, setJev] = useState(emptyModel);
  const [llm, setLlm] = useState(emptyModel);
  const [total, setTotal] = useState(0);
  const [status, setStatus] = useState("Idle");
  const [running, setRunning] = useState(false);
  const wsRef = useRef(null);

  function start() {
    setJev(emptyModel());
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
        // Backend already computed everything; just store the snapshot.
        if (msg.model === "jev") setJev(msg);
        else setLlm(msg);
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

  const done = Math.min(jev.processed, llm.processed);
  const pct = total ? (done / total) * 100 : 0;

  // Speed comparison uses the speeds the backend sent.
  let winner = null;
  if (jev.speed && llm.speed) {
    const faster = jev.speed >= llm.speed ? "JEV" : "LLM";
    const factor = (Math.max(jev.speed, llm.speed) / Math.min(jev.speed, llm.speed)).toFixed(1);
    winner = { faster, factor };
  }

  return (
    <div className="app">
      <header>
        <h1>JEV vs LLM — Live Comment Classifier</h1>
        <p>Each comment is sent to both models in parallel. Watch the counts and speed update live.</p>
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
          className="jev"
          title="JEV Model"
          tag="System-1 classifier"
          model={jev}
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
            Speed: <b>{winner.faster}</b> is about <b>{winner.factor}x</b> faster right now.
          </>
        )}
      </div>
    </div>
  );
}
