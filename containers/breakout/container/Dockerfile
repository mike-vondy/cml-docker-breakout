FROM ubuntu:18.04

COPY /breakout /opt/breakout/breakout
COPY /config.yaml /opt/breakout/config.yaml
COPY /labs.yaml /opt/breakout/labs.yaml

# User Specific Env Variables to be set during the Docker spin up.
ENV BREAKOUT_USERNAME = "username"
ENV BREAKOUT_PASSWORD = "password"
ENV BREAKOUT_UI_SERVER_PORT = "userport"
ENV BREAKOUT_CONSOLE_START_PORT = ""
ENV BREAKOUT_VNC_START_PORT = ""
ENV BREAKOUT_LAB_CONFIG_NAME = "labs.yaml"

# Need to find a way to dynamically open ports for UI and for CONSOLE/VNC Ports of Each user...
# NGINX Proxy to distribute ports?
WORKDIR /opt/breakout
CMD ["./breakout", "ui"]