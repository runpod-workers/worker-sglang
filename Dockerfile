FROM nvidia/cuda:12.1.0-base-ubuntu22.04 

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y \
    && apt-get dist-upgrade -y \
    && apt-get install -y python3-pip

RUN ldconfig /usr/local/cuda-12.1/compat/

# install sglang's dependencies

# EFRON:
# these guys are unbelivably huge - >80GiB. Took well over ten minutes to install on my machine and used 28GiB(!) of RAM.
# we should consider having a base image with them pre-installed or seeing if we can knock it down a little bit.
RUN python3 -m pip install "sglang[all]" 
RUN python3 -m pip install flashinfer -i https://flashinfer.ai/whl/cu121/torch2.3


# install _our_ dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    python3 -m pip install --upgrade pip && \
    python3 -m pip install --upgrade -r /requirements.txt

RUN mkdir app
COPY requirements.txt ./app/requirements.txt

# EFRON: no idea what this is doing: leaving it in in case it's important
ENV BASE_PATH=$BASE_PATH 
ENV HF_DATASETS_CACHE="${BASE_PATH}/huggingface-cache/datasets" 
ENV HF_HOME="${BASE_PATH}/huggingface-cache/hub"
ENV HF_HUB_ENABLE_HF_TRANSFER=1
ENV HUGGINGFACE_HUB_CACHE="${BASE_PATH}/huggingface-cache/hub"
ENV MODEL_NAME=$MODEL_NAME
ENV MODEL_REVISION=$MODEL_REVISION
ENV QUANTIZATION=$QUANTIZATION
ENV TOKENIZER_NAME=$TOKENIZER_NAME
ENV TOKENIZER_REVISION=$TOKENIZER_REVISION

# not sure why this is here: is a vllm-workspace even in our image?
ENV PYTHONPATH="/:/vllm-workspace" 
COPY ./src/handler.py ./app/handler.py
CMD ["python3", "./app/handler.py"] # actually run the handler
