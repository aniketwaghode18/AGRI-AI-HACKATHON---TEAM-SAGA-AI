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
			ctx.lineWidth = 3;
			ctx.font = 'bold 14px ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, Helvetica Neue, Arial';
			
			result.result.detections.forEach((d, idx) => {
				const [x1, y1, x2, y2] = d.bbox;
				const rx = x1 * sx;
				const ry = y1 * sy;
				const rw = (x2 - x1) * sx;
				const rh = (y2 - y1) * sy;

				// Color coding based on quality
				let color, bgColor;
				if (d.label === 'Healthy') {
					color = 'rgba(34, 197, 94, 1)'; // green
					bgColor = 'rgba(34, 197, 94, 0.2)';
				} else if (d.label === 'Defective') {
					color = 'rgba(239, 68, 68, 1)'; // red
					bgColor = 'rgba(239, 68, 68, 0.2)';
				} else {
					color = 'rgba(59, 130, 246, 1)'; // blue
					bgColor = 'rgba(59, 130, 246, 0.2)';
				}

				// Draw bounding box
				ctx.strokeStyle = color;
				ctx.fillStyle = bgColor;
				ctx.beginPath();
				ctx.rect(rx, ry, rw, rh);
				ctx.stroke();
				ctx.fill();

				// Draw label background
				const text = `${d.label} ${(d.confidence * 100).toFixed(1)}%`;
				const textWidth = ctx.measureText(text).width;
				ctx.fillStyle = color;
				ctx.fillRect(rx, Math.max(ry - 20, 0), textWidth + 12, 20);
				
				// Draw label text
				ctx.fillStyle = 'white';
				ctx.fillText(text, rx + 6, Math.max(ry - 6, 14));
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
		<div className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50">
			{/* Header with logo */}
			<header className="bg-white/80 backdrop-blur-sm shadow-lg border-b border-green-200">
				<div className="max-w-7xl mx-auto px-4 py-6">
					<div className="flex items-center space-x-4">
						<div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center shadow-lg transform hover:scale-105 transition-transform duration-300">
							<svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
								<path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
							</svg>
						</div>
						<div>
							<h1 className="text-3xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
								AgriVision
							</h1>
							<p className="text-green-600 font-medium">AI-Powered Seed Quality Analysis</p>
						</div>
					</div>
				</div>
			</header>

			<div className="max-w-7xl mx-auto px-4 py-8">
				{/* Hero Section */}
				<div className="text-center mb-12">
					<h2 className="text-4xl font-bold text-gray-800 mb-4">
						Detect Seed Quality with AI
					</h2>
					<p className="text-xl text-gray-600 max-w-3xl mx-auto">
						Upload an image of soybean seeds to instantly identify healthy, defective, moldy, or damaged seeds with advanced computer vision.
					</p>
				</div>

				{/* Upload Section */}
				<div className="bg-white/70 backdrop-blur-sm rounded-3xl shadow-xl p-8 mb-8 border border-green-100">
					<form onSubmit={onSubmit} className="space-y-6">
						<div className="text-center">
							<label className="block text-lg font-semibold text-gray-700 mb-4">
								Choose Seed Image
							</label>
							<div className="relative">
								<input
									type="file"
									accept="image/*"
									onChange={onFileChange}
									className="block w-full text-sm text-gray-700 file:mr-4 file:py-4 file:px-6 file:rounded-2xl file:border-0 file:text-sm file:font-semibold file:bg-gradient-to-r file:from-green-500 file:to-emerald-500 file:text-white hover:file:from-green-600 hover:file:to-emerald-600 file:transition-all file:duration-300 file:shadow-lg file:hover:shadow-xl file:cursor-pointer"
								/>
							</div>
						</div>
						
						<div className="text-center">
							<button
								type="submit"
								disabled={!file || loading}
								className="inline-flex items-center gap-3 px-8 py-4 rounded-2xl bg-gradient-to-r from-green-500 to-emerald-500 text-white font-semibold text-lg disabled:opacity-50 hover:from-green-600 hover:to-emerald-600 hover:shadow-xl transform hover:scale-105 transition-all duration-300 disabled:transform-none disabled:hover:scale-100"
							>
								{loading && (
									<span className="inline-block h-6 w-6 border-3 border-white border-t-transparent rounded-full animate-spin" />
								)}
								<span>{loading ? 'Analyzing Seeds...' : '🔍 Analyze Seeds'}</span>
							</button>
						</div>
					</form>
				</div>

				{error && (
					<div className="bg-red-50 border border-red-200 rounded-2xl p-6 mb-8">
						<div className="flex items-center">
							<svg className="w-6 h-6 text-red-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
								<path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
							</svg>
							<span className="text-red-700 font-medium">{error}</span>
						</div>
					</div>
				)}

				{/* Results Section */}
				<div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
					{/* Preview */}
					<div className="bg-white/70 backdrop-blur-sm rounded-3xl shadow-xl p-8 border border-green-100">
						<h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
							<svg className="w-6 h-6 text-green-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
								<path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
							</svg>
							Analysis Preview
						</h3>
						<div className="border-2 border-dashed border-green-200 rounded-2xl p-6 flex items-center justify-center min-h-[400px] bg-gradient-to-br from-green-50 to-emerald-50">
							{previewUrl ? (
								<canvas ref={canvasRef} className="max-w-full h-auto rounded-xl shadow-lg" />
							) : (
								<div className="text-center text-gray-500">
									<svg className="w-16 h-16 mx-auto mb-4 text-green-300" fill="currentColor" viewBox="0 0 20 20">
										<path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
									</svg>
									<p className="text-lg">No image selected</p>
									<p className="text-sm">Upload an image to see analysis</p>
								</div>
							)}
						</div>
					</div>

					{/* Results */}
					<div className="bg-white/70 backdrop-blur-sm rounded-3xl shadow-xl p-8 border border-green-100">
						<h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
							<svg className="w-6 h-6 text-blue-500 mr-3" fill="currentColor" viewBox="0 0 20 20">
								<path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
							</svg>
							Quality Analysis
						</h3>
						
						{result ? (
							<div className="space-y-6">
								{/* Summary Stats */}
								<div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-6 border border-blue-200">
									<div className="grid grid-cols-2 gap-4">
										<div className="text-center">
											<div className="text-3xl font-bold text-blue-600">{result.result.detections.length}</div>
											<div className="text-sm text-blue-700 font-medium">Total Seeds</div>
										</div>
										<div className="text-center">
											<div className="text-3xl font-bold text-green-600">
												{result.result.detections.filter(d => d.label === 'Healthy').length}
											</div>
											<div className="text-sm text-green-700 font-medium">Healthy</div>
										</div>
									</div>
								</div>

								{/* Detection List */}
								<div className="space-y-3">
									<h4 className="font-semibold text-gray-700 mb-3">Individual Analysis:</h4>
									{result.result.detections.map((d, idx) => (
										<div key={idx} className={`p-4 rounded-xl border-2 transition-all duration-300 hover:shadow-md ${
											d.label === 'Healthy' 
												? 'bg-green-50 border-green-200 hover:bg-green-100' 
												: 'bg-red-50 border-red-200 hover:bg-red-100'
										}`}>
											<div className="flex items-center justify-between">
												<div className="flex items-center space-x-3">
													<div className={`w-4 h-4 rounded-full ${
														d.label === 'Healthy' ? 'bg-green-500' : 'bg-red-500'
													}`}></div>
													<span className="font-semibold text-gray-800">{d.label}</span>
												</div>
												<div className="text-right">
													<div className="text-lg font-bold text-gray-700">{(d.confidence * 100).toFixed(1)}%</div>
													<div className="text-xs text-gray-500">confidence</div>
												</div>
											</div>
										</div>
									))}
								</div>

								{/* Action Buttons */}
								<div className="flex space-x-4 pt-4">
									<a
										href={result.result.overlay_url}
										target="_blank"
										rel="noreferrer"
										className="flex-1 px-4 py-3 rounded-xl bg-gradient-to-r from-gray-500 to-gray-600 text-white font-semibold text-center hover:from-gray-600 hover:to-gray-700 transition-all duration-300 transform hover:scale-105"
									>
										🔍 View Overlay
									</a>
									<button
										onClick={onDownloadPdf}
										className="flex-1 px-4 py-3 rounded-xl bg-gradient-to-r from-green-500 to-emerald-500 text-white font-semibold hover:from-green-600 hover:to-emerald-600 transition-all duration-300 transform hover:scale-105"
									>
										📄 Download Report
									</button>
								</div>
							</div>
						) : (
							<div className="text-center text-gray-500 py-12">
								<svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
									<path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
								</svg>
								<p className="text-lg">No analysis yet</p>
								<p className="text-sm">Upload an image to get started</p>
							</div>
						)}
					</div>
				</div>

				{/* Footer */}
				<footer className="text-center mt-16 text-gray-500">
					<p className="text-sm">🌱 Powered by AI • Built for Agriculture • Quality First</p>
				</footer>
			</div>
		</div>
	);
}