import Sidebar from "../Sidebar";
import Topbar from "../Topbar";

function DashboardLayout({ title, subtitle, actions, children }) {
  return (
    <div className="dashboard">
      <Sidebar />

      <div className="dashboard-content">
        <Topbar />

        <main className="page-content">
          <div className="page-header-row">
            <div className="page-header">
              <span className="eyebrow">Hotel Partner Workspace</span>
              <h1>{title}</h1>
              <p>{subtitle}</p>
            </div>

            {actions ? <div className="page-actions">{actions}</div> : null}
          </div>

          {children}
        </main>
      </div>
    </div>
  );
}

export default DashboardLayout;