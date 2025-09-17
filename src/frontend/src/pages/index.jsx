import React, { useEffect, useRef, useState } from 'react';
import { api } from '../utils/api';

export default function IndexPage() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const imgRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!file) {
      setPreviewUrl(null);
      return;
    }
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  useEffect(() => {
    // Draw overlay when result or preview changes
    const draw = async () => {
      const canvas = canvasRef.current;
      const imgEl = imgRef.current;
      if (!canvas || !imgEl) return;

      const ctx = canvas.getContext('2d');
      const img = new Image();
      img.src = previewUrl || '';
      await img.decode().catch(() => {});

      const maxWidth = 640;
      const scale = Math.min(1, maxWidth / (img.width || 1));
      canvas.width = Math.max(1, Math.floor((img.width || 1) * scale));
      canvas.height = Math.max(1, Math.floor((img.height || 1) * scale));

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      if (img.width && img.height) {
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      }

      // If backend provided overlay_url, draw it on top.
      if (result?.overlay_url) {
        const ov = new Image();
        ov.crossOrigin = 'anonymous';
        ov.src = result.overlay_url.startsWith('http') ? result.overlay_url : `${api.base}${result.overlay_url}`;
        await ov.decode().catch(() => {});
        ctx.drawImage(ov, 0, 0, canvas.width, canvas.height);
        return;
      }

      // Else, draw boxes from prediction.objects if present
      const objects = result?.prediction?.objects || [];
      ctx.lineWidth = Math.max(2, Math.floor(Math.min(canvas.width, canvas.height) / 150));
      ctx.strokeStyle = '#22c55e';
      ctx.fillStyle = 'rgba(0,0,0,0.6)';
      ctx.font = '12px ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto';

      const scaleX = canvas.width / (img.width || 1);
      const scaleY = canvas.height / (img.height || 1);

      objects.forEach((det) => {
        const [x1, y1, x2, y2] = det.box || [0, 0, 0, 0];
        const rx1 = x1 * scaleX;
        const ry1 = y1 * scaleY;
        const rw = (x2 - x1) * scaleX;
        const rh = (y2 - y1) * scaleY;
        ctx.strokeRect(rx1, ry1, rw, rh);

        const label = `${det.label} ${(det.confidence ?? 0).toFixed(2)}`;
        const tw = ctx.measureText(label).width;
        const th = 14;
        ctx.fillStyle = 'rgba(0,0,0,0.6)';
        ctx.fillRect(rx1, Math.max(0, ry1 - th - 4), tw + 8, th + 4);
        ctx.fillStyle = '#fff';
        ctx.fillText(label, rx1 + 4, Math.max(10, ry1 - 6));
        ctx.fillStyle = 'rgba(0,0,0,0.6)';
      });
    };
    draw();
  }, [result, previewUrl]);

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select an image.');
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const form = new FormData();
      form.append('image', file);
      const json = await api.post('/analyze', form, true);
      setResult(json);
    } catch (err) {
      setError(err.message || 'Request failed');
    } finally {
      setLoading(false);
    }
  };

  const downloadPdf = () => {
    // Simple client-side report: open a printable window and let user save as PDF
    const canvas = canvasRef.current;
    const data = result?.prediction || {};
    const win = window.open('', '_blank');
    if (!win) return;
    const imgData = canvas?.toDataURL('image/png') || '';
    win.document.write(`<!doctype html><html><head><title>Report</title></head><body style="font-family: ui-sans-serif, system-ui;">
      <h1>AgriVision Report</h1>
      <p><strong>Mode:</strong> ${result?.mode || 'n/a'}</p>
      <p><strong>Objects:</strong> ${Array.isArray(data.objects) ? data.objects.length : 0}</p>
      <img src="${imgData}" style="max-width: 100%; border: 1px solid #ccc;"/>
      <pre style="background:#f6f8fa; padding:12px;">${JSON.stringify(result, null, 2)}</pre>
      <script>window.onload = () => { window.print(); }</script>
    </body></html>`);
    win.document.close();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-5xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-semibold text-gray-900">AgriVision</h1>
        <p className="text-gray-600 mt-1">Upload a crop image to analyze health.</p>

        <form onSubmit={onSubmit} className="mt-6 p-4 bg-white rounded-lg shadow border border-gray-100">
          <div className="flex items-center gap-3">
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="block w-full text-sm text-gray-900 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100"
            />
            <button
              type="submit"
              disabled={loading || !file}
              className="inline-flex items-center px-4 py-2 rounded-md bg-emerald-600 text-white text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:bg-emerald-700"
            >
              {loading && (
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
                </svg>
              )}
              {loading ? 'Analyzing…' : 'Analyze'}
            </button>
          </div>
        </form>

        {error && (
          <div className="mt-4 p-3 rounded-md bg-red-50 text-red-700 border border-red-100">{String(error)}</div>
        )}

        <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
          <div className="bg-white rounded-lg shadow border border-gray-100 p-3">
            <h2 className="text-sm font-medium text-gray-700 mb-2">Preview & Overlay</h2>
            <div className="w-full overflow-auto">
              <canvas ref={canvasRef} className="w-full h-auto rounded border border-gray-200" />
              {/* Hidden image to know natural size */}
              {previewUrl && (
                <img ref={imgRef} src={previewUrl} alt="preview" style={{ display: 'none' }} />
              )}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow border border-gray-100 p-4">
            <h2 className="text-sm font-medium text-gray-700 mb-2">Results</h2>
            {!result && <p className="text-gray-500 text-sm">No results yet.</p>}
            {result && (
              <div className="space-y-3">
                <div className="text-sm text-gray-800">
                  <div><span className="text-gray-500">Mode:</span> {result.mode || 'n/a'}</div>
                  <div><span className="text-gray-500">Objects:</span> {result?.prediction?.objects?.length ?? 0}</div>
                </div>

                <div className="max-h-64 overflow-auto border border-gray-100 rounded">
                  <table className="min-w-full text-sm">
                    <thead className="bg-gray-50 text-gray-600">
                      <tr>
                        <th className="text-left px-3 py-2">Label</th>
                        <th className="text-left px-3 py-2">Confidence</th>
                        <th className="text-left px-3 py-2">Box</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(result?.prediction?.objects || []).map((o, idx) => (
                        <tr key={idx} className="border-t">
                          <td className="px-3 py-2">{o.label}</td>
                          <td className="px-3 py-2">{(o.confidence ?? 0).toFixed(2)}</td>
                          <td className="px-3 py-2">[{o.box?.map((v) => Number(v).toFixed(0)).join(', ')}]</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={downloadPdf}
                    disabled={!result}
                    className="inline-flex items-center px-3 py-2 rounded-md bg-gray-800 text-white text-sm hover:bg-gray-900 disabled:opacity-50"
                  >
                    Download PDF
                  </button>
                  {result?.overlay_url && (
                    <a
                      className="inline-flex items-center px-3 py-2 rounded-md bg-gray-100 text-gray-800 text-sm hover:bg-gray-200"
                      href={result.overlay_url.startsWith('http') ? result.overlay_url : `${api.base}${result.overlay_url}`}
                      target="_blank" rel="noreferrer"
                    >
                      Open Overlay PNG
                    </a>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
