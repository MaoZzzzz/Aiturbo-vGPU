FROM tensorflow-mps

MAINTAINER maozz

# experiment scripts
COPY scripts/init.sh /
COPY scripts/init.py /
COPY scripts/start.py /
COPY scripts/speed-monitor.py /
COPY scripts/get_podlist.py /

RUN pip install kubernetes
RUN mkdir -p /tf/benchmarks/scripts/data