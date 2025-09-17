import React, { useEffect, useRef } from 'react';

/**
 * OverlayCanvas
 * - Props:
 *   - imageUrl: string (required) original image URL
 *   - predictions: Array<{ box: [number, number, number, number], label?: string, confidence?: number }>
 *   - maxWidth?: number (default 640)
 */
export default function OverlayCanvas({ imageUrl, predictions = [], maxWidth = 640 }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    let disposed = false;
    const draw = async () => {
      const canvas = canvasRef.current;
      if (!canvas || !imageUrl) return;
      const ctx = canvas.getContext('2d');

      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.src = imageUrl;

      try {
        await img.decode();
      } catch (e) {
        // If decode fails, try onload fallback
        await new Promise((resolve) => (img.onload = resolve));
      }
      if (disposed) return;

      const scale = Math.min(1, maxWidth / (img.width || 1));
      const cW = Math.max(1, Math.floor((img.width || 1) * scale));
      const cH = Math.max(1, Math.floor((img.height || 1) * scale));
      canvas.width = cW;
      canvas.height = cH;

      ctx.clearRect(0, 0, cW, cH);
      if (img.width && img.height) {
        ctx.drawImage(img, 0, 0, cW, cH);
      }

      const scaleX = cW / (img.width || 1);
      const scaleY = cH / (img.height || 1);

      ctx.lineWidth = Math.max(2, Math.floor(Math.min(cW, cH) / 150));
      ctx.strokeStyle = '#22c55e';
      ctx.font = '12px ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto';

      predictions.forEach((det) => {
        const [x1, y1, x2, y2] = det.box || [0, 0, 0, 0];
        const rx1 = x1 * scaleX;
        const ry1 = y1 * scaleY;
        const rw = (x2 - x1) * scaleX;
        const rh = (y2 - y1) * scaleY;
        ctx.strokeRect(rx1, ry1, rw, rh);

        const label = `${det.label ?? 'object'} ${(det.confidence ?? 0).toFixed(2)}`;
        const tw = ctx.measureText(label).width;
        const th = 14;
        ctx.fillStyle = 'rgba(0,0,0,0.6)';
        ctx.fillRect(rx1, Math.max(0, ry1 - th - 4), tw + 8, th + 4);
        ctx.fillStyle = '#fff';
        ctx.fillText(label, rx1 + 4, Math.max(10, ry1 - 6));
      });
    };

    draw();
    return () => {
      disposed = true;
    };
  }, [imageUrl, predictions, maxWidth]);

  return (
    <canvas ref={canvasRef} className="w-full h-auto rounded border border-gray-200" />
  );
}
