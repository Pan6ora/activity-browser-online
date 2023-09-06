# Quickstart

- install Activity Browser Online with conda:

```bash
conda create -n ab-online -c pan6ora -c conda-forge activity-browser-online
conda activate ab-online
```

- ensure that you have Docker installed and configured
- start the example session by running:

```
ab-online start example
```

- let docker build images and start containers, then check that containers are up and running with `docker ps --format="{{.Image}}\t{{.Names}}\t{{.Status}}"` which should return something like:

```
ab-online/local:example	example-0       Up 1 minute
ab-online/novnc:latest	example-gate    Up 1 minute
```

- connect to the only machine of this session at: [http://localhost:8080/vnc.html?resize=remote&path=novnc/websockify?token=0](http://localhost:8080/vnc.html?resize=remote&path=novnc/websockify?token=0)