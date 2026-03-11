import { useEffect, useMemo, useState } from "react";
import DashboardLayout from "../components/layout/DashboardLayout";
import InfoSection from "../components/seller/InfoSection";
import {
  addPropertyAmenity,
  createHotel,
  deletePropertyAmenity,
  getHotelPhotos,
  getMyHotel,
  getPropertyAmenities,
  updateHotel,
  uploadHotelPhotosBulk,
} from "../api/hotelApi";
import "../styles/sellerProfile.css";

const emptyHotelForm = {
  property_name: "",
  email: "",
  contact_number: "",
  address: "",
  city: "",
  country: "",
  timezone: "",
};

const emptyAmenityForm = {
  name: "",
  category: "",
};

const statusLabel = (value) => {
  if (!value) return "Draft";
  return value.replaceAll("_", " ").replace(/\b\w/g, (char) => char.toUpperCase());
};

const statusTone = (value) => {
  if (value === "approved" || value === "published") return "success";
  if (value === "changes_requested") return "warning";
  if (value === "rejected" || value === "suspended") return "danger";
  return "info";
};

const toImageUrl = (url) => {
  if (!url) return "";
  if (url.startsWith("http://") || url.startsWith("https://")) return url;
  return `http://127.0.0.1:8000${url}`;
};

