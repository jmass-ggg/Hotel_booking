function Topbar() {
  return (
    <header className="topbar">
      <div className="topbar-search">
        <span className="material-symbols-outlined search-icon">search</span>
        <input type="text" placeholder="Search properties, rooms, sellers..." />
      </div>

      <div className="topbar-actions">
        <div className="workspace-pill">
          <span className="material-symbols-outlined">bolt</span>
          Live workspace
        </div>

        <button className="btn btn-primary topbar-btn" type="button">
          <span className="material-symbols-outlined">add</span>
          Quick Add
        </button>

        <button className="icon-btn" type="button">
          <span className="material-symbols-outlined">notifications</span>
          <span className="dot"></span>
        </button>

        <div className="topbar-divider"></div>

        <div className="user-box">
          <div className="user-text">
            <strong>Royal Suites Group</strong>
            <span>Hotel Admin</span>
          </div>
          <div className="user-avatar">A</div>
        </div>
      </div>
    </header>
  );
}

export default Topbar;