FROM maven:3.9.9-eclipse-temurin-17

ARG SAFFRON_GIT_REF=bcf009f176713ced1d707324043124670827125b
ENV SAFFRON_HOME=/opt/saffron \
    SAFFRON_GIT_REF=${SAFFRON_GIT_REF} \
    STORE_LOCAL_COPY=true \
    MAVEN_OPTS="-Xms512m -Xmx3g"

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl git python3 python3-venv \
    && rm -rf /var/lib/apt/lists/* \
    && git clone https://github.com/insight-centre/saffron.git "$SAFFRON_HOME" \
    && git -C "$SAFFRON_HOME" checkout "$SAFFRON_GIT_REF" \
    && mvn -q -f "$SAFFRON_HOME/pom.xml" -DskipTests clean install \
    && python3 -m venv /opt/runner-venv

COPY docker/saffron/requirements.txt /tmp/saffron-runner-requirements.txt
RUN /opt/runner-venv/bin/pip install --no-cache-dir -r /tmp/saffron-runner-requirements.txt \
    && rm /tmp/saffron-runner-requirements.txt
COPY docker/saffron/runner.py /opt/fetcher-saffron/runner.py

WORKDIR /opt/saffron
EXPOSE 8080

CMD ["/opt/runner-venv/bin/python", "/opt/fetcher-saffron/runner.py"]
