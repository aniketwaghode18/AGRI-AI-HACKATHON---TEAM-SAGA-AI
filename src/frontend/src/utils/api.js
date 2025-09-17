const BASE = (import.meta && import.meta.env && import.meta.env.VITE_API_BASE) || 'http://localhost:5000';

async function request(path, { method = 'GET', body, isForm = false } = {}) {
  const headers = {};
  if (!isForm) headers['Content-Type'] = 'application/json';

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: isForm ? body : body ? JSON.stringify(body) : undefined,
  });

  const text = await res.text();
  let json;
  try {
    json = text ? JSON.parse(text) : {};
  } catch (e) {
    throw new Error(`Invalid JSON response: ${text?.slice(0, 200)}`);
  }

  if (!res.ok || json?.ok === false) {
    const msg = json?.error || res.statusText || 'Request failed';
    throw new Error(msg);
  }

  return json;
}

export const api = {
  base: BASE,
  get: (path) => request(path),
  post: (path, body, isForm = false) => request(path, { method: 'POST', body, isForm }),
};
