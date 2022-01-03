FROM ubuntu:18.04

# Install dependencies

RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata
RUN apt-get install software-properties-common -y && \
    add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get -y install python3.9-distutils python3.9 python3-pip git wget && \
    python3.9 -m pip install --upgrade pip
RUN cd /tmp && \
    mkdir ffmpeg && \
    cd ffmpeg && \
    wget https://www.johnvansickle.com/ffmpeg/old-releases/ffmpeg-4.2.1-amd64-static.tar.xz && \
    tar xvf ffmpeg-4.2.1-amd64-static.tar.xz && \
    mv ffmpeg-4.2.1-amd64-static/ffmpeg /usr/bin/ffmpeg
RUN apt-get -y install libgl1-mesa-glx
RUN cd /usr/bin/ && \
    ln -s /usr/bin/python3.9 py
RUN python3.9 -m pip install --upgrade setuptools
RUN git clone https://github.com/brianyen/gbic.git && \
    cd gbic && \
    python3.9 -m pip install -r requirements.txt

CMD cd gbic && \ 
    py server.py
