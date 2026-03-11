import { apiRequest } from "./http";

const unwrapList = (payload) => {
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.results)) return payload.results;
  return [];
};

export const getRooms = async (propertyId) => {
  const data = await apiRequest(`/room/${propertyId}/rooms/`);
  return unwrapList(data);
};

export const createRoom = async (propertyId, payload) => {
  return apiRequest(`/room/${propertyId}/rooms/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
};

export const updateRoom = async (propertyId, roomId, payload) => {
  return apiRequest(`/room/${propertyId}/rooms/${roomId}/`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
};

export const deleteRoom = async (propertyId, roomId) => {
  return apiRequest(`/room/${propertyId}/rooms/${roomId}/`, {
    method: "DELETE",
  });
};

export const getRoomPhotos = async (propertyId, roomId) => {
  const data = await apiRequest(`/room/${propertyId}/rooms/${roomId}/photos/`);
  return unwrapList(data);
};

export const uploadRoomPhoto = async (
  propertyId,
  roomId,
  file,
  sortOrder = 0
) => {
  const formData = new FormData();
  formData.append("image", file);
  formData.append("sort_order", String(sortOrder));

  return apiRequest(`/room/${propertyId}/rooms/${roomId}/photos/`, {
    method: "POST",
    body: formData,
  });
};