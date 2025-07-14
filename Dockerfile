# Use a lightweight base image with build tools
FROM python:3.12-slim

# Set environment variables to make noninteractive installs cleaner
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-tk tk-dev libx11-dev libxft-dev libxext-dev \
    cmake \
    git \
    curl \
    vim \
    bash \
    unzip \
    default-jre \
    xorg \
    libxt6 \
    libxmu6 \
    libxext6 \
    libxpm4 \
    libglu1-mesa \
    libgtk2.0-0 \
    libgconf-2-4 \
    libnss3 \
    libasound2 \
    libsm6 \
    libxrender1 \
    libfontconfig1 \
    libice6 \
    openssh-client \
    libfftw3-dev \
    pkg-config \
    doxygen \
    zip \
    uncrustify \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /project

# Copy MCR installer into image (assume it's in the same directory as Dockerfile)
COPY janus-c-3.0.5.zip /project/
COPY MATLAB_Runtime_R2025a_glnxa64.zip /tmp/

# Unzip and install MCR
RUN unzip /tmp/MATLAB_Runtime_R2025a_glnxa64.zip -d /tmp/mcr && \
    /tmp/mcr/install -mode silent -agreeToLicense yes -destinationFolder /opt/mcr && \
    rm -rf /tmp/mcr /tmp/MATLAB_Runtime_R2025a_glnxa64.zip

# Set environment variables for MCR
ENV LD_LIBRARY_PATH=/opt/mcr/R2025a/runtime/glnxa64:/opt/mcr/R2025a/bin/glnxa64:/opt/mcr/R2025a/sys/os/glnxa64
ENV XAPPLRESDIR=/opt/mcr/R2025a/X11/app-defaults

CMD ["/bin/bash"]