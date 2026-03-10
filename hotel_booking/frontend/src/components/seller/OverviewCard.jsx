function OverviewCard() {
  return (
    <section className="card">
      <h4 className="card-small-title">Account Overview</h4>

      <div className="overview-list">
        <div className="overview-row">
          <span>Verification Status</span>
          <span className="status-pill success">
            <span className="material-symbols-outlined small-icon">verified</span>
            Verified
          </span>
        </div>

        <div className="overview-row">
          <span>Account Age</span>
          <strong>2 years, 4 months</strong>
        </div>

        <div className="overview-row">
          <span>Seller Tier</span>
          <strong className="premium-text">
            <span className="material-symbols-outlined small-icon">grade</span>
            Premium
          </strong>
        </div>
      </div>
    </section>
  );
}

export default OverviewCard;