function MyHotel() {
  const [hotel, setHotel] = useState(null);
  const [form, setForm] = useState(emptyHotelForm);
  const [amenityForm, setAmenityForm] = useState(emptyAmenityForm);
  const [amenities, setAmenities] = useState([]);
  const [photos, setPhotos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [amenitySaving, setAmenitySaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const hasHotel = Boolean(hotel?.id);

  const resetHotelState = () => {
    setHotel(null);
    setForm(emptyHotelForm);
    setAmenities([]);
    setPhotos([]);
  };

  const fillFormFromHotel = (hotelData) => {
    setForm({
      property_name: hotelData?.property_name || "",
      email: hotelData?.email || "",
      contact_number: hotelData?.contact_number || "",
      address: hotelData?.address || "",
      city: hotelData?.city || "",
      country: hotelData?.country || "",
      timezone: hotelData?.timezone || "",
    });
  };

  const loadHotel = async () => {
    try {
      setLoading(true);
      setError("");
      setSuccess("");

      const currentHotel = await getMyHotel();

      if (!currentHotel) {
        resetHotelState();
        return;
      }

      setHotel(currentHotel);
      fillFormFromHotel(currentHotel);
      setPhotos(Array.isArray(currentHotel.photos) ? currentHotel.photos : []);

      try {
        const amenityData = await getPropertyAmenities(currentHotel.id);
        setAmenities(Array.isArray(amenityData) ? amenityData : []);
      } catch {
        setAmenities([]);
      }

      try {
        const photoData = await getHotelPhotos(currentHotel.id);
        setPhotos(Array.isArray(photoData) ? photoData : []);
      } catch {
        setPhotos(Array.isArray(currentHotel.photos) ? currentHotel.photos : []);
      }
    } catch (err) {
      resetHotelState();
      setError(err.message || "Failed to load hotel.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHotel();
  }, []);

  const checklist = useMemo(() => {
    return [
      { label: "Property name added", done: !!form.property_name.trim() },
      { label: "Contact email added", done: !!form.email.trim() },
      { label: "Contact number added", done: !!form.contact_number.trim() },
      { label: "Address added", done: !!form.address.trim() },
      { label: "Location completed", done: !!form.city.trim() && !!form.country.trim() },
      { label: "Timezone configured", done: !!form.timezone.trim() },
      { label: "Amenities assigned", done: amenities.length > 0 },
      { label: "Photos uploaded", done: photos.length > 0 },
    ];
  }, [form, amenities, photos]);

  const readiness = Math.round(
    (checklist.filter((item) => item.done).length / checklist.length) * 100
  );

  const stats = [
    {
      label: "Listing Status",
      value: hasHotel ? statusLabel(hotel?.status) : "No Hotel",
      helper: hasHotel
        ? "Seller can view this status but cannot change it"
        : "Create your hotel first",
      badge: hasHotel ? statusLabel(hotel?.status) : "Empty",
      tone: hasHotel ? statusTone(hotel?.status) : "neutral",
    },
    {
      label: "Property Amenities",
      value: String(amenities.length),
      helper: hasHotel ? "Amenities linked to this property" : "No property created yet",
    },
    {
      label: "Media Coverage",
      value: `${photos.length} Photos`,
      helper: hasHotel ? "Images uploaded for the property" : "No photos uploaded yet",
    },
  ];

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleAmenityFormChange = (e) => {
    const { name, value } = e.target;
    setAmenityForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSaveHotel = async () => {
    try {
      setSaving(true);
      setError("");
      setSuccess("");

      const payload = {
        property_name: form.property_name.trim(),
        email: form.email.trim(),
        contact_number: form.contact_number.trim(),
        address: form.address.trim(),
        city: form.city.trim(),
        country: form.country.trim(),
        timezone: form.timezone.trim(),
      };

      if (hasHotel) {
        await updateHotel(hotel.id, payload);
        setSuccess("Hotel updated successfully.");
      } else {
        await createHotel(payload);
        setSuccess("Hotel created successfully.");
      }

      await loadHotel();
    } catch (err) {
      setError(err.message || "Failed to save hotel.");
    } finally {
      setSaving(false);
    }
  };

  const handleUploadPhotos = async (e) => {
    const files = e.target.files;
    if (!files?.length || !hotel?.id) return;

    try {
      setUploading(true);
      setError("");
      setSuccess("");

      await uploadHotelPhotosBulk(hotel.id, files);
      setSuccess("Property photos uploaded successfully.");
      await loadHotel();
    } catch (err) {
      setError(err.message || "Failed to upload photos.");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const handleAddAmenity = async () => {
    if (!hotel?.id) {
      setError("Create hotel first.");
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

      await addPropertyAmenity(hotel.id, {
        name: amenityForm.name.trim(),
        category: amenityForm.category.trim(),
      });

      setAmenityForm(emptyAmenityForm);
      setSuccess("Property amenity added.");
      await loadHotel();
    } catch (err) {
      setError(err.message || "Failed to add property amenity.");
    } finally {
      setAmenitySaving(false);
    }
  };

  const handleDeleteAmenity = async (amenityLinkId) => {
    if (!hotel?.id) return;

    try {
      setError("");
      setSuccess("");

      await deletePropertyAmenity(hotel.id, amenityLinkId);
      setSuccess("Property amenity removed.");
      await loadHotel();
    } catch (err) {
      setError(err.message || "Failed to remove property amenity.");
    }
  };

  return (
    <DashboardLayout
      title="My Hotel"
      subtitle="Manage property details, amenities, photos and listing readiness."
      actions={
        <>
          <button className="btn btn-light" type="button" onClick={loadHotel}>
            Refresh
          </button>

          <button
            className="btn btn-primary"
            type="button"
            onClick={handleSaveHotel}
            disabled={saving}
          >
            {saving ? "Saving..." : hasHotel ? "Update Hotel" : "Create Hotel"}
          </button>
        </>
      }
    >
      {error ? <div className="status-message error">{error}</div> : null}
      {success ? <div className="status-message success">{success}</div> : null}

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

      {!hasHotel && !loading ? (
        <div className="empty-panel" style={{ marginBottom: "22px" }}>
          <p style={{ marginBottom: "12px" }}>No hotel found for this seller.</p>
          <button className="btn btn-primary" type="button" onClick={handleSaveHotel}>
            {saving ? "Creating..." : "Create Hotel"}
          </button>
        </div>
      ) : null}

      <div className="hotel-layout">
        <div className="hotel-main">
          <InfoSection title="Property Details">
            <div className="form-grid">
              <div className="form-group">
                <label>Property Name</label>
                <input
                  type="text"
                  name="property_name"
                  value={form.property_name}
                  onChange={handleFormChange}
                  placeholder="Enter property name"
                />
              </div>

              <div className="form-group">
                <label>Status</label>
                <input
                  type="text"
                  value={hasHotel ? statusLabel(hotel?.status) : ""}
                  disabled
                  placeholder="Status will appear after property is created"
                />
                <span className="field-helper">Read-only for seller</span>
              </div>

              <div className="form-group">
                <label>Contact Email</label>
                <input
                  type="email"
                  name="email"
                  value={form.email}
                  onChange={handleFormChange}
                  placeholder="hotel@example.com"
                />
              </div>

              <div className="form-group">
                <label>Contact Number</label>
                <input
                  type="text"
                  name="contact_number"
                  value={form.contact_number}
                  onChange={handleFormChange}
                  placeholder="+97798XXXXXXXX"
                />
              </div>
            </div>
          </InfoSection>

          <InfoSection title="Location">
            <div className="form-grid">
              <div className="form-group form-group-full">
                <label>Address</label>
                <input
                  type="text"
                  name="address"
                  value={form.address}
                  onChange={handleFormChange}
                  placeholder="Street / area / landmark"
                />
              </div>

              <div className="form-group">
                <label>City</label>
                <input
                  type="text"
                  name="city"
                  value={form.city}
                  onChange={handleFormChange}
                  placeholder="City"
                />
              </div>

              <div className="form-group">
                <label>Country</label>
                <input
                  type="text"
                  name="country"
                  value={form.country}
                  onChange={handleFormChange}
                  placeholder="Country"
                />
              </div>

              <div className="form-group">
                <label>Timezone</label>
                <input
                  type="text"
                  name="timezone"
                  value={form.timezone}
                  onChange={handleFormChange}
                  placeholder="Asia/Kathmandu"
                />
              </div>
            </div>
          </InfoSection>

          <InfoSection title="Property Amenities">
            {hasHotel ? (
              <div className="grid-two">
                <div>
                  <div className="chip-grid">
                    {amenities.map((item) => (
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
                    {!amenities.length ? (
                      <div className="empty-panel">No amenities added yet.</div>
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
                      placeholder="Free Wi-Fi"
                    />
                  </div>

                  <div className="form-group">
                    <label>Category</label>
                    <input
                      type="text"
                      name="category"
                      value={amenityForm.category}
                      onChange={handleAmenityFormChange}
                      placeholder="General"
                    />
                  </div>

                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={handleAddAmenity}
                    disabled={amenitySaving}
                  >
                    {amenitySaving ? "Adding..." : "Add Amenity"}
                  </button>
                </div>
              </div>
            ) : (
              <div className="empty-panel">
                Create the hotel first, then you can add amenities.
              </div>
            )}
          </InfoSection>

          <InfoSection title="Property Gallery">
            {hasHotel ? (
              <div className="upload-grid">
                {photos.map((photo, index) => (
                  <div className="upload-card" key={photo.id}>
                    <img
                      className="gallery-image"
                      src={toImageUrl(photo.image)}
                      alt={`Property ${index + 1}`}
                    />
                    <strong>Photo {index + 1}</strong>
                    <span>Sort order: {photo.sort_order}</span>
                  </div>
                ))}

                <label className="upload-card upload-card-add">
                  <div className="upload-visual upload-visual-dashed">
                    <span className="material-symbols-outlined">add_photo_alternate</span>
                  </div>
                  <strong>{uploading ? "Uploading..." : "Add Property Photos"}</strong>
                  <span>Choose one or more files</span>
                  <input
                    className="hidden-file-input"
                    type="file"
                    accept="image/*"
                    multiple
                    onChange={handleUploadPhotos}
                    disabled={uploading}
                  />
                </label>

                {!photos.length ? (
                  <div className="empty-panel">No property photos uploaded yet.</div>
                ) : null}
              </div>
            ) : (
              <div className="empty-panel">
                Create the hotel first, then you can upload photos.
              </div>
            )}
          </InfoSection>
        </div>

        <aside className="hotel-side">
          <section className="card sticky-card">
            <div className="mini-panel-header">
              <h3>Listing Readiness</h3>
              <span className="status-pill success">{readiness}%</span>
            </div>

            <div className="checklist">
              {checklist.map((item) => (
                <div className="checklist-item" key={item.label}>
                  <span className="material-symbols-outlined">
                    {item.done ? "check_circle" : "radio_button_unchecked"}
                  </span>
                  <span>{item.label}</span>
                </div>
              ))}
            </div>
          </section>

          <section className="card">
            <div className="mini-panel-header">
              <h3>Review Notes</h3>
              <span className={`status-pill ${hasHotel ? statusTone(hotel?.status) : "neutral"}`}>
                {hasHotel ? statusLabel(hotel?.status) : "Empty"}
              </span>
            </div>

            <p className="muted-paragraph">
              {hasHotel
                ? "Update your hotel details, add amenities and upload photos here. Property status is controlled by admin or staff."
                : "No hotel exists for this seller yet. Fill the form and click Create Hotel."}
            </p>
          </section>
        </aside>
      </div>

      {loading ? <div className="empty-panel">Loading hotel data...</div> : null}
    </DashboardLayout>
  );
}

export default MyHotel;