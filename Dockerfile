FROM kivy/kivy:2.3.0-python3.11-sd

WORKDIR /app

COPY . /app

RUN cd android && \
    buildozer android debug && \
    cp bin/*.apk /root/.buildozer/bin/

CMD ["ls", "-la", "/root/.buildozer/bin/"]