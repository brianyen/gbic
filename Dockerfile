FROM ubuntu:18.04

# Install dependencies
RUN apt-get update
RUN apt-get install -y python3 python3-pip git && \
    pip3 install --upgrade pip
RUN git clone https://github.com/brianyen/gbic.git && \
    cd gbic && \
    pip3 install -r requirements.txt
RUN apt-get install -y wget
RUN cd /tmp && \
    mkdir ffmpeg && \
    cd ffmpeg && \
    wget https://www.johnvansickle.com/ffmpeg/old-releases/ffmpeg-4.2.1-amd64-static.tar.xz && \
    tar xvf ffmpeg-4.2.1-amd64-static.tar.xz && \
    mv ffmpeg-4.2.1-amd64-static/ffmpeg /usr/bin/ffmpeg && \
    cd /gbic
RUN cd /usr/bin/ && \
    ln -s /usr/bin/python3 py && \ 
    cd /gbic