# Use a lightweight base image with build tools
FROM ubuntu:22.04

# Set environment variables to make noninteractive installs cleaner
ENV DEBIAN_FRONTEND=noninteractive

# Update and install essential packages
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    curl \
    vim \
    bash \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /project

# Start container in interactive bash shell
CMD ["/bin/bash"]