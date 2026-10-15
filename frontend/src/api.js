async function request(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(typeof detail.detail === "string" ? detail.detail : `Request failed (${res.status})`);
  }
  return res.status === 204 ? null : res.json();
}

export const api = {
  list: (status) => request(`/api/tickets${status && status !== "all" ? `?status=${status}` : ""}`),
  stats: () => request("/api/tickets/stats"),
  create: (data) => request("/api/tickets", { method: "POST", body: JSON.stringify(data) }),
  update: (id, data) => request(`/api/tickets/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  remove: (id) => request(`/api/tickets/${id}`, { method: "DELETE" }),
};
