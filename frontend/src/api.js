const BASE = "/api";

async function req(path, opts = {}) {
  const res = await fetch(BASE + path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${res.status}: ${text}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  listEmployees: () => req("/employees"),
  createEmployee: (data) => req("/employees", { method: "POST", body: JSON.stringify(data) }),
  deleteEmployee: (name) => req(`/employees/${encodeURIComponent(name)}`, { method: "DELETE" }),

  listViolations: (filters = {}) => {
    const qs = new URLSearchParams(
      Object.entries(filters).filter(([, v]) => v !== undefined && v !== null && v !== "")
    ).toString();
    return req(`/violations${qs ? `?${qs}` : ""}`);
  },
  createViolation: (data) => req("/violations", { method: "POST", body: JSON.stringify(data) }),
  deleteViolation: (id) => req(`/violations/${id}`, { method: "DELETE" }),
  previewPenalty: (employee_name, category, incident) => {
    const qs = new URLSearchParams({ employee_name, category, incident }).toString();
    return req(`/violations/preview?${qs}`);
  },

  dashboard: () => req("/stats/dashboard"),
  matrix: () => req("/matrix"),

  exportViolationsUrl: (filters = {}) => {
    const qs = new URLSearchParams(
      Object.entries(filters).filter(([, v]) => v !== undefined && v !== null && v !== "")
    ).toString();
    return `${BASE}/violations/export${qs ? `?${qs}` : ""}`;
  },
};
