FROM docker.elastic.co/elasticsearch/elasticsearch:9.5.4@sha256:82ac14f43fe701992e601f4cc81e1c0d7dbc5a2576d8cd736006452925df4026
ENV PORT="8081" \
    ES_PORT="9200" \
    ES_JAVA_OPTS="-Xms256m -Xmx256m"
USER root
RUN microdnf install -y python3-3.9.25-7.el9_8.3 && microdnf clean all
COPY elasticsearch.yml /usr/share/elasticsearch/config/elasticsearch.yml
COPY rotate.py /opt/elk/rotate.py
COPY lifecycle.py /opt/elk/lifecycle.py
COPY bootstrap.py /opt/elk/bootstrap.py
COPY start.sh /opt/elk/start.sh
RUN chmod 755 /opt/elk/start.sh
ENTRYPOINT ["/bin/tini", "--", "/opt/elk/start.sh"]
