import { apiRequest } from "./http";

const HOTEL_BASE = "/hotels";
const AMENITY_BASE = "/amenities";

const unwrapList = (payload) => {
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.results)) return payload.results;
  return [];
};

export async function getHotels() {
  const data = await apiRequest(`${HOTEL_BASE}/`);
  return unwrapList(data);
}

export async function getMyHotel() {
  return apiRequest(`${HOTEL_BASE}/my/`, {
    method: "GET",
  });
}

export async function createHotel(payload) {
  return apiRequest(`${HOTEL_BASE}/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateHotel(hotelId, payload) {
  return apiRequest(`${HOTEL_BASE}/${hotelId}/`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

/* -----------------------------
   PROPERTY AMENITIES
-------------------------------- */

export async function getPropertyAmenities(propertyId) {
  const data = await apiRequest(`${AMENITY_BASE}/${propertyId}/amenities/`, {
    method: "GET",
  });

  return unwrapList(data);
}

export async function addPropertyAmenity(propertyId, payload) {
  return apiRequest(`${AMENITY_BASE}/${propertyId}/amenities/`, {
    method: "POST",
    body: JSON.stringify({
      amenity: {
        name: payload.name,
        category: payload.category || "",
      },
    }),
  });
}

export async function deletePropertyAmenity(propertyId, amenityLinkId) {
  return apiRequest(
    `${AMENITY_BASE}/${propertyId}/amenities/${amenityLinkId}/`,
    {
      method: "DELETE",
    }
  );
}

/* -----------------------------
   PROPERTY PHOTOS
-------------------------------- */

export async function getHotelPhotos(hotelId) {
  const data = await apiRequest(`${HOTEL_BASE}/${hotelId}/photos/`, {
    method: "GET",
  });

  return unwrapList(data);
}

export async function uploadHotelPhotosBulk(hotelId, files) {
  const formData = new FormData();

  Array.from(files).forEach((file) => {
    formData.append("images", file);
  });

  return apiRequest(`${HOTEL_BASE}/${hotelId}/photos/bulk/`, {
    method: "POST",
    body: formData,
  });
}