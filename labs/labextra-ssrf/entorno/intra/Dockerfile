# Intranet de PhantomCorp (Lab Extra SSRF). Solo vive en internalnet.
FROM debian:stable-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY server.py /opt/server.py
EXPOSE 80
CMD ["python3", "/opt/server.py"]
