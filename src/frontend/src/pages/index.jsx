import React, { useEffect, useRef, useState } from 'react';
import { api } from '../utils/api';

export default function Home() {
	const [file, setFile] = useState(null);
	const [previewUrl, setPreviewUrl] = useState('');
	const [loading, setLoading] = useState(false);
	const [result, setResult] = useState(null);
	const [error, setError] = useState(null);
	const canvasRef = useRef(null);

	useEffect(() => {
		return () => {
			if (previewUrl) URL.revokeObjectURL(previewUrl);
		};
	}, [previewUrl]);

	useEffect(() => {
		if (!result || !previewUrl) return;
		const img = new Image();
		img.onload = () => {
			const canvas = canvasRef.current;
			if (!canvas) return;
			const scale = Math.min(640 / img.width, 480 / img.height, 1);
			canvas.width = Math.floor(img.width * scale);
			canvas.height = Math.floor(img.height * scale);
			const ctx = canvas.getContext('2d');
			ctx.clearRect(0, 0, canvas.width, canvas.height);
			ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
			const sx = canvas.width / result.result.width;
			const sy = canvas.height / result.result.height;
			ctx.lineWidth = 2;
			ctx.font = '12px sans-serif';
			result.result.detections.forEach((d) => {
				const [x1, y1, x2, y2] = d.bbox;
				ctx.strokeStyle = 'rgba(16, 185, 129, 1)'; // emerald-500
				ctx.fillStyle = 'rgba(16, 185, 129, 0.2)';
				ctx.beginPath();
				ctx.rect(x1 * sx, y1 * sy, (x2 - x1) * sx, (y2 - y1) * sy);
				ctx.stroke();
				ctx.fill();
				ctx.fillStyle = 'rgba(16, 185, 129, 1)';
				ctx.fillText(`${d.label} ${(d.confidence * 100).toFixed(1)}%`, x1 * sx + 4, y1 * sy + 14);
			});
		};
		img.src = previewUrl;
	}, [result, previewUrl]);

	const onFileChange = (e) => {
		const f = e.target.files?.[0] ?? null;
		setFile(f);
		setResult(null);
		setError(null);
		if (previewUrl) URL.revokeObjectURL(previewUrl);
		setPreviewUrl(f ? URL.createObjectURL(f) : '');
	};

	const onSubmit = async (e) => {
		e.preventDefault();
		if (!file) return;
		setLoading(true);
		setError(null);
		setResult(null);
		try {
			const res = await api.analyze(file);
			setResult(res);
		} catch (err) {
			setError(err.message || 'Request failed');
		} finally {
			setLoading(false);
		}
	};

	const onDownloadPdf = () => {
		window.print();
	};

	return (
		<div className="min-h-screen bg-gray-50 text-gray-900">
			<div className="max-w-5xl mx-auto px-4 py-8">
				<header className="mb-6">
					<h1 className="text-2xl font-semibold">AgriVision</h1>
					<p className="text-sm text-gray-600">Upload an image to analyze crop health.</p>
				</header>
				<form onSubmit={onSubmit} className="bg-white rounded-lg shadow p-4 flex items-center gap-3">
					<input
						type="file"
						accept="image/*"
						onChange={onFileChange}
						className="block w-full text-sm text-gray-700 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100"
					/>
					<button
						type="submit"
						disabled={!file || loading}
						className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-emerald-600 text-white disabled:opacity-50 hover:bg-emerald-700"
					>
						{loading && (
							<span className="inline-block h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
						)}
						<span>{loading ? 'Analyzing…' : 'Analyze'}</span>
					</button>
				</form>

				{error && (
					<div className="mt-4 p-3 rounded-md bg-red-50 text-red-700 text-sm">{error}</div>
				)}

				<div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
					<div className="bg-white rounded-lg shadow p-4">
						<h2 className="text-lg font-medium mb-3">Preview</h2>
						<div className="border rounded-md p-2 flex items-center justify-center min-h-[240px]">
							{previewUrl ? (
								<canvas ref={canvasRef} className="max-w-full h-auto" />
							) : (
								<p className="text-gray-500 text-sm">No image selected.</p>
							)}
						</div>
					</div>

					<div className="bg-white rounded-lg shadow p-4">
						<h2 className="text-lg font-medium mb-3">Results</h2>
						{result ? (
							<div>
								<div className="mb-3 text-sm text-gray-700">
									<span className="font-medium">Detections:</span> {result.result.detections.length}
								</div>
								<ul className="space-y-2">
									{result.result.detections.map((d, idx) => (
										<li key={idx} className="text-sm flex items-center justify-between border rounded-md p-2">
											<span className="text-gray-800">{d.label}</span>
											<span className="text-gray-500">{(d.confidence * 100).toFixed(1)}%</span>
										</li>
									))}
								</ul>
								<div className="mt-4 flex gap-2">
									<a
										href={result.result.overlay_url}
										target="_blank"
										rel="noreferrer"
										className="px-3 py-2 rounded-md bg-gray-100 text-gray-800 hover:bg-gray-200 text-sm"
									>
										Open Overlay
									</a>
									<button
										onClick={onDownloadPdf}
										className="px-3 py-2 rounded-md bg-emerald-600 text-white hover:bg-emerald-700 text-sm"
									>
										Download PDF
									</button>
								</div>
							</div>
						) : (
							<p className="text-gray-500 text-sm">No results yet.</p>
						)}
					</div>
				</div>

				<footer className="mt-10 text-xs text-gray-500">API: /analyze — styled with Tailwind classes</footer>
			</div>
		</div>
	);
}
