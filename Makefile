.PHONY: setup setup-backend setup-frontend build-frontend run run-backend run-frontend test seed clean

# ── Python executable ──────────────────────────────────────────────────────────
PYTHON ?= C:\Users\bhada\OneDrive\Desktop\GJ POLICE\python_portable\python.exe

# ── Setup ──────────────────────────────────────────────────────────────────────
setup: setup-backend setup-frontend build-frontend seed
	@echo ""
	@echo "=========================================================="
	@echo "  Fraud Shield setup complete!"
	@echo "  Run:  make run   (or double-click run.bat)"
	@echo "=========================================================="

setup-backend:
	@echo "Installing Python dependencies..."
	cd backend && "$(PYTHON)" -m pip install -r requirements.txt

setup-frontend:
	@echo "Installing Node dependencies..."
	cd frontend && npm install

build-frontend:
	@echo "Building frontend bundle..."
	cd frontend && npm run build

seed:
	@echo "Seeding synthetic database..."
	cd backend && "$(PYTHON)" app/services/seed.py

# ── Run ────────────────────────────────────────────────────────────────────────
run:
	@echo "Starting Fraud Shield on http://localhost:8000 ..."
	cd backend && "$(PYTHON)" run.py

run-backend:
	cd backend && "$(PYTHON)" run.py

run-frontend:
	cd frontend && npm run dev

# ── Test ───────────────────────────────────────────────────────────────────────
test:
	cd backend && "$(PYTHON)" -m pytest tests/ -v

# ── Clean ──────────────────────────────────────────────────────────────────────
clean:
	cd backend && "$(PYTHON)" -c "import os; os.remove('fraud_shield.db') if os.path.exists('fraud_shield.db') else None"
	@echo "Database removed. Run 'make seed' to re-seed."
