function ProfileCard() {
  return (
    <section className="card">
      <div className="profile-card">
        <div className="profile-image-wrap">
          <div className="profile-image">A</div>
          <button className="edit-avatar-btn">
            <span className="material-symbols-outlined">edit</span>
          </button>
        </div>

        <h3>Alex Johnson</h3>
        <p className="profile-company">Royal Suites Group</p>

        <div className="profile-info-list">
          <div className="profile-info-item">
            <span className="material-symbols-outlined">mail</span>
            <span>alex.johnson@royalsuites.com</span>
          </div>

          <div className="profile-info-item">
            <span className="material-symbols-outlined">call</span>
            <span>+1 (555) 123-4567</span>
          </div>

          <div className="profile-info-item">
            <span className="material-symbols-outlined">location_on</span>
            <span>New York, USA</span>
          </div>
        </div>
      </div>
    </section>
  );
}

export default ProfileCard;