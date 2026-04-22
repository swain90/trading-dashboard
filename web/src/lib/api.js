const API_URL = 'http://167.99.176.5:8090';
const API_KEY = import.meta.env.VITE_API_KEY || "";

async function request(path, params = {}) {
  const url = new URL(`${API_URL}${path}`);
  Object.entries(params).forEach(([k, v]) => {
    if (v != null) url.searchParams.set(k, v);
  });

  const res = await fetch(url, {
    headers: API_KEY ? { "X-API-Key": API_KEY } : {},
  });

  if (!res.ok) {
    throw new Error(`API ${res.status}: ${res.statusText}`);
  }
  return res.json();
}

export const api = {
  overview: () => request("/api/overview"),
  positions: (bot) => request("/api/positions", { bot }),
  signals: (limit = 50, bot) => request("/api/signals", { limit, bot }),
  trades: (days = 7, bot) => request("/api/trades", { days, bot }),
  health: () => request("/api/health"),
};
