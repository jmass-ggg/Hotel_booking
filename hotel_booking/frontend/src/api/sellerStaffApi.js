import http from "./http";

export async function getSellerStaff() {
  const { data } = await http.get("/seller-staff/");
  return data;
}

export async function createSellerStaff(payload) {
  const { data } = await http.post("/seller-staff/", payload);
  return data;
}

export async function updateSellerStaffPermissions(staffId, payload) {
  const { data } = await http.patch(`/seller-staff/${staffId}/permissions/`, payload);
  return data;
}

export async function deleteSellerStaff(staffId) {
  const { data } = await http.delete(`/seller-staff/${staffId}/`);
  return data;
}