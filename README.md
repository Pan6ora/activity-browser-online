# Activity Browser Online

Launch reproducible [Activity Browser](https://github.com/LCA-ActivityBrowser/activity-browser) sessions and distribute them using NoVNC.

**This project is a personal work. It is not maintained by the Activity Browser team.**

## Current state

This project is in early stage. Be careful that things my changed drastically at any point. 

See CHANGELOG for what is yet to be implemented. 

## Content

- [Quickstart](#quickstart)
- [What is Activity Browser Online ?](#what-is-activity-browser-online)
- [How does it work ?](#how-does-it-work)
- [Current state](#current-state)
- [Documentation](#documentation)

## Quickstart

- install Activity Browser Online with conda:

```bash
conda install -c pan6ora -c conda-forge ab-online
```

- ensure that you have Docker configured in your session
- start the example session by running:

```
ab-online start example
```

- let docker build images and start containers, then check that containers are up and running with `docker ps --format="{{.Image}}\t{{.Names}}\t{{.Status}}"` which should return something like:

```
ab-online/local:example	example-0       Up 1 minute
ab-online/novnc:latest	example-gate    Up 1 minute
```

- connect to the only machine of this session at: `http://localhost:8080/vnc.html?resize=remote&path=novnc/websockify?token=0`

## What is Activity Browser Online ?

Like SimaPRO Online, Activity Browser Online goal is to make AB available in a web browser.

The interface has two main parts :

- users sessions (Activity Browser machines accessible from the web browser)
- admin panel (a web interface to create and manage previous machines)

### Use case

This project was originally developed at the [G-SCOP laboratory](https://g-scop.grenoble-inp.fr/en) for educational purpose. When giving lessons to students in multiple universities it can be hard to have Activity Browser installed on every computer. A web browser embedded solution make things easier. It also gives the ability to manage different Activity Browser setup for different lessons.

## How does it work ?

### machine

A machine is an environment running Activity Browser and accessible through NoVNC. 
It can be seen as a virtual machine that one user can connect to.

### sessions

Sessions are used to define machines content. 

A session is described in a json files. This file describes how many machines to launch and the Activity Browser configuration :
- projects to create
- databases to import in projects
- plugins to activate in projects

See [Sessions documentation](#sessions) for more infos.

### docker containers

- Each user machine is a docker container with Activity Browser installed and setup.
- Each session has also a container with a NoVNC client.
- On top of that, a container with a proxy manage login.

The following scheme is an example with two sessions started:

![](includes/containers.png)


## Documentation

### Usage

There are 3 main ways to use AB Online:

#### From the command-line

Using the `ab-online` command you can perform many actions such as :
- start/stop/build sessions
- list active sessions
- much more...

Run `ab-online -h` for more infos, or `ab-online <some_command> -h` for infos about a specific command (ex: `ab-online start -h`).

# As a python library

AB Online can be used directly from a python script as a library:

```python
from ab_online import API

abo = API()
abo.list_sessions()
```

This can be useful to do complex stuff or create a new web interface.

# From the web interface

_not yet implemented_
 
### sessions


