FROM kivy/buildozer

WORKDIR /app

COPY . /app

RUN cd android && \
    buildozer android debug && \
    cp bin/*.apk /root/.buildozer/bin/

CMD ["ls", "-la", "/root/.buildozer/bin/"]