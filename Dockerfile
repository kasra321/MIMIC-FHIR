FROM python:3.11-slim

RUN pip install --no-cache-dir duckdb sqlmesh[duckdb] pyarrow

WORKDIR /app
COPY ./pipeline /app/pipeline
COPY ./models /app/models
COPY ./run_pipeline.sh /app/run_pipeline.sh

# Fix EOL errors when running on different machines (windows vs. mac/linux)
RUN sed -i 's/\r$//' /app/run_pipeline.sh && \
    chmod +x /app/run_pipeline.sh

ENV DUCKDB_PATH=/data/warehouse/mimic_fhir.duckdb
ENV RAW_DATA_PATH=/data/raw

ENTRYPOINT [ "/app/run_pipeline.sh" ]
