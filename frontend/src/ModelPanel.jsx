// One model's live panel. All numbers come straight from the backend snapshot.
// Each category is a bubble whose size grows with its count; the current leader
// is highlighted, and a live feed shows the most recent classifications.

const MIN_SIZE = 28; // px diameter when count is 0
const MAX_SIZE = 100; // px diameter for the current top category

export default function ModelPanel({ className, title, tag, model, categories }) {
  const counts = model.counts || {};
  const total = categories.reduce((sum, cat) => sum + (counts[cat] || 0), 0);
  const maxCount = Math.max(1, ...categories.map((cat) => counts[cat] || 0));

  // The category currently in the lead (first one that hits maxCount, > 0).
  const leader =
    maxCount > 0 ? categories.find((cat) => (counts[cat] || 0) === maxCount) : null;

  const sizeFor = (count) => {
    // Area-proportional: radius grows with sqrt so 4x count reads as ~2x wide.
    const ratio = Math.sqrt((count || 0) / maxCount);
    return MIN_SIZE + ratio * (MAX_SIZE - MIN_SIZE);
  };

  const pctFor = (count) => (total ? Math.round((count / total) * 100) : 0);

  return (
    <section className={`panel ${className}`}>
      <div className="panel-head">
        <div>
          <h2>{title}</h2>
          <div className="tag">{tag}</div>
        </div>
        {leader && (
          <div className="leader">
            <span className="leader-lbl">Leading</span>
            <span className="leader-cat">{leader}</span>
          </div>
        )}
      </div>

      <div className="stats">
        <div className="stat">
          <div className="num">{model.processed}</div>
          <div className="lbl">Processed</div>
        </div>
        <div className="stat">
          <div className="num">{(model.time_seconds || 0).toFixed(1)}s</div>
          <div className="lbl">Time spent</div>
        </div>
        <div className="stat">
          <div className="num">{(model.speed || 0).toFixed(1)}</div>
          <div className="lbl">Comments/sec</div>
        </div>
      </div>

      <div className="bubbles">
        {categories.map((cat) => {
          const count = counts[cat] || 0;
          const size = sizeFor(count);
          const isLeader = cat === leader && count > 0;
          return (
            <div className="bubble-cell" key={cat}>
              <div
                className={`bubble${isLeader ? " lead" : ""}`}
                style={{ width: `${size}px`, height: `${size}px` }}
                title={`${cat}: ${count} (${pctFor(count)}%)`}
              >
                <span className="bubble-count">{count}</span>
              </div>
              <span className="bubble-label">{cat}</span>
            </div>
          );
        })}
      </div>

      <div className="feed">
        <div className="feed-title">Live feed</div>
        {(model.feed || []).length === 0 ? (
          <div className="feed-empty">Waiting for comments…</div>
        ) : (
          <ul>
            {model.feed.map((item) => (
              <li key={item.id}>
                <span className={`chip cat-${slug(item.category)}`}>{item.category}</span>
                <span className="feed-text" title={item.comment}>{item.comment}</span>
                <span className="feed-ms">{Math.round(item.ms)}ms</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}

// Turn a category name into a css-safe slug for the chip color.
function slug(name) {
  return name.toLowerCase().replace(/[^a-z]+/g, "-").replace(/^-|-$/g, "");
}
