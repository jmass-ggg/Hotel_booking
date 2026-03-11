import { apiRequest, ApiError } from "./http";

const HOTEL_BASE = "/hotels";
const MY_HOTEL_ENDPOINT = `${HOTEL_BASE}/my-hotel/`;

// If your backend URLs are different, change only these endpoint strings.

export async function getHotels() {
  return apiRequest(`${HOTEL_BASE}/`);
}

export async function createHotel(payload) {
  return apiRequest(`${HOTEL_BASE}/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getMyHotel() {
  try {
    return await apiRequest(MY_HOTEL_ENDPOINT, {
      method: "GET",
    });
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      return null;
    }
    throw error;
  }
}

export async function updateHotel(hotelId, payload) {
  return apiRequest(`${HOTEL_BASE}/${hotelId}/`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function getPropertyAmenities(hotelId) {
  return apiRequest(`${HOTEL_BASE}/${hotelId}/amenities/`, {
    method: "GET",
  });
}

export async function addPropertyAmenity(hotelId, payload) {
  return apiRequest(`${HOTEL_BASE}/${hotelId}/amenities/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function deletePropertyAmenity(hotelId, amenityLinkId) {
  return apiRequest(`${HOTEL_BASE}/${hotelId}/amenities/${amenityLinkId}/`, {
    method: "DELETE",
  });
}

export async function getHotelPhotos(hotelId) {
  return apiRequest(`${HOTEL_BASE}/${hotelId}/photos/`, {
    method: "GET",
  });
}

export async function uploadHotelPhotosBulk(hotelId, files) {
  const formData = new FormData();

  Array.from(files).forEach((file) => {
    formData.append("images", file);
  });

  return apiRequest(`${HOTEL_BASE}/${hotelId}/photos/bulk-upload/`, {
    method: "POST",
    body: formData,
  });
}