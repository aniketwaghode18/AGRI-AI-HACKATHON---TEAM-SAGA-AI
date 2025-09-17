const API_BASE = import.meta?.env?.VITE_API_BASE || 'http://127.0.0.1:5000';

async function http(method, path, body, headers = {}) {
	const res = await fetch(`${API_BASE}${path}`, {
		method,
		body,
		headers
	});
	if (!res.ok) {
		const txt = await res.text();
		throw new Error(`HTTP ${res.status}: ${txt}`);
	}
	const ct = res.headers.get('content-type') || '';
	if (ct.includes('application/json')) return res.json();
	return res.text();
}

export const api = {
	health: () => http('GET', '/health'),
	analyze: async (file) => {
		const form = new FormData();
		form.append('image', file);
		return http('POST', '/analyze', form);
	}
};
