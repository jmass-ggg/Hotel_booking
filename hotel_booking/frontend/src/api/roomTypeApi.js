import { apiRequest } from "./http";

const unwrapList = (payload) => {
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.results)) return payload.results;
  return [];
};

export const getRoomTypes = async (propertyId) => {
  const data = await apiRequest(`/room/${propertyId}/room-types/`);
  return unwrapList(data);
};

export const createRoomType = async (propertyId, payload) => {
  return apiRequest(`/room/${propertyId}/room-types/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
};

export const updateRoomType = async (propertyId, roomTypeId, payload) => {
  return apiRequest(`/room/${propertyId}/room-types/${roomTypeId}/`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
};

export const deleteRoomType = async (propertyId, roomTypeId) => {
  return apiRequest(`/room/${propertyId}/room-types/${roomTypeId}/`, {
    method: "DELETE",
  });
};

export const getRoomTypeAmenities = async (propertyId, roomTypeId) => {
  const data = await apiRequest(
    `/amenities/${propertyId}/room-types/${roomTypeId}/amenities/`
  );
  return unwrapList(data);
};

export const addRoomTypeAmenity = async (propertyId, roomTypeId, payload) => {
  return apiRequest(
    `/amenities/${propertyId}/room-types/${roomTypeId}/amenities/`,
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
};

export const deleteRoomTypeAmenity = async (
  propertyId,
  roomTypeId,
  amenityLinkId
) => {
  return apiRequest(
    `/amenities/${propertyId}/room-types/${roomTypeId}/amenities/${amenityLinkId}/`,
    {
      method: "DELETE",
    }
  );
};