import { useEffect, useMemo, useState } from "react";
import DashboardLayout from "../components/layout/DashboardLayout";
import InfoSection from "../components/seller/InfoSection";
import { getMyHotel } from "../api/hotelApi";
import {
  createRoom,
  deleteRoom,
  getRooms,
  uploadRoomPhoto,
  updateRoom,
} from "../api/roomApi";
import { getRoomTypes } from "../api/roomTypeApi";
import "../styles/sellerProfile.css";

const emptyRoomForm = {
  id: null,
  room_number: "",
  floor: "",
  room_type: "",
  price: "",
  status: "active",
};

const toImageUrl = (url) => {
  if (!url) return "";
  if (url.startsWith("http://") || url.startsWith("https://")) return url;
  return `http://127.0.0.1:8000${url}`;
};

function Rooms() {
  const [hotel, setHotel] = useState(null);
  const [roomTypes, setRoomTypes] = useState([]);
  const [rooms, setRooms] = useState([]);
  const [form, setForm] = useState(emptyRoomForm);
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const loadData = async () => {
    try {
      setLoading(true);
      setError("");
      setSuccess("");

      const currentHotel = await getMyHotel();
      setHotel(currentHotel);

      if (!currentHotel?.id) {
        setRoomTypes([]);
        setRooms([]);
        return;
      }

      const [roomTypeData, roomData] = await Promise.all([
        getRoomTypes(currentHotel.id),
        getRooms(currentHotel.id),
      ]);

      setRoomTypes(Array.isArray(roomTypeData) ? roomTypeData : []);
      setRooms(Array.isArray(roomData) ? roomData : []);
    } catch (err) {
      setError(err.message || "Failed to load rooms.");
      setRoomTypes([]);
      setRooms([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const roomTypeMap = useMemo(() => {
    return roomTypes.reduce((acc, item) => {
      acc[item.id] = item.name;
      return acc;
    }, {});
  }, [roomTypes]);

  const filteredRooms = useMemo(() => {
    if (filter === "all") return rooms;
    return rooms.filter((room) => room.status === filter);
  }, [rooms, filter]);

  const currentRoom = useMemo(() => {
    return rooms.find((item) => item.id === form.id) || null;
  }, [rooms, form.id]);

  const stats = useMemo(() => {
    const activeCount = rooms.filter((item) => item.status === "active").length;
    const outOfOrderCount = rooms.filter(
      (item) => item.status === "out_of_order"
    ).length;

    return [
      {
        label: "Total Rooms",
        value: String(rooms.length),
        helper: "Inventory linked to this property",
      },
      {
        label: "Active Rooms",
        value: String(activeCount),
        helper: "Available to sell",
        badge: activeCount ? "Healthy" : null,
        tone: "success",
      },
      {
        label: "Out of Order",
        value: String(outOfOrderCount),
        helper: "Temporarily unavailable",
        badge: outOfOrderCount ? "Needs follow-up" : null,
        tone: "warning",
      },
    ];
  }, [rooms]);

  const resetForm = () => {
    setForm(emptyRoomForm);
    setError("");
    setSuccess("");
  };

  const fillForm = (room) => {
    setForm({
      id: room.id,
      room_number: room.room_number || "",
      floor: room.floor ?? "",
      room_type: room.room_type || "",
      price: room.price || "",
      status: room.status || "active",
    });
    setError("");
    setSuccess("");
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSaveRoom = async () => {
    if (!hotel?.id) {
      setError("Create hotel first.");
      return;
    }

    try {
      setSaving(true);
      setError("");
      setSuccess("");

      const payload = {
        room_type: form.room_type,
        room_number: form.room_number.trim(),
        floor: form.floor === "" ? null : Number(form.floor),
        price: form.price,
        status: form.status,
      };

      if (form.id) {
        await updateRoom(hotel.id, form.id, payload);
        setSuccess("Room updated successfully.");
      } else {
        await createRoom(hotel.id, payload);
        setSuccess("Room created successfully.");
        setForm(emptyRoomForm);
      }

      await loadData();
    } catch (err) {
      setError(err.message || "Failed to save room.");
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteRoom = async (roomId) => {
    if (!hotel?.id) return;

    try {
      setError("");
      setSuccess("");

      await deleteRoom(hotel.id, roomId);

      if (form.id === roomId) {
        setForm(emptyRoomForm);
      }

      setSuccess("Room deleted.");
      await loadData();
    } catch (err) {
      setError(err.message || "Failed to delete room.");
    }
  };

  const handleUploadPhoto = async (e) => {
    const file = e.target.files?.[0];
    if (!file || !hotel?.id || !currentRoom?.id) return;

    try {
      setUploading(true);
      setError("");
      setSuccess("");

      await uploadRoomPhoto(
        hotel.id,
        currentRoom.id,
        file,
        currentRoom.photos?.length || 0
      );

      setSuccess("Room photo uploaded successfully.");
      await loadData();
    } catch (err) {
      setError(err.message || "Failed to upload room photo.");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  return (
    <DashboardLayout
      title="Rooms"
      subtitle="Manage room inventory, room type mapping, status and photos."
      actions={
        <>
          <button className="btn btn-light" type="button" onClick={resetForm}>
            New Room
          </button>
          <button
            className="btn btn-primary"
            type="button"
            onClick={handleSaveRoom}
            disabled={saving}
          >
            {saving ? "Saving..." : form.id ? "Update Room" : "Add Room"}
          </button>
        </>
      }
    >
      {error ? <div className="status-message error">{error}</div> : null}
      {success ? <div className="status-message success">{success}</div> : null}

      {!hotel?.id && !loading ? (
        <div className="empty-panel">
          Create your hotel first before creating rooms.
        </div>
      ) : null}

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
            <p>Track room number, floor, room type, price and status.</p>
          </div>

          <div className="toolbar-chips">
            <button
              type="button"
              className={`filter-chip ${filter === "all" ? "active" : ""}`}
              onClick={() => setFilter("all")}
            >
              All
            </button>
            <button
              type="button"
              className={`filter-chip ${filter === "active" ? "active" : ""}`}
              onClick={() => setFilter("active")}
            >
              Active
            </button>
            <button
              type="button"
              className={`filter-chip ${filter === "out_of_order" ? "active" : ""}`}
              onClick={() => setFilter("out_of_order")}
            >
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
              {filteredRooms.map((room) => (
                <tr key={room.id}>
                  <td>{room.room_number}</td>
                  <td>{room.floor ?? "-"}</td>
                  <td>{roomTypeMap[room.room_type] || "Unknown"}</td>
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
                    <button
                      type="button"
                      className="table-link"
                      onClick={() => fillForm(room)}
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      className="table-link table-link-danger"
                      onClick={() => handleDeleteRoom(room.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}

              {!filteredRooms.length ? (
                <tr>
                  <td colSpan="6">
                    <div className="empty-panel">No rooms found.</div>
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </section>

      <InfoSection title={form.id ? "Edit Room" : "Create Room"}>
        <div className="form-grid">
          <div className="form-group">
            <label>Room Number</label>
            <input
              type="text"
              name="room_number"
              value={form.room_number}
              onChange={handleFormChange}
              placeholder="101"
            />
          </div>

          <div className="form-group">
            <label>Floor</label>
            <input
              type="number"
              min="0"
              name="floor"
              value={form.floor}
              onChange={handleFormChange}
              placeholder="1"
            />
          </div>

          <div className="form-group">
            <label>Room Type</label>
            <select
              name="room_type"
              value={form.room_type}
              onChange={handleFormChange}
            >
              <option value="">Select room type</option>
              {roomTypes.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Price</label>
            <input
              type="text"
              name="price"
              value={form.price}
              onChange={handleFormChange}
              placeholder="20000"
            />
          </div>

          <div className="form-group form-group-full">
            <label>Status</label>
            <select
              name="status"
              value={form.status}
              onChange={handleFormChange}
            >
              <option value="active">Active</option>
              <option value="out_of_order">Out of Order</option>
            </select>
          </div>

          <div className="form-group form-group-full">
            <label>Room Photos</label>

            {currentRoom ? (
              <div className="upload-grid compact-upload">
                {(currentRoom.photos || []).map((photo, index) => (
                  <div className="upload-card" key={photo.id}>
                    <img
                      className="gallery-image"
                      src={toImageUrl(photo.image)}
                      alt={`Room ${index + 1}`}
                    />
                    <strong>Photo {index + 1}</strong>
                    <span>Sort order: {photo.sort_order}</span>
                  </div>
                ))}

                <label className="upload-card upload-card-add">
                  <div className="upload-visual upload-visual-dashed">
                    <span className="material-symbols-outlined">add_photo_alternate</span>
                  </div>
                  <strong>{uploading ? "Uploading..." : "Add Room Photo"}</strong>
                  <span>Choose an image file</span>
                  <input
                    className="hidden-file-input"
                    type="file"
                    accept="image/*"
                    onChange={handleUploadPhoto}
                    disabled={uploading}
                  />
                </label>
              </div>
            ) : (
              <div className="empty-panel">
                Save the room first, then upload room photos.
              </div>
            )}
          </div>
        </div>

        <div className="action-bar with-top-border">
          <button className="btn btn-light" type="button" onClick={resetForm}>
            Cancel
          </button>
          <button
            className="btn btn-primary"
            type="button"
            onClick={handleSaveRoom}
            disabled={saving}
          >
            {saving ? "Saving..." : form.id ? "Update Room" : "Save Room"}
          </button>
        </div>
      </InfoSection>

      {loading ? <div className="empty-panel">Loading rooms...</div> : null}
    </DashboardLayout>
  );
}

export default Rooms;