function SecurityCard() {
  return (
    <section className="card section-card">
      <div className="section-header">
        <h3>Security</h3>
      </div>

      <div className="section-body">
        <div className="security-box">
          <div className="security-left">
            <div className="security-icon-wrap">
              <span className="material-symbols-outlined">security</span>
            </div>

            <div>
              <h4>Two-Factor Authentication</h4>
              <p>Protect your account with an extra layer of security.</p>
              <span className="security-status">
                <span className="material-symbols-outlined small-icon">
                  check_circle
                </span>
                Enabled via Authenticator App
              </span>
            </div>
          </div>

          <button className="btn btn-secondary">Change Password</button>
        </div>
      </div>
    </section>
  );
}

export default SecurityCard;