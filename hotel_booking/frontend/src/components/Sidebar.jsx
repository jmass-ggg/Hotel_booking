import { NavLink } from "react-router-dom";

function Sidebar({ user }) {
  const items = [
    { icon: "person_outline", label: "Seller Profile", to: "/profile" },
    { icon: "apartment", label: "My Hotel", to: "/my-hotel" },
    { icon: "category", label: "Room Types", to: "/room-types" },
    { icon: "bed", label: "Rooms", to: "/rooms" },
  ];

  if (user?.role === "SELLER") {
    items.push({
      icon: "groups",
      label: "Seller Staff",
      to: "/seller-staff",
    });
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-icon-wrap">
          <span className="material-symbols-outlined">domain</span>
        </div>

        <div>
          <h2>Royal Suites</h2>
          <p>Management Console</p>
        </div>
      </div>

      <nav className="sidebar-nav">
        <div className="sidebar-section-label">Workspace</div>

        {items.map((item) => (
          <NavLink
            key={item.label}
            to={item.to}
            className={({ isActive }) =>
              `sidebar-link ${isActive ? "active" : ""}`
            }
          >
            <span className="material-symbols-outlined">{item.icon}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}

        <div className="sidebar-footer-links">
          <button type="button" className="sidebar-link sidebar-link-muted">
            <span className="material-symbols-outlined">settings</span>
            <span>Settings</span>
          </button>
        </div>
      </nav>
    </aside>
  );
}

export default Sidebar;