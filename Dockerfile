FROM artifactory.vorausrobotik.com/docker/voraus-build-image:latest

USER root

RUN apt-get update && apt-get install -y \
    qemu-system-x86

USER jenkins
