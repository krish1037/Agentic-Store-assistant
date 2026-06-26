FROM python:3.11-slim
# Prevent python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies if any are needed (e.g. gcc, curl)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Run ingestion step to pre-build the FAISS index during the image build process
# (Requires GOOGLE_API_KEY to be passed as a build argument: --build-arg GOOGLE_API_KEY=your_key)
#ARG GOOGLE_API_KEY
#RUN if [ -z "$GOOGLE_API_KEY" ]; then \
#    echo "Error: GOOGLE_API_KEY build argument is required to build the FAISS index at build time." && exit 1; \
#   fi && \
#   GOOGLE_API_KEY=${GOOGLE_API_KEY} python -c "from app.rag.ingest import build_index; build_index()"

# Expose port (metadata only; Cloud Run uses dynamic port binding)
EXPOSE 8080

# Run FastAPI app using uvicorn, reading PORT env variable dynamically
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
