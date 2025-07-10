# Use a lightweight base image with build tools
FROM ubuntu:22.04

# Set environment variables to make noninteractive installs cleaner
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
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
ENV LD_LIBRARY_PATH=/opt/mcr/v99/runtime/glnxa64:/opt/mcr/v99/bin/glnxa64:/opt/mcr/v99/sys/os/glnxa64
ENV XAPPLRESDIR=/opt/mcr/v99/X11/app-defaults

# Install pyenv
ENV PYENV_ROOT="/root/.pyenv"
ENV PATH="$PYENV_ROOT/bin:$PATH"

RUN curl https://pyenv.run | bash && \
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> /root/.bashrc && \
    echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> /root/.bashrc && \
    echo 'eval "$(pyenv init --path)"' >> /root/.bashrc && \
    echo 'eval "$(pyenv init -)"' >> /root/.bashrc && \
    echo 'eval "$(pyenv virtualenv-init -)"' >> /root/.bashrc

CMD ["/bin/bash"]