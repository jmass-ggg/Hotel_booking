import DashboardLayout from "../components/layout/DashboardLayout";
import InfoSection from "../components/seller/InfoSection";
import "../styles/sellerProfile.css";

function Rooms() {
  const rooms = [
    {
      roomNumber: "1101",
      floor: 11,
      roomType: "Deluxe King",
      price: "$195.00",
      status: "active",
    },
    {
      roomNumber: "1102",
      floor: 11,
      roomType: "Deluxe King",
      price: "$195.00",
      status: "active",
    },
    {
      roomNumber: "1204",
      floor: 12,
      roomType: "Executive Twin",
      price: "$220.00",
      status: "out_of_order",
    },
    {
      roomNumber: "1401",
      floor: 14,
      roomType: "Family Suite",
      price: "$340.00",
      status: "active",
    },
  ];

  const stats = [
    {
      label: "Total Rooms",
      value: "26",
      helper: "Current inventory tied to this property",
    },
    {
      label: "Active Rooms",
      value: "25",
      helper: "Sellable units available for booking",
      badge: "Healthy",
      tone: "success",
    },
    {
      label: "Out of Order",
      value: "1",
      helper: "Temporarily unavailable due to maintenance",
      badge: "Needs follow-up",
      tone: "warning",
    },
  ];

  return (
    <DashboardLayout
      title="Rooms"
      subtitle="Manage room-level inventory, pricing, assignments and operational status."
      actions={
        <>
          <button className="btn btn-light" type="button">
            Import Inventory
          </button>
          <button className="btn btn-primary" type="button">
            Add Room
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

      <section className="card table-card">
        <div className="table-toolbar">
          <div>
            <span className="card-kicker">Inventory</span>
            <h3>Room List</h3>
            <p>Track room number, floor, mapped type, nightly price and status.</p>
          </div>

          <div className="toolbar-chips">
            <button type="button" className="filter-chip active">
              All
            </button>
            <button type="button" className="filter-chip">
              Active
            </button>
            <button type="button" className="filter-chip">
              Out of Order
            </button>
          </div>
        </div>

        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Room Number</th>
                <th>Floor</th>
                <th>Room Type</th>
                <th>Price</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>

            <tbody>
              {rooms.map((room) => (
                <tr key={room.roomNumber}>
                  <td>{room.roomNumber}</td>
                  <td>{room.floor}</td>
                  <td>{room.roomType}</td>
                  <td>{room.price}</td>
                  <td>
                    <span
                      className={`status-pill ${
                        room.status === "active" ? "success" : "warning"
                      }`}
                    >
                      {room.status === "active" ? "Active" : "Out of Order"}
                    </span>
                  </td>
                  <td className="table-actions">
                    <button type="button" className="table-link">
                      Edit
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <InfoSection title="Create / Edit Room">
        <div className="form-grid">
          <div className="form-group">
            <label>Room Number</label>
            <input type="text" placeholder="e.g. 1204" />
          </div>

          <div className="form-group">
            <label>Floor</label>
            <input type="number" min="0" placeholder="12" />
          </div>

          <div className="form-group">
            <label>Property</label>
            <select defaultValue="royal-suites-manhattan">
              <option value="royal-suites-manhattan">
                Royal Suites Manhattan
              </option>
            </select>
          </div>

          <div className="form-group">
            <label>Room Type</label>
            <select defaultValue="">
              <option value="" disabled>
                Select room type
              </option>
              <option value="deluxe-king">Deluxe King</option>
              <option value="executive-twin">Executive Twin</option>
              <option value="family-suite">Family Suite</option>
            </select>
          </div>

          <div className="form-group">
            <label>Price</label>
            <input type="text" placeholder="$199.00" />
          </div>

          <div className="form-group">
            <label>Status</label>
            <select defaultValue="active">
              <option value="active">Active</option>
              <option value="out_of_order">Out of Order</option>
            </select>
          </div>

          <div className="form-group form-group-full">
            <label>Room Photos</label>
            <div className="upload-grid compact-upload">
              <button type="button" className="upload-card upload-card-add">
                <div className="upload-visual upload-visual-dashed">
                  <span className="material-symbols-outlined">add_photo_alternate</span>
                </div>
                <strong>Add Room Photo</strong>
                <span>Upload room-specific images</span>
              </button>
            </div>
          </div>
        </div>

        <div className="action-bar with-top-border">
          <button className="btn btn-light" type="button">
            Cancel
          </button>
          <button className="btn btn-primary" type="button">
            Save Room
          </button>
        </div>
      </InfoSection>
    </DashboardLayout>
  );
}

export default Rooms;