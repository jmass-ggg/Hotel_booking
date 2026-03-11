import { useEffect, useMemo, useState } from "react";
import DashboardLayout from "../components/layout/DashboardLayout";
import InfoSection from "../components/seller/InfoSection";
import { getMyHotel } from "../api/hotelApi";
import { getRooms } from "../api/roomApi";
import {
  addRoomTypeAmenity,
  createRoomType,
  deleteRoomType,
  deleteRoomTypeAmenity,
  getRoomTypeAmenities,
  getRoomTypes,
  updateRoomType,
} from "../api/roomTypeApi";
import "../styles/sellerProfile.css";

const emptyRoomTypeForm = {
  id: null,
  name: "",
  max_occupancy: 2,
  base_bed_type: "",
  description: "",
};

const emptyAmenityForm = {
  name: "",
  category: "",
};

function RoomTypes() {
  const [hotel, setHotel] = useState(null);
  const [roomTypes, setRoomTypes] = useState([]);
  const [rooms, setRooms] = useState([]);
  const [amenityMap, setAmenityMap] = useState({});
  const [form, setForm] = useState(emptyRoomTypeForm);
  const [amenityForm, setAmenityForm] = useState(emptyAmenityForm);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [amenitySaving, setAmenitySaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const loadData = async () => {
    try {
      setLoading(true);
      setError("");

      const currentHotel = await getMyHotel();
      setHotel(currentHotel);

      if (!currentHotel?.id) {
        setRoomTypes([]);
        setRooms([]);
        setAmenityMap({});
        return;
      }

      const [roomTypeData, roomData] = await Promise.all([
        getRoomTypes(currentHotel.id),
        getRooms(currentHotel.id),
      ]);

      setRoomTypes(roomTypeData);
      setRooms(roomData);

      const amenityEntries = await Promise.all(
        roomTypeData.map(async (item) => {
          const amenities = await getRoomTypeAmenities(currentHotel.id, item.id);
          return [item.id, amenities];
        })
      );

      setAmenityMap(Object.fromEntries(amenityEntries));
    } catch (err) {
      setError(err.message || "Failed to load room types.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const roomCountMap = useMemo(() => {
    return rooms.reduce((acc, room) => {
      acc[room.room_type] = (acc[room.room_type] || 0) + 1;
      return acc;
    }, {});
  }, [rooms]);

  const stats = useMemo(() => {
    const totalAmenities = Object.values(amenityMap).reduce(
      (sum, list) => sum + list.length,
      0
    );

    const averageCapacity = roomTypes.length
      ? (
          roomTypes.reduce(
            (sum, item) => sum + Number(item.max_occupancy || 0),
            0
          ) / roomTypes.length
        ).toFixed(1)
      : "0.0";

    return [
      {
        label: "Active Room Types",
        value: String(roomTypes.length),
        helper: "Room categories created for this hotel",
      },
      {
        label: "Mapped Amenities",
        value: String(totalAmenities),
        helper: "Amenities attached to room types",
      },
      {
        label: "Average Capacity",
        value: `${averageCapacity} Guests`,
        helper: "Average max occupancy",
      },
    ];
  }, [roomTypes, amenityMap]);

  const currentAmenities = form.id ? amenityMap[form.id] || [] : [];

  const fillForm = (item) => {
    setForm({
      id: item.id,
      name: item.name || "",
      max_occupancy: item.max_occupancy || 1,
      base_bed_type: item.base_bed_type || "",
      description: item.description || "",
    });
    setAmenityForm(emptyAmenityForm);
    setError("");
    setSuccess("");
  };

  const resetForm = () => {
    setForm(emptyRoomTypeForm);
    setAmenityForm(emptyAmenityForm);
    setError("");
    setSuccess("");
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: name === "max_occupancy" ? Number(value) : value,
    }));
  };

  const handleAmenityFormChange = (e) => {
    const { name, value } = e.target;
    setAmenityForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSaveRoomType = async () => {
    if (!hotel?.id) {
      setError("Create hotel first.");
      return;
    }

    try {
      setSaving(true);
      setError("");
      setSuccess("");

      const payload = {
        name: form.name,
        max_occupancy: Number(form.max_occupancy),
        base_bed_type: form.base_bed_type,
        description: form.description,
      };

      if (form.id) {
        await updateRoomType(hotel.id, form.id, payload);
        setSuccess("Room type updated successfully.");
      } else {
        await createRoomType(hotel.id, payload);
        setSuccess("Room type created successfully.");
        resetForm();
      }

      await loadData();
    } catch (err) {
      setError(err.message || "Failed to save room type.");
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteRoomType = async (roomTypeId) => {
    try {
      setError("");
      setSuccess("");

      await deleteRoomType(hotel.id, roomTypeId);
      if (form.id === roomTypeId) resetForm();
      setSuccess("Room type deleted.");
      await loadData();
    } catch (err) {
      setError(err.message || "Failed to delete room type.");
    }
  };

  const handleAddAmenity = async () => {
    if (!hotel?.id || !form.id) {
      setError("Save or select a room type first.");
      return;
    }

    if (!amenityForm.name.trim()) {
      setError("Amenity name is required.");
      return;
    }

    try {
      setAmenitySaving(true);
      setError("");
      setSuccess("");

      await addRoomTypeAmenity(hotel.id, form.id, {
        name: amenityForm.name.trim(),
        category: amenityForm.category.trim(),
      });

      setAmenityForm(emptyAmenityForm);
      setSuccess("Room type amenity added.");
      await loadData();
    } catch (err) {
      setError(err.message || "Failed to add room type amenity.");
    } finally {
      setAmenitySaving(false);
    }
  };

  const handleDeleteAmenity = async (amenityLinkId) => {
    if (!hotel?.id || !form.id) return;

    try {
      setError("");
      setSuccess("");

      await deleteRoomTypeAmenity(hotel.id, form.id, amenityLinkId);
      setSuccess("Room type amenity removed.");
      await loadData();
    } catch (err) {
      setError(err.message || "Failed to remove room type amenity.");
    }
  };

  return (
    <DashboardLayout
      title="Room Types"
      subtitle="Create room categories, capacity, bed type and room-type amenities."
      actions={
        <>
          <button className="btn btn-light" type="button" onClick={resetForm}>
            New Room Type
          </button>
          <button
            className="btn btn-primary"
            type="button"
            onClick={handleSaveRoomType}
            disabled={saving}
          >
            {saving ? "Saving..." : form.id ? "Update Room Type" : "Add Room Type"}
          </button>
        </>
      }
    >
      {error ? <div className="status-message error">{error}</div> : null}
      {success ? <div className="status-message success">{success}</div> : null}

      {!hotel?.id && !loading ? (
        <div className="empty-panel">
          Create your hotel first before creating room types.
        </div>
      ) : null}

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
        {roomTypes.map((item) => {
          const amenities = amenityMap[item.id] || [];

          return (
            <article className="card room-type-card" key={item.id}>
              <div className="room-type-top">
                <div>
                  <span className="card-kicker">Room Type</span>
                  <h3>{item.name}</h3>
                </div>

                <span className="status-pill neutral">
                  {roomCountMap[item.id] || 0} rooms
                </span>
              </div>

              <p className="room-type-description">
                {item.description || "No description added."}
              </p>

              <div className="room-type-meta">
                <div>
                  <span>Max Occupancy</span>
                  <strong>{item.max_occupancy} Guests</strong>
                </div>
                <div>
                  <span>Base Bed Type</span>
                  <strong>{item.base_bed_type || "Not set"}</strong>
                </div>
                <div>
                  <span>Amenities</span>
                  <strong>{amenities.length}</strong>
                </div>
              </div>

              <div className="chip-grid compact">
                {amenities.map((amenityItem) => (
                  <span className="amenity-chip" key={amenityItem.id}>
                    {amenityItem.amenity?.name || "Amenity"}
                  </span>
                ))}
                {!amenities.length ? (
                  <span className="field-helper">No amenities assigned.</span>
                ) : null}
              </div>

              <div className="card-footer-actions">
                <button
                  className="btn btn-secondary"
                  type="button"
                  onClick={() => fillForm(item)}
                >
                  Edit Type
                </button>
                <button
                  className="btn btn-light"
                  type="button"
                  onClick={() => handleDeleteRoomType(item.id)}
                >
                  Delete
                </button>
              </div>
            </article>
          );
        })}
      </section>

      <InfoSection title={form.id ? "Edit Room Type" : "Create Room Type"}>
        <div className="form-grid">
          <div className="form-group">
            <label>Room Type Name</label>
            <input
              type="text"
              name="name"
              value={form.name}
              onChange={handleFormChange}
              placeholder="Deluxe King"
            />
          </div>

          <div className="form-group">
            <label>Max Occupancy</label>
            <input
              type="number"
              min="1"
              name="max_occupancy"
              value={form.max_occupancy}
              onChange={handleFormChange}
              placeholder="2"
            />
          </div>

          <div className="form-group form-group-full">
            <label>Base Bed Type</label>
            <input
              type="text"
              name="base_bed_type"
              value={form.base_bed_type}
              onChange={handleFormChange}
              placeholder="1 King Bed"
            />
          </div>

          <div className="form-group form-group-full">
            <label>Description</label>
            <textarea
              rows="4"
              name="description"
              value={form.description}
              onChange={handleFormChange}
              placeholder="Describe the room type"
            />
          </div>
        </div>

        <div className="with-top-border">
          <div className="grid-two">
            <div>
              <h4 className="card-small-title">Room Type Amenities</h4>
              <div className="chip-grid">
                {currentAmenities.map((item) => (
                  <span className="amenity-chip selected" key={item.id}>
                    {item.amenity?.name || "Amenity"}
                    <button
                      type="button"
                      className="chip-remove"
                      onClick={() => handleDeleteAmenity(item.id)}
                    >
                      ×
                    </button>
                  </span>
                ))}
                {!currentAmenities.length ? (
                  <div className="empty-panel">
                    Save or select a room type, then add amenities.
                  </div>
                ) : null}
              </div>
            </div>

            <div className="inline-form">
              <div className="form-group">
                <label>Amenity Name</label>
                <input
                  type="text"
                  name="name"
                  value={amenityForm.name}
                  onChange={handleAmenityFormChange}
                  placeholder="Wi-Fi"
                />
              </div>

              <div className="form-group">
                <label>Category</label>
                <input
                  type="text"
                  name="category"
                  value={amenityForm.category}
                  onChange={handleAmenityFormChange}
                  placeholder="Room"
                />
              </div>

              <button
                type="button"
                className="btn btn-secondary"
                onClick={handleAddAmenity}
                disabled={amenitySaving || !form.id}
              >
                {amenitySaving ? "Adding..." : "Add Amenity"}
              </button>
            </div>
          </div>
        </div>

        <div className="action-bar with-top-border">
          <button className="btn btn-light" type="button" onClick={resetForm}>
            Reset
          </button>
          <button
            className="btn btn-primary"
            type="button"
            onClick={handleSaveRoomType}
            disabled={saving}
          >
            {saving ? "Saving..." : form.id ? "Update Room Type" : "Save Room Type"}
          </button>
        </div>
      </InfoSection>

      {loading ? <div className="empty-panel">Loading room types...</div> : null}
    </DashboardLayout>
  );
}

export default RoomTypes;