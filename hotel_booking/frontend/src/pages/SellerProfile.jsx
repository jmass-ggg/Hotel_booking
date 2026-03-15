import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import DashboardLayout from "../components/layout/DashboardLayout";
import InfoSection from "../components/seller/InfoSection";
import { getMe } from "../api/authApi";
import "../styles/sellerProfile.css";

function SellerProfile() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const hasFetchedRef = useRef(false);

  const loadProfile = useCallback(async () => {
    try {
      setLoading(true);
      setError("");

      const data = await getMe();
      setUser(data);
    } catch (err) {
      setError(err.message || "Failed to load profile.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (hasFetchedRef.current) return;
    hasFetchedRef.current = true;
    loadProfile();
  }, [loadProfile]);

  const initials = useMemo(() => {
    if (!user?.username) return "U";
    return user.username.charAt(0).toUpperCase();
  }, [user?.username]);

  const verificationText = useMemo(() => {
    return user ? "Verified Login" : "Unknown";
  }, [user]);

  const stats = useMemo(
    () => [
      {
        label: "Username",
        value: user?.username || "-",
        helper: "Loaded from /api/auth/me/",
      },
      {
        label: "Email",
        value: user?.email || "-",
        helper: "Current account email",
      },
      {
        label: "Verification",
        value: verificationText,
        helper: "Based on authenticated me API response",
        badge: user ? "Active" : "Unknown",
        tone: user ? "success" : "warning",
      },
    ],
    [user, verificationText]
  );

  return (
    <DashboardLayout
      title="Seller Profile"
      subtitle="Account information loaded from your me API."
      actions={
        <button
          className="btn btn-primary"
          type="button"
          onClick={loadProfile}
          disabled={loading}
        >
          {loading ? "Refreshing..." : "Refresh Profile"}
        </button>
      }
    >
      {error ? <div className="status-message error">{error}</div> : null}

      <div className="stats-grid">
        {stats.map((item) => (
          <section className="card stat-card" key={item.label}>
            <div className="stat-meta">
              <span className="stat-label">{item.label}</span>
              {item.badge ? (
                <span className={`status-pill ${item.tone}`}>{item.badge}</span>
              ) : null}
            </div>
            <h3>{item.value}</h3>
            <p>{item.helper}</p>
          </section>
        ))}
      </div>

      <div className="profile-layout">
        <div className="profile-left">
          <section className="card profile-card">
            <div className="profile-image-wrap">
              <div className="profile-image">{initials}</div>
            </div>

            <h3>{loading ? "Loading..." : user?.username || "Unknown User"}</h3>
            <p className="profile-company">{user?.email || "No email found"}</p>

            <div className="profile-info-list">
              <div className="profile-info-item">
                <span className="material-symbols-outlined">person</span>
                <span>{user?.username || "-"}</span>
              </div>

              <div className="profile-info-item">
                <span className="material-symbols-outlined">mail</span>
                <span>{user?.email || "-"}</span>
              </div>

              <div className="profile-info-item">
                <span className="material-symbols-outlined">verified_user</span>
                <span>{verificationText}</span>
              </div>

              <div className="profile-info-item">
                <span className="material-symbols-outlined">badge</span>
                <span>Role ID: {user?.role ?? "-"}</span>
              </div>
            </div>
          </section>
        </div>

        <div className="profile-right">
          <InfoSection title="Account Information">
            <div className="form-grid">
              <div className="form-group">
                <label>Username</label>
                <input
                  type="text"
                  value={user?.username || ""}
                  readOnly
                  placeholder="Username"
                />
              </div>

              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={user?.email || ""}
                  readOnly
                  placeholder="Email"
                />
              </div>

              <div className="form-group">
                <label>Verification</label>
                <input
                  type="text"
                  value={verificationText}
                  readOnly
                  placeholder="Verification"
                />
              </div>

              <div className="form-group">
                <label>Role</label>
                <input
                  type="text"
                  value={user?.role ?? ""}
                  readOnly
                  placeholder="Role"
                />
              </div>
            </div>
          </InfoSection>

          <section className="card">
            <div className="mini-panel-header">
              <h3>API Response Summary</h3>
              <span className="status-pill success">Live</span>
            </div>

            <p className="muted-paragraph">
              This page is using <strong>/api/auth/me/</strong> and showing only
              username, email, role and a verification label.
            </p>
          </section>

          {loading ? <div className="empty-panel">Loading profile...</div> : null}
        </div>
      </div>
    </DashboardLayout>
  );
}

export default SellerProfile;