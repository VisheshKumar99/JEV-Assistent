// One model's live panel. All numbers come straight from the backend snapshot.
export default function ModelPanel({ className, title, tag, model, categories }) {
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

      <ul className="cats">
        {categories.map((cat) => (
          <li key={cat}>
            <span>{cat}</span>
            <span className="count">{model.counts[cat]}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
