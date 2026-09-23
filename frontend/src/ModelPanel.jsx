// One model's live panel. All numbers come straight from the backend snapshot.
// Each category is drawn as a bubble whose size grows with its count.

const MIN_SIZE = 26; // px diameter when count is 0
const MAX_SIZE = 96; // px diameter for the current top category

export default function ModelPanel({ className, title, tag, model, categories }) {
  // Scale bubbles relative to the biggest count in THIS panel so the largest
  // category fills the bubble and everything else scales proportionally.
  const maxCount = Math.max(1, ...categories.map((cat) => model.counts[cat] || 0));

  const sizeFor = (count) => {
    // Area-proportional scaling: radius grows with sqrt of the count so a
    // category with 4x the count looks 2x wider, which reads more honestly.
    const ratio = Math.sqrt((count || 0) / maxCount);
    return MIN_SIZE + ratio * (MAX_SIZE - MIN_SIZE);
  };

  return (
    <section className={`panel ${className}`}>
      <h2>{title}</h2>
      <div className="tag">{tag}</div>

      <div className="stats">
        <div className="stat">
          <div className="num">{model.processed}</div>
          <div className="lbl">Processed</div>
        </div>
        <div className="stat">
          <div className="num">{model.time_seconds.toFixed(1)}s</div>
          <div className="lbl">Time spent</div>
        </div>
        <div className="stat">
          <div className="num">{model.speed.toFixed(1)}</div>
          <div className="lbl">Comments/sec</div>
        </div>
      </div>

      <div className="bubbles">
        {categories.map((cat) => {
          const count = model.counts[cat] || 0;
          const size = sizeFor(count);
          return (
            <div className="bubble-cell" key={cat}>
              <div
                className="bubble"
                style={{ width: `${size}px`, height: `${size}px` }}
                title={`${cat}: ${count}`}
              >
                <span className="bubble-count">{count}</span>
              </div>
              <span className="bubble-label">{cat}</span>
            </div>
          );
        })}
      </div>
    </section>
  );
}
