FROM python:3.11.2
RUN python -m pip install lci-sim-app-device
CMD [ "python", "-m", "lci-sim-app-device", "--dir=/SIM-Data" ]