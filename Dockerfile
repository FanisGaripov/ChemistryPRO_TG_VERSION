FROM ubuntu:22.04

# Устанавливаем все зависимости
RUN apt-get update && \
    apt-get install -y \
    wget \
    unzip \
    make \
    g++ \
    autoconf \
    automake \
    libtool \
    pkg-config \
    libpng-dev \
    libjpeg-dev \
    libtiff-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Leptonica
WORKDIR /tmp
RUN wget http://www.leptonica.org/source/leptonica-1.83.1.tar.gz && \
    tar -xzf leptonica-1.83.1.tar.gz && \
    cd leptonica-1.83.1 && \
    ./configure && \
    make && \
    make install && \
    ldconfig && \
    rm -rf /tmp/leptonica*

# Устанавливаем Tesseract
WORKDIR /tmp
RUN wget https://github.com/tesseract-ocr/tesseract/archive/5.3.2.tar.gz && \
    tar -xzf 5.3.2.tar.gz && \
    cd tesseract-5.3.2 && \
    ./autogen.sh && \
    ./configure && \
    make && \
    make install && \
    ldconfig && \
    rm -rf /tmp/tesseract*

# Устанавливаем языковые данные
WORKDIR /usr/local/share/tessdata
RUN wget https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata && \
    wget https://github.com/tesseract-ocr/tessdata/raw/main/rus.traineddata

# Проверяем установку
CMD ["tesseract", "--version"]
