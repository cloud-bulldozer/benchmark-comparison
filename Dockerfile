FROM ubuntu

WORKDIR /tmp
ARG DEBIAN_FRONTEND=noninteractive

# Install necessary libraries for subsequent commands
RUN apt-get update && apt-get install -y podman wget vim git dumb-init python3.6 python3-distutils python3-pip python3-apt

# Install and setup snafu for storing vegeta results into ES
RUN mkdir -p /opt/touchstone/ \
 && git clone https://github.com/cloud-bulldozer/benchmark-comparison \
 && cd benchmark-comparison \
 && cp -R . /opt/touchstone/ \
 && pip3 install --upgrade pip \
 && pip3 install -e /opt/touchstone/

# Cleanup the installation remainings
RUN apt-get clean autoclean && \
    apt-get autoremove --yes && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/

# Start the command
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
# Keeping this command as sleep infinity for now.
# Can be changed according to the development requirements.
CMD ["sleep", "infinity"]