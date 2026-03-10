import DashboardLayout from "../components/layout/DashboardLayout";
import InfoSection from "../components/seller/InfoSection";
import "../styles/sellerProfile.css";

function RoomTypes() {
  const roomTypes = [
    {
      name: "Deluxe King",
      maxOccupancy: 2,
      bed: "1 King Bed",
      description:
        "Premium city-view room with workstation, minibar and rainfall shower.",
      rooms: 12,
      price: "$195 / night",
      amenities: ["Wi-Fi", "Smart TV", "Minibar", "Work Desk", "City View"],
    },
    {
      name: "Executive Twin",
      maxOccupancy: 2,
      bed: "2 Twin Beds",
      description:
        "Ideal for business travelers with lounge access and faster check-in.",
      rooms: 8,
      price: "$220 / night",
      amenities: ["Wi-Fi", "Breakfast", "Lounge Access", "Safe", "Coffee Kit"],
    },
    {
      name: "Family Suite",
      maxOccupancy: 4,
      bed: "1 King + Sofa Bed",
      description:
        "Large layout with a separate sitting area and added luggage space.",
      rooms: 6,
      price: "$340 / night",
      amenities: ["Wi-Fi", "Bathtub", "Living Area", "Mini Fridge", "Dining Nook"],
    },
  ];

  const stats = [
    {
      label: "Active Room Types",
      value: "3",
      helper: "Structured room inventory templates",
    },
    {
      label: "Mapped Amenities",
      value: "15",
      helper: "Attached across all room type categories",
    },
    {
      label: "Average Capacity",
      value: "2.7 Guests",
      helper: "Across current room type definitions",
    },
  ];

  return (
    <DashboardLayout
      title="Room Types"
      subtitle="Define inventory categories, capacities, bed setup and room-level amenities."
      actions={
        <>
          <button className="btn btn-light" type="button">
            Duplicate Type
          </button>
          <button className="btn btn-primary" type="button">
            Add Room Type
          </button>
        </>
      }
    >
      <div className="stats-grid">
        {stats.map((item) => (
          <section className="card stat-card" key={item.label}>
            <div className="stat-meta">
              <span className="stat-label">{item.label}</span>
            </div>
            <h3>{item.value}</h3>
            <p>{item.helper}</p>
          </section>
        ))}
      </div>

      <section className="room-type-grid">
        {roomTypes.map((type) => (
          <article className="card room-type-card" key={type.name}>
            <div className="room-type-top">
              <div>
                <span className="card-kicker">Room Type</span>
                <h3>{type.name}</h3>
              </div>

              <span className="status-pill neutral">{type.rooms} rooms</span>
            </div>

            <p className="room-type-description">{type.description}</p>

            <div className="room-type-meta">
              <div>
                <span>Max Occupancy</span>
                <strong>{type.maxOccupancy} Guests</strong>
              </div>
              <div>
                <span>Base Bed Type</span>
                <strong>{type.bed}</strong>
              </div>
              <div>
                <span>Starting Rate</span>
                <strong>{type.price}</strong>
              </div>
            </div>

            <div className="chip-grid compact">
              {type.amenities.map((amenity) => (
                <span className="amenity-chip" key={amenity}>
                  {amenity}
                </span>
              ))}
            </div>

            <div className="card-footer-actions">
              <button className="btn btn-light" type="button">
                View Rooms
              </button>
              <button className="btn btn-secondary" type="button">
                Edit Type
              </button>
            </div>
          </article>
        ))}
      </section>

      <InfoSection title="Create / Edit Room Type">
        <div className="form-grid">
          <div className="form-group">
            <label>Room Type Name</label>
            <input type="text" placeholder="e.g. Deluxe King" />
          </div>

          <div className="form-group">
            <label>Max Occupancy</label>
            <input type="number" min="1" placeholder="2" />
          </div>

          <div className="form-group">
            <label>Base Bed Type</label>
            <input type="text" placeholder="e.g. 1 King Bed" />
          </div>

          <div className="form-group">
            <label>Default Nightly Price</label>
            <input type="text" placeholder="$199.00" />
          </div>

          <div className="form-group form-group-full">
            <label>Description</label>
            <textarea
              rows="4"
              placeholder="Describe the room type experience, layout and target guest."
            />
          </div>

          <div className="form-group form-group-full">
            <label>Room Type Amenities</label>
            <div className="chip-grid">
              {[
                "Wi-Fi",
                "TV",
                "Minibar",
                "Bathtub",
                "Balcony",
                "Lounge Access",
                "Work Desk",
                "Coffee Machine",
              ].map((amenity) => (
                <span className="amenity-chip selectable" key={amenity}>
                  {amenity}
                </span>
              ))}
            </div>
          </div>
        </div>

        <div className="action-bar with-top-border">
          <button className="btn btn-light" type="button">
            Reset
          </button>
          <button className="btn btn-primary" type="button">
            Save Room Type
          </button>
        </div>
      </InfoSection>
    </DashboardLayout>
  );
}

export default RoomTypes;