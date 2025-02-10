FROM nvidia/cuda:12.1.0-base-ubuntu22.04  as deps

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y \
    && apt-get dist-upgrade -y \
    && apt-get install -y python3-pip

RUN ldconfig /usr/local/cuda-12.1/compat/

# update pip
RUN --mount=type=cache,target=/root/.cache/pip python3 -m pip install --upgrade pip

# install sglang's dependencies
# EFRON:
# these guys are unbelivably huge - >80GiB. Took well over ten minutes to install on my machine and used 28GiB(!) of RAM.
# we should consider having a base image with them pre-installed or seeing if we can knock it down a little bit.
RUN --mount=type=cache,target=/root/.cache/pip python3 -m pip install "sglang[all]" 
RUN --mount=type=cache,target=/root/.cache/pip python3 -m pip install flashinfer -i https://flashinfer.ai/whl/cu121/torch2.3

# install our own python dependencies
COPY requirements.txt ./requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip python3 -m pip install --upgrade -r ./requirements.txt

# not sure why this is here: is a vllm-workspace even in our image?
# ENV PYTHONPATH="/:/vllm-workspace" 
COPY ./src/handler.py ./handler.py

# run the serverless worker
CMD ["python3", "./handler.py"]
