# Quickstart

## Install Docker & Conda

_if you already have conda (or mamba) and docker installed you can skip to the next section. Ensure that your user is in the docker group._

The following scripts are from docker and conda documentation. They might become obsolete at some point. If so, get the last instructions from their official websites.

The docker part is **for Debian** and it's derivative. For other OS adapt the commands yourself or see official website.

**Docker**

```
# Add Docker's official GPG key:
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y -y
sudo groupadd docker
sudo usermod -aG docker $USER
```

**Miniconda**

```
curl https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh > miniconda_install.sh
bash miniconda_install.sh -b
source $HOME/miniconda3/bin/activate
conda init --all
```

**Post-install setup**

Restart your terminal to have anaconda ready to go. Then run:

```
# update user groups to see $user in group docker
exec su -l $USER
# switch conda solver for faster dependencies solving
conda update -n base conda
conda install -y -n base conda-libmamba-solver
conda config --set solver libmamba
conda config --add channels conda-forge
```

## Install Activity Browser Online

Install Activity Browser Online with conda:

```bash
conda create -n ab-online -c pan6ora activity-browser-online
conda activate ab-online
```

List sessions with:

```
ab-online list
```

Start the "example" session by running:

```
ab-online start example
```

Let docker build images and start containers. This will take some time giving AB Online has to build all necessary images. Next start will be much faster.

When it is done, you can check that containers are up and running with `docker ps --format="{{.Image}}\t{{.Names}}\t{{.Status}}"` which should return something like:

```
ab-online/local:example	example-0       Up 1 minute
ab-online/novnc:latest	example-gate    Up 1 minute
```

Open the home page at: [http://ab-online.localhost](http://ab-online.localhost)

_Nb: don't worry about your browser warning, it is because the server runs on localhost and thus cannot have a valid certificate. You might later configure a real domain name to open it outside._

Choose the only available session, then connect using **session name as login** and default password:

- login: **example**
- password: **example**

After logging in, choose the only machine of the session. A new page should open containing a working Activity Browser in your web browser !

When you are finished playing with it, shut down the session with:

```
ab-online stop example
```

## What's next ?

### Read the doc

There are multiple ways to use Activity Browser Online such as:

- using the terminal client with the `ab-online` command
- using the web api from another computer or language
- as a python library into another project

### Discover Activity Browser Online Admin Panel

A [basic web panel](https://github.com/Pan6ora/ab-online-admin) has also been developed to help administrators managing AB Online.

It uses AB Online API as a python library and launch a Flask server providing a simple web interface to interact with AB Online.

To use it simply add the package to your conda environment and launch it:

```
conda install -n ab-online -c pan6ora ab-online-admin
ab-online-admin
```

### Dig into the code

This project is not completely documented. If you wan't to take it further you will ultimately need to dig into the code.

Fortunately it is not that big. Keep it mind that it's only goal is to:

- manage a set of .json files containing an Activity Browser configuration description
- manage a set of .bw2package databases to put into these configurations
- create Docker images containing well configured Activity Browser sessions and a vnc server
- launch multiple images behind a Cadddy proxy using docker networks

### Contact me

If you are interested into working with this project (or even contributing to it !) you can contact me by:

- opening an issue or merge request on [Github](https://github.com/Pan6ora/activity-browser-online)
- sending me an email at [remy@lecalloch.net](mailto:remy@lecalloch.net)

_Nb: from July 2024 I will no longer work on this project professionally. Nevertheless I am still motivated to help people working with it. Don't hesitate to contact me, but don't worry if it take some time for me to answer._

## Potential errors

### unstable network connection

If you are having a bad network connection the build might fail because conda is unable to fetch packages for too long.

If so you only need to rebuild having a better connection.

### "no space left on device" in a Virtual Machine

If you run this in a virtual machine, AB-Online might fail saying "no space left on device".

It is likely that you have a separate logical disk for the /var folder which is too small. Docker generates huge file during images creation (can be more than 5Go !).

Run `df -h` to check it.
To increase it's size you can try something like :

```
sudo lvdisplay
sudo lvresize <LV path> -L +5g
sudo resize2fs <LV path>
```

Search on the internet for other ways to do it.
