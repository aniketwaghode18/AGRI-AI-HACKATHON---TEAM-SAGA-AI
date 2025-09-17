AgriVision: minimal Flask + React scaffold for rapid ML prototyping (mockable, hackathon-ready).

Local development (Windows cmd and Bash shown):
- Create and activate venv:
  - Windows: python -m venv .venv && .venv\Scripts\activate
  - Bash: python -m venv .venv && source .venv/bin/activate
- Install Python deps (global delegates to server): pip install -r requirements.txt
- Run Flask API (dev): set FLASK_ENV=development&& set MOCK=1&& python src/server/app.py
  - Bash: FLASK_ENV=development MOCK=1 python src/server/app.py
  - API at http://127.0.0.1:5000
- Run frontend dev server:
  - cd src/frontend
  - npm install
  - npm run dev
  - App at http://127.0.0.1:5173
- Example prediction (curl): curl -F "file=@data/sample.jpg" http://127.0.0.1:5000/predict
- Run tests (none yet; placeholders):
  - Python: pytest -q
  - Frontend: cd src/frontend && npm test

Repo layout:
- src/server: Flask app (+ Dockerfile)
- src/ml: ML stubs (inference/export/train/preprocess)
- src/frontend: React Vite skeleton
- data: datasets go here
- .github/workflows/ci.yml: CI skeleton
