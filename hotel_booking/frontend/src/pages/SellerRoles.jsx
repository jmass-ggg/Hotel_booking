import { useEffect, useMemo, useState } from "react";
import DashboardLayout from "../components/layout/DashboardLayout";
import InfoSection from "../components/seller/InfoSection";
import { getMe } from "../api/authApi";
import {
  createSellerStaff,
  deleteSellerStaff,
  getSellerStaff,
  updateSellerStaffPermissions,
} from "../api/sellerStaffApi";
import "../styles/sellerProfile.css";

const emptyCreateForm = {
  username: "",
  email: "",
  password: "",
  can_create: false,
  can_update: false,
  can_delete: false,
  can_view: true,
};

const emptyPermissionForm = {
  can_create: false,
  can_update: false,
  can_delete: false,
  can_view: false,
};

function SellerRoles() {
  const [user, setUser] = useState(null);
  const [staffList, setStaffList] = useState([]);
  const [form, setForm] = useState(emptyCreateForm);
  const [editingStaff, setEditingStaff] = useState(null);
  const [permissionForm, setPermissionForm] = useState(emptyPermissionForm);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [permissionSaving, setPermissionSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const loadData = async () => {
    try {
      setLoading(true);
      setError("");

      const me = await getMe();
      setUser(me);

      const staff = await getSellerStaff();
      setStaffList(Array.isArray(staff) ? staff : []);
    } catch (err) {
      setError(err.message || "Failed to load seller staff.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const stats = useMemo(() => {
    return [
      {
        label: "Total Staff",
        value: String(staffList.length),
        helper: "Staff members under this seller",
      },
      {
        label: "Can Create",
        value: String(staffList.filter((item) => item.can_create).length),
        helper: "Staff with create permission",
      },
      {
        label: "Can Delete",
        value: String(staffList.filter((item) => item.can_delete).length),
        helper: "Staff with delete permission",
      },
    ];
  }, [staffList]);

  const handleFormChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handlePermissionChange = (e) => {
    const { name, checked } = e.target;
    setPermissionForm((prev) => ({
      ...prev,
      [name]: checked,
    }));
  };

  const resetForm = () => {
    setForm(emptyCreateForm);
    setError("");
    setSuccess("");
  };

  const handleCreateStaff = async () => {
    if (!form.username.trim() || !form.email.trim() || !form.password.trim()) {
      setError("Username, email and password are required.");
      return;
    }

    try {
      setSaving(true);
      setError("");
      setSuccess("");

      await createSellerStaff({
        username: form.username.trim(),
        email: form.email.trim(),
        password: form.password,
        can_create: form.can_create,
        can_update: form.can_update,
        can_delete: form.can_delete,
        can_view: form.can_view,
      });

      setSuccess("Seller staff created successfully.");
      setForm(emptyCreateForm);
      await loadData();
    } catch (err) {
      setError(err.message || "Failed to create seller staff.");
    } finally {
      setSaving(false);
    }
  };

  const openPermissionEditor = (staff) => {
    setEditingStaff(staff);
    setPermissionForm({
      can_create: !!staff.can_create,
      can_update: !!staff.can_update,
      can_delete: !!staff.can_delete,
      can_view: !!staff.can_view,
    });
    setError("");
    setSuccess("");
  };

  const closePermissionEditor = () => {
    setEditingStaff(null);
    setPermissionForm(emptyPermissionForm);
  };

  const handleSavePermissions = async () => {
    if (!editingStaff?.id) return;

    try {
      setPermissionSaving(true);
      setError("");
      setSuccess("");

      await updateSellerStaffPermissions(editingStaff.id, permissionForm);

      setSuccess("Permissions updated successfully.");
      closePermissionEditor();
      await loadData();
    } catch (err) {
      setError(err.message || "Failed to update permissions.");
    } finally {
      setPermissionSaving(false);
    }
  };

  const handleDeleteStaff = async (staffId) => {
    try {
      setError("");
      setSuccess("");

      await deleteSellerStaff(staffId);
      setSuccess("Seller staff deleted successfully.");

      if (editingStaff?.id === staffId) {
        closePermissionEditor();
      }

      await loadData();
    } catch (err) {
      setError(err.message || "Failed to delete seller staff.");
    }
  };

  return (
    <DashboardLayout
      title="Seller Staff"
      subtitle="Create staff accounts and manage permission access."
      actions={
        <>
          <button className="btn btn-light" type="button" onClick={resetForm}>
            Reset
          </button>
          <button
            className="btn btn-primary"
            type="button"
            onClick={handleCreateStaff}
            disabled={saving}
          >
            {saving ? "Creating..." : "Create Staff"}
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
            </div>
            <h3>{item.value}</h3>
            <p>{item.helper}</p>
          </section>
        ))}
      </div>

      <InfoSection title="Create Seller Staff">
        <div className="form-grid">
          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              name="username"
              value={form.username}
              onChange={handleFormChange}
              placeholder="staff_username"
            />
          </div>

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              name="email"
              value={form.email}
              onChange={handleFormChange}
              placeholder="staff@example.com"
            />
          </div>

          <div className="form-group form-group-full">
            <label>Password</label>
            <input
              type="password"
              name="password"
              value={form.password}
              onChange={handleFormChange}
              placeholder="Enter password"
            />
          </div>

          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="can_view"
                checked={form.can_view}
                onChange={handleFormChange}
              />
              Can View
            </label>
          </div>

          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="can_create"
                checked={form.can_create}
                onChange={handleFormChange}
              />
              Can Create
            </label>
          </div>

          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="can_update"
                checked={form.can_update}
                onChange={handleFormChange}
              />
              Can Update
            </label>
          </div>

          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="can_delete"
                checked={form.can_delete}
                onChange={handleFormChange}
              />
              Can Delete
            </label>
          </div>
        </div>

        <div className="action-bar with-top-border">
          <button className="btn btn-light" type="button" onClick={resetForm}>
            Reset
          </button>
          <button
            className="btn btn-primary"
            type="button"
            onClick={handleCreateStaff}
            disabled={saving}
          >
            {saving ? "Creating..." : "Create Staff"}
          </button>
        </div>
      </InfoSection>

      <section className="card table-card">
        <div className="table-toolbar">
          <div>
            <span className="eyebrow">Staff List</span>
            <h3>Seller Staff Accounts</h3>
            <p>Manage the staff members created by this seller account.</p>
          </div>
        </div>

        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Username</th>
                <th>Email</th>
                <th>View</th>
                <th>Create</th>
                <th>Update</th>
                <th>Delete</th>
                <th className="table-actions">Actions</th>
              </tr>
            </thead>

            <tbody>
              {staffList.map((staff) => (
                <tr key={staff.id}>
                  <td>{staff.username}</td>
                  <td>{staff.email}</td>
                  <td>{staff.can_view ? "Yes" : "No"}</td>
                  <td>{staff.can_create ? "Yes" : "No"}</td>
                  <td>{staff.can_update ? "Yes" : "No"}</td>
                  <td>{staff.can_delete ? "Yes" : "No"}</td>
                  <td className="table-actions">
                    <button
                      type="button"
                      className="table-link"
                      onClick={() => openPermissionEditor(staff)}
                    >
                      Edit Permissions
                    </button>

                    <button
                      type="button"
                      className="table-link table-link-danger"
                      onClick={() => handleDeleteStaff(staff.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}

              {!staffList.length && !loading ? (
                <tr>
                  <td colSpan="7">
                    <div className="empty-panel">No seller staff found.</div>
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </section>

      {editingStaff ? (
        <InfoSection title={`Edit Permissions - ${editingStaff.username}`}>
          <div className="form-grid">
            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="can_view"
                  checked={permissionForm.can_view}
                  onChange={handlePermissionChange}
                />
                Can View
              </label>
            </div>

            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="can_create"
                  checked={permissionForm.can_create}
                  onChange={handlePermissionChange}
                />
                Can Create
              </label>
            </div>

            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="can_update"
                  checked={permissionForm.can_update}
                  onChange={handlePermissionChange}
                />
                Can Update
              </label>
            </div>

            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="can_delete"
                  checked={permissionForm.can_delete}
                  onChange={handlePermissionChange}
                />
                Can Delete
              </label>
            </div>
          </div>

          <div className="action-bar with-top-border">
            <button className="btn btn-light" type="button" onClick={closePermissionEditor}>
              Cancel
            </button>
            <button
              className="btn btn-primary"
              type="button"
              onClick={handleSavePermissions}
              disabled={permissionSaving}
            >
              {permissionSaving ? "Saving..." : "Save Permissions"}
            </button>
          </div>
        </InfoSection>
      ) : null}

      {loading ? <div className="empty-panel">Loading seller staff...</div> : null}

      {user?.role !== "SELLER" && !loading ? (
        <div className="empty-panel">
          Only users with role <strong>SELLER</strong> can access this page.
        </div>
      ) : null}
    </DashboardLayout>
  );
}

export default SellerRoles;