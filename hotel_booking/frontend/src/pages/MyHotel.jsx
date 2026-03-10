import DashboardLayout from "../components/layout/DashboardLayout";
import InfoSection from "../components/seller/InfoSection";
import "../styles/sellerProfile.css";

function MyHotel() {
  const stats = [
    {
      label: "Listing Status",
      value: "Approved",
      helper: "Property has passed review and is ready to publish",
      badge: "Review complete",
      tone: "success",
    },
    {
      label: "Property Amenities",
      value: "18",
      helper: "Core facilities mapped for this listing",
    },
    {
      label: "Media Coverage",
      value: "12 Photos",
      helper: "Recommended minimum content is already met",
    },
  ];

  const amenities = [
    "Free Wi-Fi",
    "Airport Shuttle",
    "Swimming Pool",
    "Spa",
    "Gym",
    "Room Service",
    "Restaurant",
    "Bar",
    "Meeting Room",
    "Parking",
    "24/7 Front Desk",
    "Laundry",
  ];

  const gallery = [
    "Main facade",
    "Lobby reception",
    "Executive lounge",
    "Deluxe room",
    "Pool deck",
    "Restaurant",
  ];

  const checklist = [
    "Property details completed",
    "Primary contact confirmed",
    "Amenities assigned",
    "Photos uploaded",
    "Timezone configured",
    "Ready for publication",
  ];

  return (
    <DashboardLayout
      title="My Hotel"
      subtitle="Manage property details, amenities, listing readiness and visual content."
      actions={
        <>
          <button className="btn btn-light" type="button">
            Preview Listing
          </button>
          <button className="btn btn-primary" type="button">
            Save Property
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

      <div className="hotel-layout">
        <div className="hotel-main">
          <InfoSection title="Property Details">
            <div className="form-grid">
              <div className="form-group">
                <label>Property Name</label>
                <input type="text" defaultValue="Royal Suites Manhattan" />
              </div>

              <div className="form-group">
                <label>Status</label>
                <select defaultValue="approved">
                  <option value="draft">Draft</option>
                  <option value="submitted">Submitted</option>
                  <option value="under_review">Under review</option>
                  <option value="changes_requested">Changes requested</option>
                  <option value="rejected">Rejected</option>
                  <option value="approved">Approved</option>
                  <option value="published">Published</option>
                  <option value="suspended">Suspended</option>
                </select>
              </div>

              <div className="form-group">
                <label>Contact Email</label>
                <input type="email" defaultValue="stay@royalsuites.com" />
              </div>

              <div className="form-group">
                <label>Contact Number</label>
                <input type="text" defaultValue="+1 (800) 454-7788" />
              </div>
            </div>
          </InfoSection>

          <InfoSection title="Location & Operations">
            <div className="form-grid">
              <div className="form-group form-group-full">
                <label>Address</label>
                <input
                  type="text"
                  defaultValue="500 5th Ave, New York, NY 10110"
                />
              </div>

              <div className="form-group">
                <label>City</label>
                <input type="text" defaultValue="New York" />
              </div>

              <div className="form-group">
                <label>Country</label>
                <input type="text" defaultValue="United States" />
              </div>

              <div className="form-group">
                <label>Timezone</label>
                <select defaultValue="America/New_York">
                  <option value="UTC">UTC</option>
                  <option value="America/New_York">America/New_York</option>
                  <option value="Europe/London">Europe/London</option>
                  <option value="Asia/Dubai">Asia/Dubai</option>
                </select>
              </div>

              <div className="form-group">
                <label>Front Desk Hours</label>
                <input type="text" defaultValue="24/7" />
              </div>
            </div>
          </InfoSection>

          <InfoSection title="Property Amenities">
            <div className="chip-grid">
              {amenities.map((amenity) => (
                <span className="amenity-chip selected" key={amenity}>
                  <span className="material-symbols-outlined">check</span>
                  {amenity}
                </span>
              ))}
            </div>
          </InfoSection>

          <InfoSection title="Property Gallery">
            <div className="upload-grid">
              {gallery.map((item) => (
                <div className="upload-card" key={item}>
                  <div className="upload-visual">
                    <span className="material-symbols-outlined">image</span>
                  </div>
                  <strong>{item}</strong>
                  <span>Replace photo</span>
                </div>
              ))}

              <button type="button" className="upload-card upload-card-add">
                <div className="upload-visual upload-visual-dashed">
                  <span className="material-symbols-outlined">add_photo_alternate</span>
                </div>
                <strong>Add Property Photo</strong>
                <span>Drag & drop or browse</span>
              </button>
            </div>
          </InfoSection>
        </div>

        <aside className="hotel-side">
          <section className="card sticky-card">
            <div className="mini-panel-header">
              <h3>Listing Readiness</h3>
              <span className="status-pill success">96%</span>
            </div>

            <div className="checklist">
              {checklist.map((item) => (
                <div className="checklist-item" key={item}>
                  <span className="material-symbols-outlined">check_circle</span>
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </section>

          <section className="card">
            <div className="mini-panel-header">
              <h3>Review Notes</h3>
              <span className="status-pill info">Last updated today</span>
            </div>

            <p className="muted-paragraph">
              Your property passed compliance review. Add a few more exterior
              photos and publish when ready.
            </p>
          </section>
        </aside>
      </div>
    </DashboardLayout>
  );
}

export default MyHotel;