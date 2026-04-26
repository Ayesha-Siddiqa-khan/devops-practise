const API_BASE = "/api";

async function http(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options
  });

  const data = await response.json();

  if (!response.ok) {
    const message = data?.message || "Request failed";
    throw new Error(message);
  }

  return data;
}

export const api = {
  products: () => http("/products"),
  productById: (id) => http(`/products/${id}`),
  cart: (userId) => http(`/cart/${userId}`),
  addToCart: (payload) =>
    http("/cart", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  updateCartItem: (itemId, quantity) =>
    http(`/cart/${itemId}`, {
      method: "PUT",
      body: JSON.stringify({ quantity })
    }),
  removeCartItem: (itemId) =>
    http(`/cart/${itemId}`, {
      method: "DELETE"
    }),
  placeOrder: (payload) =>
    http("/orders/place", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  clearCart: (userId) =>
    http(`/cart/user/${userId}`, {
      method: "DELETE"
    }),
  updateAddress: (userId, payload) =>
    http(`/users/${userId}/address`, {
      method: "PUT",
      body: JSON.stringify(payload)
    }),
  getAddress: (userId) => http(`/users/${userId}/address`)
};
