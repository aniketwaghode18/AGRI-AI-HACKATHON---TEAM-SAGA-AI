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
    const draw = async () => {
      const canvas = canvasRef.current;
      const imgEl = imgRef.current;
      if (!canvas || !imgEl) return;

      const ctx = canvas.getContext('2d');
      const img = new Image();
      img.src = previewUrl || '';
      await img.decode().catch(() => {});

      const maxWidth = 720;
      const scale = Math.min(1, maxWidth / (img.width || 1));
      canvas.width = Math.max(1, Math.floor((img.width || 1) * scale));
      canvas.height = Math.max(1, Math.floor((img.height || 1) * scale));

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      if (img.width && img.height) ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

      if (result?.overlay_url) {
        const ov = new Image();
        ov.crossOrigin = 'anonymous';
        ov.src = result.overlay_url.startsWith('http') ? result.overlay_url : `${api.base}${result.overlay_url}`;
        await ov.decode().catch(() => {});
        ctx.drawImage(ov, 0, 0, canvas.width, canvas.height);
        return;
      }

      const objects = result?.prediction?.objects || [];
      ctx.lineWidth = Math.max(2, Math.floor(Math.min(canvas.width, canvas.height) / 150));
      ctx.strokeStyle = '#10b981';
      ctx.fillStyle = 'rgba(0,0,0,0.6)';
      ctx.font = '12px Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto';

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
        ctx.fillStyle = 'rgba(17,24,39,0.8)';
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
    if (!file) { setError('Please select an image.'); return; }
    setLoading(true); setError(null); setResult(null);
    try {
      const form = new FormData();
      form.append('image', file);
      const json = await api.post('/analyze', form, true);
      setResult(json);
    } catch (err) { setError(err.message || 'Request failed'); }
    finally { setLoading(false); }
  };

  const downloadPdf = () => {
    const canvas = canvasRef.current;
    const data = result?.prediction || {};
    const win = window.open('', '_blank');
    if (!win) return;
    const imgData = canvas?.toDataURL('image/png') || '';
    win.document.write(`<!doctype html><html><head><title>Report</title></head><body style="font-family: Inter, ui-sans-serif, system-ui;">
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
    <div className="space-y-6">
      <section className="card p-6">
        <div className="sm:flex sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-xl font-semibold text-gray-900">Analyze crop image</h1>
            <p className="text-gray-600 text-sm mt-1">Upload a photo to detect plant health and view overlays.</p>
          </div>
        </div>
        <form onSubmit={onSubmit} className="mt-4">
          <div className="flex flex-col sm:flex-row sm:items-center gap-3">
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="block w-full text-sm text-gray-900 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100"
            />
            <button type="submit" disabled={loading || !file} className="btn-primary">
              {loading ? 'Analyzing…' : 'Analyze'}
            </button>
          </div>
          {error && <div className="mt-3 p-3 rounded-md bg-red-50 text-red-700 border border-red-100">{String(error)}</div>}
        </form>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        <section className="card p-4">
          <h2 className="text-sm font-medium text-gray-700 mb-2">Preview & Overlay</h2>
          <div className="w-full overflow-auto">
            <canvas ref={canvasRef} className="w-full h-auto rounded border border-gray-200 shadow-inner" />
            {previewUrl && (<img ref={imgRef} src={previewUrl} alt="preview" style={{ display: 'none' }} />)}
          </div>
        </section>

        <section className="card p-4">
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
                      <tr key={idx} className="border-t hover:bg-gray-50">
                        <td className="px-3 py-2">{o.label}</td>
                        <td className="px-3 py-2">{(o.confidence ?? 0).toFixed(2)}</td>
                        <td className="px-3 py-2">[{o.box?.map((v) => Number(v).toFixed(0)).join(', ')}]</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="flex gap-2">
                <button onClick={downloadPdf} disabled={!result} className="btn-secondary disabled:opacity-50">Download PDF</button>
                {result?.overlay_url && (
                  <a className="btn bg-gray-100 text-gray-800 hover:bg-gray-200" href={result.overlay_url.startsWith('http') ? result.overlay_url : `${api.base}${result.overlay_url}`} target="_blank" rel="noreferrer">Open Overlay PNG</a>
                )}
              </div>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
