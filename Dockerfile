FROM python:3.7.3
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install lci-sim-app-device
CMD [ "python3", "-m", "lci-sim-app-device", "--dir=/SIM-Data" ]