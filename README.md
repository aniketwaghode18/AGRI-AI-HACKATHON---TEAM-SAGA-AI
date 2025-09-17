# AgriVision: Fast CV starter for crop health inference

## Local development

### Prereqs
- Python 3.11+
- Node.js 18+
- Git

### Setup (Windows/macOS/Linux)
```bash
# 1) Create virtualenv
python -m venv .venv

# 2) Activate venv
# Windows (cmd)
.venv\\Scripts\\activate
# Windows (PowerShell)
# .venv\\Scripts\\Activate.ps1
# macOS/Linux (bash/zsh)
# source .venv/bin/activate

# 3) Install Python deps
pip install -U pip
pip install -r requirements.txt

# 4) Install server deps (optional if using top-level)
pip install -r src/server/requirements.txt

# 5) Install frontend deps
cd src/frontend
npm install
cd ../..
```

### Run services
```bash
# Terminal A - Flask API
set FLASK_APP=src/server/app.py & set FLASK_ENV=development & flask run --host=0.0.0.0 --port=5000 | cat
# macOS/Linux:
# FLASK_APP=src/server/app.py FLASK_ENV=development flask run --host=0.0.0.0 --port=5000

# Terminal B - Frontend (Vite dev server)
cd src/frontend
npm run dev
```

### Example API usage
```bash
# Health check
curl http://localhost:5000/health

# Predict with an image file
curl -X POST http://localhost:5000/api/predict -F "image=@path/to/sample.jpg"

# Predict with JSON (e.g., URL)
curl -X POST http://localhost:5000/api/predict -H "Content-Type: application/json" -d '{"url": "https://example.com/image.jpg"}'
```

### Tests
```bash
# (Server) Using pytest
pytest -q
```

### Docker (server only)
```bash
# Build
docker build -t agrivision-server -f src/server/Dockerfile .
# Run
docker run -it --rm -p 5000:5000 agrivision-server
```

### Project layout
- src/server: Flask API
- src/ml: Training, preprocessing, export, and inference code
- src/frontend: React (Vite) app skeleton
- data: Datasets and artifacts (gitignored)
```
