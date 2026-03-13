import { apiRequest } from "./http";

export async function getSellerStaff() {
  return apiRequest("/seller-staff/");
}

export async function createSellerStaff(payload) {
  return apiRequest("/seller-staff/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateSellerStaffPermissions(staffId, payload) {
  return apiRequest(`/seller-staff/${staffId}/permissions/`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function deleteSellerStaff(staffId) {
  return apiRequest(`/seller-staff/${staffId}/`, {
    method: "DELETE",
  });
}