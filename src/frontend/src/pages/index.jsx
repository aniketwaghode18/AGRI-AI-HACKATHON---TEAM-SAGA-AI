import React, { useState } from 'react';
import { api } from '../utils/api';

export default function Home() {
	const [file, setFile] = useState(null);
	const [loading, setLoading] = useState(false);
	const [result, setResult] = useState(null);
	const [error, setError] = useState(null);

	const onSubmit = async (e) => {
		e.preventDefault();
		setError(null);
		setResult(null);
		if (!file) return;
		setLoading(true);
		try {
			const res = await api.predict(file);
			setResult(res);
		} catch (err) {
			setError(err.message || 'Request failed');
		} finally {
			setLoading(false);
		}
	};

	return (
		<div style={{ maxWidth: 640, margin: '40px auto', fontFamily: 'sans-serif' }}>
			<h1>AgriVision</h1>
			<p>Upload an image to get a prediction.</p>
			<form onSubmit={onSubmit}>
				<input type="file" accept="image/*" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
				<button type="submit" disabled={!file || loading} style={{ marginLeft: 8 }}>
					{loading ? 'Predicting…' : 'Predict'}
				</button>
			</form>
			{error && <pre style={{ color: 'crimson' }}>{error}</pre>}
			{result && (
				<pre style={{ background: '#f5f5f5', padding: 12, borderRadius: 6 }}>
{JSON.stringify(result, null, 2)}
				</pre>
			)}
		</div>
	);
}
