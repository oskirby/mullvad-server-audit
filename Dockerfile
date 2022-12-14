FROM ubuntu:jammy

ENV DEBIAN_FRONTEND="noninteractive"

RUN \
  echo "---- Installing Dependencies ----" && \
  apt-get update && \
  apt-get install -y --no-install-recommends \
    speedtest-cli \
    wireguard \
    wireguard-tools

