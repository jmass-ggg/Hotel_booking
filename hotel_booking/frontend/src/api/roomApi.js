import { apiRequest } from "./http";

const ROOM_BASE = "/room";

const unwrapList = (payload) => {
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.results)) return payload.results;
  return [];
};

export async function getRooms(propertyId) {
  const data = await apiRequest(`${ROOM_BASE}/${propertyId}/rooms/`, {
    method: "GET",
  });

  return unwrapList(data);
}

export async function createRoom(propertyId, payload) {
  return apiRequest(`${ROOM_BASE}/${propertyId}/rooms/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateRoom(propertyId, roomId, payload) {
  return apiRequest(`${ROOM_BASE}/${propertyId}/rooms/${roomId}/`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function deleteRoom(propertyId, roomId) {
  return apiRequest(`${ROOM_BASE}/${propertyId}/rooms/${roomId}/`, {
    method: "DELETE",
  });
}

export async function uploadRoomPhoto(propertyId, roomId, file, sortOrder = 0) {
  const formData = new FormData();
  formData.append("image", file);
  formData.append("sort_order", sortOrder);

  return apiRequest(`/hotels/${propertyId}/rooms/${roomId}/photos/`, {
    method: "POST",
    body: formData,
  });
}