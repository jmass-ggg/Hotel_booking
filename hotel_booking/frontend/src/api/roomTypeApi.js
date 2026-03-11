import { apiRequest } from "./http";

const ROOM_BASE = "/room";
const AMENITY_BASE = "/amenities";

const unwrapList = (payload) => {
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.results)) return payload.results;
  return [];
};

export async function getRoomTypes(propertyId) {
  const data = await apiRequest(`${ROOM_BASE}/${propertyId}/room-types/`, {
    method: "GET",
  });

  return unwrapList(data);
}

export async function createRoomType(propertyId, payload) {
  return apiRequest(`${ROOM_BASE}/${propertyId}/room-types/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateRoomType(propertyId, roomTypeId, payload) {
  return apiRequest(`${ROOM_BASE}/${propertyId}/room-types/${roomTypeId}/`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function deleteRoomType(propertyId, roomTypeId) {
  return apiRequest(`${ROOM_BASE}/${propertyId}/room-types/${roomTypeId}/`, {
    method: "DELETE",
  });
}

/* ---------------------------
ROOM TYPE AMENITIES
--------------------------- */

export async function getRoomTypeAmenities(propertyId, roomTypeId) {
  const data = await apiRequest(
    `${AMENITY_BASE}/${propertyId}/room-types/${roomTypeId}/amenities/`,
    {
      method: "GET",
    }
  );

  return unwrapList(data);
}

export async function addRoomTypeAmenity(propertyId, roomTypeId, payload) {
  return apiRequest(
    `${AMENITY_BASE}/${propertyId}/room-types/${roomTypeId}/amenities/`,
    {
      method: "POST",
      body: JSON.stringify({
        amenity: {
          name: payload.name,
          category: payload.category || "",
        },
      }),
    }
  );
}

export async function deleteRoomTypeAmenity(propertyId, roomTypeId, amenityId) {
  return apiRequest(
    `${AMENITY_BASE}/${propertyId}/room-types/${roomTypeId}/amenities/${amenityId}/`,
    {
      method: "DELETE",
    }
  );
}