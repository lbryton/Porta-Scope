FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
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
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy MCR installer into image (assume it's in the same directory as Dockerfile)
COPY MATLAB_Runtime_R2025a_glnxa64.zip /tmp/

# Unzip and install MCR
RUN unzip /tmp/MATLAB_Runtime_R2025a_glnxa64.zip -d /tmp/mcr && \
    /tmp/mcr/install -mode silent -agreeToLicense yes -destinationFolder /opt/mcr && \
    rm -rf /tmp/mcr /tmp/MATLAB_Runtime_R2025a_glnxa64.zip


WORKDIR /project

# Set environment variables for MCR
ENV LD_LIBRARY_PATH=/opt/mcr/v99/runtime/glnxa64:/opt/mcr/v99/bin/glnxa64:/opt/mcr/v99/sys/os/glnxa64
ENV XAPPLRESDIR=/opt/mcr/v99/X11/app-defaults