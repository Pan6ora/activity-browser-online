import os
import shutil

import docker

from ..session import Session
from .. import config as CONFIG
from .storage import Storage


class Docker:
    storage_path = f"{CONFIG.STORAGE}/sessions_storage"
    if CONFIG.DEBUG:
        client = docker.from_env()
    else:
        try:
            client = docker.from_env()
        except:
            print("Warning: unable to connect to docker API")

    @classmethod
    def stop_containers(cls, session):
        for c in cls.client.containers.list(filters={"network": session.esc_name}):
            c.stop()
        cls.client.containers.prune()

    @classmethod
    def stop_proxy(cls):
        try:
            proxy = cls.client.containers.get("proxy")
            proxy.stop()
            cls.client.containers.prune()
        except:
            pass

    @classmethod
    def remove_network(cls, session):
        for network in cls.client.networks.list():
            if network.name == session.esc_name:
                network.remove()
        cls.client.networks.prune()

    @classmethod
    def create_main_network(cls):
        if not cls.client.networks.list(names="ABonline"):
            Docker.client.networks.create("ABonline")

    @classmethod
    def remove_main_network(cls):
        try:
            networks = cls.client.networks.list(names="ABonline")
            for network in networks:
                network.remove()
            cls.client.networks.prune()
        except:
            pass

    @classmethod
    def start_caddy_proxy(cls):
        """start main reverse proxy"""
        Storage.create_folder("proxy/data")
        Storage.create_folder("proxy/storage")
        Storage.create_folder("proxy/static")
        Storage.add_file(f"{CONFIG.INCLUDES}/Caddyfile", "Caddyfile", "proxy")
        Storage.add_file(f"{CONFIG.INCLUDES}/index.html",
                         "index.html", "proxy/static")
        Storage.add_file(f"{CONFIG.INCLUDES}/main.css",
                         "main.css", "proxy/static")
        proxy = cls.client.containers.run(
            "androw/caddy-security:latest",
            detach=True,
            ports={"80/tcp": 80, "443/tcp": 443},
            name="proxy",
            hostname="proxy",
            volumes={
                f"{CONFIG.STORAGE}/proxy/data": {"bind": "/data", "mode": "rw"},
                f"{CONFIG.STORAGE}/proxy/storage": {"bind": "/storage", "mode": "rw"},
                f"{CONFIG.STORAGE}/proxy/users.json": {
                    "bind": "/root/.local/caddy/users.json",
                    "mode": "rw",
                },
                f"{CONFIG.STORAGE}/proxy/Caddyfile": {
                    "bind": "/etc/caddy/Caddyfile",
                    "mode": "ro",
                },
                f"{CONFIG.STORAGE}/proxy/static": {"bind": "/home/home", "mode": "ro"},
                f"{CONFIG.STORAGE}/sessions_storage": {
                    "bind": "/home/storage",
                    "mode": "ro",
                },
            },
        )
        network = cls.get_network_by_name("ABonline")
        network.connect(proxy)

    @classmethod
    def reload_caddyfile(cls):
        proxy = cls.client.containers.get("proxy")
        proxy.exec_run(cmd="caddy reload", workdir="/etc/caddy")

    @classmethod
    def start_novnc_gate(cls, session):
        """create tokens and start the docker container
        with novnc client
        """
        gate_name = f"{session.esc_name}-gate"
        gate = cls.client.containers.run(
            "ab_online/novnc:latest",
            detach=True,
            name=gate_name,
            hostname=gate_name,
            network=session.esc_name,
            volumes={
                f"{cls.storage_path}/{session.esc_name}/novnc": {
                    "bind": "/root/storage",
                    "mode": "ro",
                }
            },
        )
        network = cls.get_network_by_name("ABonline")
        network.connect(gate)

    @classmethod
    def get_network_by_name(cls, name):
        network = cls.client.networks.list(
            names=[
                "ABonline",
            ]
        )
        return network[0]

    @classmethod
    def start_machine(cls, session, id=0):
        """start a new machine taking settings
        from the given session
        """
        name = f"{session.esc_name}-{id}"

        cls.client.containers.run(
            session.tag,
            detach=True,
            name=name,
            hostname=name,
            network=session.esc_name,
            # volumes={f"{cls.storage_path}/{session.esc_name}/{id}": {'bind': '/headless/.local/share/Brightway3', 'mode': 'rw'}}
        )

    @classmethod
    def build_all(cls):
        for session in cls.sessions.values():
            cls.build_sAyotzinapaession(session)

    @classmethod
    def build_session(cls, session):
        """create a docker image for the given session.
        This can take some time depending the amount of
        plugins/databases but has to be done only once
        """
        plugins_install = "true"
        if len(session.plugins.values()):
            plugins_install = "micromamba install -y -n base"
            plugins_list = ""
            for plugin in session.plugins.values():
                if plugin.channel != "local":
                    plugins_install += f" -c {plugin.channel}"
                    plugins_list += f" ab-plugin-{plugin.name}"
            plugins_install += f" -c conda-forge {plugins_list}"
        print(plugins_install)

        if CONFIG.DEV:
            setup_command = "python run-ab-online.py setup session.json"
            Storage.delete_folder("local_code")
            shutil.copytree(f"{CONFIG.INCLUDES}/../..",
                            f"{CONFIG.STORAGE}/local_code")
        else:
            setup_command = "ab-online setup session.json"

        tag = f"ab_online/{session.ab_channel}:{session.ab_version.replace('+','')}"
        try:
            Docker.client.images.get(tag)
        except:
            print("  - build Activity Browser image")
            Docker.build_ab(session.ab_channel, session.ab_version)

        buildargs = {
            "plugins_install": plugins_install,
            "session_file": f"sessions/{session.esc_name}.json",
            "ab_channel": session.ab_channel,
            "ab_version": session.ab_version.replace("+", ""),
            "setup_command": setup_command,
        }
        image, build_logs = cls.client.images.build(
            path=CONFIG.STORAGE,
            dockerfile=f"Dockerfile.machine",
            buildargs=buildargs,
            tag=session.tag,
            rm=True,
            forcerm=True,
        )
        if CONFIG.DEBUG:
            cls.log_docker_output(build_logs)

        Storage.delete_folder("local_code")

    @classmethod
    def log_docker_output(
        cls, generator, task_name: str = "docker command execution"
    ) -> None:
        """
        Log output to console from a generator returned from docker client
        :param Any generator: The generator to log the output of
        :param str task_name: A name to give the task, i.e. 'Build database image', used for logging
        """
        while True:
            try:
                output = generator.__next__()
                if "stream" in output:
                    output_str = output["stream"].strip("\r\n").strip("\n")
                    print(output_str)
            except StopIteration:
                print(f"{task_name} complete.")
                break
            except ValueError:
                print(f"Error parsing output from {task_name}: {output}")

    @classmethod
    def build_ab(cls, channel, version):
        """create the activity browser image with
        given channel and version.
        """
        tag = f"ab_online/{channel}:{version.replace('+','')}"
        buildargs = {"ab_channel": channel, "ab_version": version}
        cls.client.images.build(
            path=CONFIG.INCLUDES,
            dockerfile="Dockerfile.ab",
            buildargs=buildargs,
            tag=tag,
            rm=True,
            forcerm=True,
        )
        return tag

    @classmethod
    def build_novnc(cls):
        """create the novnc image"""
        tag = "ab_online/novnc:latest"
        cls.client.images.build(
            path=CONFIG.INCLUDES,
            dockerfile="Dockerfile.novnc",
            tag=tag,
            rm=True,
            forcerm=True,
        )
        return tag
