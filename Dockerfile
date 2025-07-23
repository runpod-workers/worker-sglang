FROM nvidia/cuda:12.1.0-devel-ubuntu22.04 

# Install system dependencies
RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev build-essential git cmake && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Configure CUDA paths
RUN ldconfig /usr/local/cuda-12.1/compat/

# Install Python dependencies
COPY builder/requirements.txt /requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    python3 -m pip install --upgrade pip && \
    python3 -m pip install --upgrade -r /requirements.txt

# Install sglang and flashinfer with specific versions and extra error handling
RUN python3 -m pip install torch>=2.3.0 && \
    python3 -m pip install "sglang[all]" --no-build-isolation && \
    python3 -m pip install --upgrade pip && \
    python3 -m pip install flashinfer --index-url https://flashinfer.ai/whl/cu121/torch2.3

# Setup for Option 2: Building the Image with the Model included
ARG MODEL_NAME=""
ARG TOKENIZER_NAME=""
ARG BASE_PATH="/runpod-volume"
ARG QUANTIZATION=""
ARG MODEL_REVISION=""
ARG TOKENIZER_REVISION=""

ENV MODEL_NAME=$MODEL_NAME \
    MODEL_REVISION=$MODEL_REVISION \
    TOKENIZER_NAME=$TOKENIZER_NAME \
    TOKENIZER_REVISION=$TOKENIZER_REVISION \
    BASE_PATH=$BASE_PATH \
    QUANTIZATION=$QUANTIZATION \
    HF_DATASETS_CACHE="${BASE_PATH}/huggingface-cache/datasets" \
    HUGGINGFACE_HUB_CACHE="${BASE_PATH}/huggingface-cache/hub" \
    HF_HOME="${BASE_PATH}/huggingface-cache/hub" \
    HF_HUB_ENABLE_HF_TRANSFER=1 

ENV PYTHONPATH="/:/vllm-workspace"

# Copy source code and test input
COPY src /src
COPY test_input.json /test_input.json

# Download model if specified
RUN --mount=type=secret,id=HF_TOKEN,required=false \
    if [ -f /run/secrets/HF_TOKEN ]; then \
        export HF_TOKEN=$(cat /run/secrets/HF_TOKEN); \
    fi && \
    if [ -n "$MODEL_NAME" ]; then \
        python3 /src/download_model.py; \
    fi

# Start the handler
CMD ["python3", "/src/handler.py"]