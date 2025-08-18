FROM artifactory.vorausrobotik.com/docker/voraus-build-image:latest

USER root

RUN apt-get update && apt-get install -y \
    libarchive-tools \
    xorriso \
    qemu-system-x86

USER jenkins
