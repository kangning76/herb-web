FROM node:20-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
COPY --from=frontend-build /frontend/dist /frontend/dist
RUN mkdir -p uploads/herbs

EXPOSE 8000
CMD ["sh", "-c", "python -m app.seed_admin && python -m app.seed_herbs && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
