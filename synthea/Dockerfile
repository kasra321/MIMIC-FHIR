FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
  curl \
  wget \
  ca-certificates \
  gnupg \
  software-properties-common \
  build-essential \
  git \
  && rm -rf /var/lib/apt/lists/*

# Install Java (OpenJDK 21 LTS)
RUN apt-get update && apt-get install -y --no-install-recommends \
  openjdk-21-jdk \
  && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Install Python 3.11
RUN add-apt-repository ppa:deadsnakes/ppa -y \
  && apt-get update && apt-get install -y --no-install-recommends \
  python3.11 \
  python3.11-dev \
  python3.11-venv \
  python3-pip \
  && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 \
  && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
RUN pip install --no-cache-dir duckdb pyarrow

WORKDIR /app

# Copy the Synthea Java file over
COPY ./synthea/synthea-with-dependencies.jar /app/synthea-with-dependencies.jar

# Pipeline
COPY ./adapters /app/adapters
COPY ./run_pipeline.sh /app/run_pipeline.sh
RUN chmod +x /app/run_pipeline.sh
RUN mkdir -p /data/warehouse && mkdir -p /data/synthea

# Check both Java and Python are installed
RUN java -version && python --version

ENTRYPOINT [ "/app/run_pipeline.sh" ]