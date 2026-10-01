FROM docker.elastic.co/logstash/logstash:9.5.4@sha256:75a495fa0ce94f44da25b7458bf6bf68bb3e4ecde8cdd00cc4376d78fa64e1e7
ENV PORT="9600" \
    INPUT_PORT="8080" \
    INPUT_USER="shipper" \
    LS_JAVA_OPTS="-Xms256m -Xmx256m -XX:MaxDirectMemorySize=128m"
USER root
COPY logstash.yml /usr/share/logstash/config/logstash.yml
RUN rm -f /usr/share/logstash/pipeline/logstash.conf
COPY pipeline.conf /usr/share/logstash/pipeline/logstash.conf
COPY start.sh /opt/elk/start.sh
RUN chmod 755 /opt/elk/start.sh
ENTRYPOINT ["/opt/elk/start.sh"]
