import { useEffect, useState } from "react";
import Sidebar from "../Sidebar";
import Topbar from "../Topbar";
import { getMe } from "../../api/authApi";

function DashboardLayout({ title, subtitle, actions, children }) {
  const [user, setUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("me") || "null");
    } catch {
      return null;
    }
  });

  useEffect(() => {
    let mounted = true;

    const loadUser = async () => {
      try {
        const me = await getMe();
        if (!mounted) return;
        setUser(me);
        localStorage.setItem("me", JSON.stringify(me));
      } catch {
        if (!mounted) return;
        setUser(null);
      }
    };

    loadUser();

    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="dashboard">
      <Sidebar user={user} />

      <div className="dashboard-content">
        <Topbar user={user} />

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