ARG PARENT_VERSION=latest
FROM ubuntu:20.04
LABEL maintainer="daviand"


ENV APT_DEPS git \
			python3 \
			python-is-python3 \
			pip \
			tshark \
			libgomp1 iproute2 
			#nano iputils-ping
ENV BUILD_DEPS build-essential cmake git libgmp3-dev libprocps-dev python3-markdown libboost-program-options-dev libssl-dev pkg-config
ENV PIP_DEPS requests flask pyshark psutil
RUN apt-get update -qq && \
	apt-get upgrade -qq
RUN DEBIAN_FRONTEND=noninteractive apt-get install -qq --no-install-recommends $APT_DEPS
#RUN  apt-get -y install tzdata
RUN DEBIAN_FRONTEND=noninteractive apt-get install -qq --no-install-recommends openjdk-17-jre
RUN pip install --no-cache-dir --upgrade pip && \
	pip install --no-cache-dir $PIP_DEPS

COPY ./Middlebox /home/Middlebox
COPY ./xjsnark_decompiled /home/xjsnark_decompiled
COPY ./libsnark /home/libsnark
WORKDIR /home/
#RUN [ ! -d "libsnark/build" ] || [ -z "$(ls -A libsnark/build)" ] && (DEBIAN_FRONTEND=noninteractive apt-get install -qq --no-install-recommends $BUILD_DEPS && cd libsnark && mkdir -p build && cd build && cmake .. && make && apt-get remove -y $BUILD_DEPS)
RUN set -e; \
    if [ ! -d "libsnark/build" ] || [ -z "$(ls -A libsnark/build)" ]; then \
        echo "Building libsnark..."; \
        apt-get update -qq && \
        DEBIAN_FRONTEND=noninteractive apt-get install -qq --no-install-recommends $BUILD_DEPS && \
        cd libsnark && mkdir -p build && cd build && cmake .. && make && \
        apt-get remove -y $BUILD_DEPS && apt-get autoremove --purge -qq; \
    else \
        echo "libsnark already built, skipping."; \
    fi

RUN apt-get autoremove --purge -qq
