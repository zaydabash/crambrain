.PHONY: install dev-api dev-web test-backend test-frontend test lint clean

install:
	@echo "Installing backend dependencies..."
	cd apps/api && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	npm install

dev-api:
	@echo "Starting API..."
	cd apps/api && . .venv/bin/activate && PYTHONPATH=src uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

dev-web:
	@echo "Starting Web..."
	npm run dev

test-backend:
	@echo "Running backend tests..."
	cd apps/api && . .venv/bin/activate && PYTHONPATH=src pytest ../../tests/backend -v

test-frontend:
	@echo "Running frontend tests..."
	npm test

test: test-backend test-frontend

lint:
	@echo "Linting..."
	npm run lint

clean:
	rm -rf apps/api/.venv
	rm -rf node_modules
