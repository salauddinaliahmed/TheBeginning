FROM python:2.7

WORKDIR /TheBeginning

COPY . /TheBeginning

RUN pip install --trusted-host dronekit, dronekit_sitl

ENV NAME Drone_Env

CMD ["python", "test.py"]
