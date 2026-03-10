import DashboardLayout from "../components/layout/DashboardLayout";
import InfoSection from "../components/seller/InfoSection";
import OverviewCard from "../components/seller/OverviewCard";
import ProfileCard from "../components/seller/ProfileCard";
import SecurityCard from "../components/seller/SecurityCard";
import "../styles/sellerProfile.css";

function SellerProfile() {
  const stats = [
    {
      label: "Profile Completion",
      value: "92%",
      helper: "Almost ready for full marketplace visibility",
    },
    {
      label: "Verification",
      value: "Verified",
      helper: "Identity and business details approved",
      badge: "Active",
      tone: "success",
    },
    {
      label: "Support SLA",
      value: "< 10 min",
      helper: "Average first response time this month",
    },
  ];

  return (
    <DashboardLayout
      title="Seller Profile"
      subtitle="Manage your identity, support channels and operational settings across the platform."
      actions={
        <>
          <button className="btn btn-light" type="button">
            Export Profile
          </button>
          <button className="btn btn-primary" type="button">
            Save Changes
          </button>
        </>
      }
    >
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
          <ProfileCard />
          <OverviewCard />
        </div>

        <div className="profile-right">
          <InfoSection title="Personal Information">
            <div className="form-grid">
              <div className="form-group">
                <label>First Name</label>
                <input type="text" defaultValue="Alex" />
              </div>

              <div className="form-group">
                <label>Last Name</label>
                <input type="text" defaultValue="Johnson" />
              </div>

              <div className="form-group">
                <label>Email Address</label>
                <input
                  type="email"
                  defaultValue="alex.johnson@royalsuites.com"
                />
              </div>

              <div className="form-group">
                <label>Phone Number</label>
                <input type="text" defaultValue="+1 (555) 123-4567" />
              </div>
            </div>
          </InfoSection>

          <InfoSection title="Business Details">
            <div className="form-group form-group-full">
              <label>Business Name</label>
              <input type="text" defaultValue="Royal Suites Group LLC" />
            </div>

            <div className="form-grid section-gap">
              <div className="form-group">
                <label>Tax ID / VAT Number</label>
                <input type="text" defaultValue="US-987654321" />
              </div>

              <div className="form-group">
                <label>Business Address</label>
                <input
                  type="text"
                  defaultValue="500 5th Ave, New York, NY 10110"
                />
              </div>
            </div>
          </InfoSection>

          <InfoSection title="Contact Details">
            <div className="form-grid">
              <div className="form-group">
                <label>Support Email</label>
                <input type="email" defaultValue="support@royalsuites.com" />
              </div>

              <div className="form-group">
                <label>Support Phone</label>
                <input type="text" defaultValue="+1 (800) 987-6543" />
              </div>
            </div>
          </InfoSection>

          <SecurityCard />

          <div className="action-bar">
            <button className="btn btn-light" type="button">
              Discard Changes
            </button>
            <button className="btn btn-primary" type="button">
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}

export default SellerProfile;