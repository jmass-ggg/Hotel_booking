function InfoSection({ title, children }) {
  return (
    <section className="card section-card">
      <div className="section-header">
        <h3>{title}</h3>
      </div>

      <div className="section-body">{children}</div>
    </section>
  );
}

export default InfoSection;