FROM docker.elastic.co/kibana/kibana:9.5.4@sha256:b1b4cea273350ffcb67292d7b90dd034598c1627bfa3cd0783315e9237dbe737
ENV PORT="8082" \
    UI_PORT="5601" \
    NODE_OPTIONS="--max-old-space-size=1280"
COPY --chown=1000:0 kibana.yml /usr/share/kibana/config/kibana.yml
COPY --chown=1000:0 ready.cjs /opt/elk/ready.cjs
CMD ["/usr/share/kibana/node/default/bin/node", "--max-old-space-size=32", "/opt/elk/ready.cjs"]
