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

function SellerRoles() {
  const [me, setMe] = useState(null);
  const [staffList, setStaffList] = useState([]);
  const [createForm, setCreateForm] = useState(emptyCreateForm);
  const [editingId, setEditingId] = useState(null);
  const [permissionForm, setPermissionForm] = useState({
    can_create: false,
    can_update: false,
    can_delete: false,
    can_view: false,
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [permissionSaving, setPermissionSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const isSeller = me?.role === "SELLER";

  const loadData = async () => {
    try {
      setLoading(true);
      setError("");

      const meData = await getMe();
      setMe(meData);

      if (meData?.role !== "SELLER") {
        setStaffList([]);
        return;
      }

      const staffData = await getSellerStaff();
      setStaffList(Array.isArray(staffData) ? staffData : []);
    } catch (err) {
      setError(err?.message || "Failed to load seller staff.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const stats = useMemo(() => {
    const total = staffList.length;
    const createCount = staffList.filter((item) => item.can_create).length;
    const updateCount = staffList.filter((item) => item.can_update).length;
    const deleteCount = staffList.filter((item) => item.can_delete).length;

    return [
      {
        label: "Total Staff",
        value: String(total),
        helper: "Seller staff accounts under your profile",
      },
      {
        label: "Create Access",
        value: String(createCount),
        helper: "Staff who can create records",
      },
      {
        label: "Delete Access",
        value: String(deleteCount),
        helper: "Staff who can delete records",
      },
    ];
  }, [staffList]);

  const handleCreateFormChange = (e) => {
    const { name, value, type, checked } = e.target;
    setCreateForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handlePermissionFormChange = (e) => {
    const { name, checked } = e.target;
    setPermissionForm((prev) => ({
      ...prev,
      [name]: checked,
    }));
  };

  const resetCreateForm = () => {
    setCreateForm(emptyCreateForm);
    setError("");
    setSuccess("");
  };

  const openPermissionEditor = (staff) => {
    setEditingId(staff.id);
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
    setEditingId(null);
    setPermissionForm({
      can_create: false,
      can_update: false,
      can_delete: false,
      can_view: false,
    });
  };

  const handleCreateStaff = async () => {
    if (!createForm.username.trim() || !createForm.email.trim() || !createForm.password.trim()) {
      setError("Username, email and password are required.");
      return;
    }

    try {
      setSaving(true);
      setError("");
      setSuccess("");

      await createSellerStaff({
        username: createForm.username.trim(),
        email: createForm.email.trim(),
        password: createForm.password,
        can_create: createForm.can_create,
        can_update: createForm.can_update,
        can_delete: createForm.can_delete,
        can_view: createForm.can_view,
      });

      setSuccess("Seller staff created successfully.");
      resetCreateForm();
      await loadData();
    } catch (err) {
      setError(err?.message || "Failed to create seller staff.");
    } finally {
      setSaving(false);
    }
  };

  const handleUpdatePermissions = async () => {
    if (!editingId) return;

    try {
      setPermissionSaving(true);
      setError("");
      setSuccess("");

      await updateSellerStaffPermissions(editingId, permissionForm);

      setSuccess("Staff permissions updated successfully.");
      closePermissionEditor();
      await loadData();
    } catch (err) {
      setError(err?.message || "Failed to update permissions.");
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

      if (editingId === staffId) {
        closePermissionEditor();
      }

      await loadData();
    } catch (err) {
      setError(err?.message || "Failed to delete seller staff.");
    }
  };

  return (
    <DashboardLayout
      title="Seller Staff"
      subtitle="Create staff accounts and manage their permissions."
      actions={
        <>
          <button className="btn btn-light" type="button" onClick={resetCreateForm}>
            Reset Form
          </button>
          <button
            className="btn btn-primary"
            type="button"
            onClick={handleCreateStaff}
            disabled={saving || !isSeller}
          >
            {saving ? "Creating..." : "Create Staff"}
          </button>
        </>
      }
    >
      {error ? <div className="status-message error">{error}</div> : null}
      {success ? <div className="status-message success">{success}</div> : null}

      {!loading && !isSeller ? (
        <div className="empty-panel">
          This page is only available for users whose role is <strong>SELLER</strong>.
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

      <InfoSection title="Create Seller Staff">
        <div className="form-grid">
          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              name="username"
              value={createForm.username}
              onChange={handleCreateFormChange}
              placeholder="staff_user"
              disabled={!isSeller}
            />
          </div>

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              name="email"
              value={createForm.email}
              onChange={handleCreateFormChange}
              placeholder="staff@example.com"
              disabled={!isSeller}
            />
          </div>

          <div className="form-group form-group-full">
            <label>Password</label>
            <input
              type="password"
              name="password"
              value={createForm.password}
              onChange={handleCreateFormChange}
              placeholder="Minimum 6 characters"
              disabled={!isSeller}
            />
          </div>

          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="can_create"
                checked={createForm.can_create}
                onChange={handleCreateFormChange}
                disabled={!isSeller}
              />{" "}
              Can Create
            </label>
          </div>

          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="can_update"
                checked={createForm.can_update}
                onChange={handleCreateFormChange}
                disabled={!isSeller}
              />{" "}
              Can Update
            </label>
          </div>

          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="can_delete"
                checked={createForm.can_delete}
                onChange={handleCreateFormChange}
                disabled={!isSeller}
              />{" "}
              Can Delete
            </label>
          </div>

          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="can_view"
                checked={createForm.can_view}
                onChange={handleCreateFormChange}
                disabled={!isSeller}
              />{" "}
              Can View
            </label>
          </div>
        </div>

        <div className="action-bar with-top-border">
          <button className="btn btn-light" type="button" onClick={resetCreateForm}>
            Reset
          </button>
          <button
            className="btn btn-primary"
            type="button"
            onClick={handleCreateStaff}
            disabled={saving || !isSeller}
          >
            {saving ? "Creating..." : "Create Staff"}
          </button>
        </div>
      </InfoSection>

      <section className="card table-card">
        <div className="table-toolbar">
          <div>
            <span className="eyebrow">Seller Staff</span>
            <h3>Manage Staff Accounts</h3>
            <p>View all staff created under the logged-in seller.</p>
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
                  <td>
                    <span className={`status-pill ${staff.can_view ? "success" : "neutral"}`}>
                      {staff.can_view ? "Yes" : "No"}
                    </span>
                  </td>
                  <td>
                    <span className={`status-pill ${staff.can_create ? "success" : "neutral"}`}>
                      {staff.can_create ? "Yes" : "No"}
                    </span>
                  </td>
                  <td>
                    <span className={`status-pill ${staff.can_update ? "success" : "neutral"}`}>
                      {staff.can_update ? "Yes" : "No"}
                    </span>
                  </td>
                  <td>
                    <span className={`status-pill ${staff.can_delete ? "danger" : "neutral"}`}>
                      {staff.can_delete ? "Yes" : "No"}
                    </span>
                  </td>
                  <td className="table-actions">
                    <button
                      className="table-link"
                      type="button"
                      onClick={() => openPermissionEditor(staff)}
                    >
                      Edit Permissions
                    </button>
                    <button
                      className="table-link table-link-danger"
                      type="button"
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

      {editingId ? (
        <InfoSection title="Edit Staff Permissions">
          <div className="form-grid">
            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="can_view"
                  checked={permissionForm.can_view}
                  onChange={handlePermissionFormChange}
                />{" "}
                Can View
              </label>
            </div>

            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="can_create"
                  checked={permissionForm.can_create}
                  onChange={handlePermissionFormChange}
                />{" "}
                Can Create
              </label>
            </div>

            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="can_update"
                  checked={permissionForm.can_update}
                  onChange={handlePermissionFormChange}
                />{" "}
                Can Update
              </label>
            </div>

            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="can_delete"
                  checked={permissionForm.can_delete}
                  onChange={handlePermissionFormChange}
                />{" "}
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
              onClick={handleUpdatePermissions}
              disabled={permissionSaving}
            >
              {permissionSaving ? "Saving..." : "Save Permissions"}
            </button>
          </div>
        </InfoSection>
      ) : null}

      {loading ? <div className="empty-panel">Loading seller staff...</div> : null}
    </DashboardLayout>
  );
}

export default SellerRoles;