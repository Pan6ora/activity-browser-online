import os
import shutil

import docker

from ..session import Session
from .. import config
from .storage import Storage

class Docker:

    storage_path = f"{config.STORAGE}/sessions_storage"
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
    def remove_main_network(cls):
        try:
            networks = cls.client.networks.list(names="ABonline")
            for network in networks:
                network.remove()
            cls.client.networks.prune()
        except:
            pass

    @classmethod
    def update_Caddyfile(cls):
        print("NOT YET IMPLEMENTED")
        pass

    @classmethod
    def start_caddy_proxy(cls):
        """start main reverse proxy
        """
        Storage.create_folder("proxy/data")
        Storage.create_folder("proxy/storage")
        Storage.create_folder("proxy/static")
        Storage.add_file(f"{config.INCLUDES}/Caddyfile","Caddyfile","proxy")
        Storage.add_file(f"{config.INCLUDES}/index.html","index.html","proxy/static")
        proxy = cls.client.containers.run("androw/caddy-security:latest",
                                   detach=True,
                                   ports= {"80/tcp": 80,
                                           "443/tcp": 443
                                           },
                                   name="proxy",
                                   hostname="proxy",
                                   volumes={f"{config.STORAGE}/proxy/data": {'bind': '/data', 'mode': 'rw'},
                                            f"{config.STORAGE}/proxy/storage": {'bind': '/storage', 'mode': 'rw'},
                                            f"{config.STORAGE}/proxy/Caddyfile": {'bind': '/etc/caddy/Caddyfile', 'mode': 'ro'},
                                            f"{config.STORAGE}/proxy/static": {'bind': '/home/home', 'mode': 'ro'},
                                            f"{config.STORAGE}/sessions_storage": {'bind': '/home/storage', 'mode': 'ro'}
                                           }
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
        gate = cls.client.containers.run("ab_online/novnc:latest",
                                   detach=True,
                                   name=gate_name,
                                   hostname=gate_name,
                                   network=session.esc_name,
                                   volumes={f"{cls.storage_path}/{session.esc_name}/novnc": {'bind': '/root/storage', 'mode': 'ro'}}
                                   )
        network = cls.get_network_by_name("ABonline")
        network.connect(gate)

    @classmethod
    def get_network_by_name(cls, name):
        network = cls.client.networks.list(names=["ABonline",])
        return network[0]
       
    @classmethod
    def start_machine(cls, session, id=0):
        """start a new machine taking settings
        from the given session
        """
        name = f"{session.esc_name}-{id}"

        cls.client.containers.run(session.tag,
                                   detach=True,
                                   name=name,
                                   hostname=name,
                                   network=session.esc_name,
                                   #volumes={f"{cls.storage_path}/{session.esc_name}/{id}": {'bind': '/home/mambauser/.local/share/Brightway3', 'mode': 'rw'}}
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
        plugins_install = "micromamba install -y -n base"
        plugins_list = ""
        for plugin in session.plugins.values():
            if plugin.channel != "local":
                plugins_install += f" -c {plugin.channel}"
                plugins_list += f" ab-plugin-{plugin.name}"
        plugins_install += f" -c conda-forge {plugins_list}"

        if config.DEV:
            setup_command = "python run-ab-online.py setup session.json"
            Storage.delete_folder("local_code")
            shutil.copytree(f"{config.INCLUDES}/../..", f"{config.STORAGE}/local_code")
        else:
            setup_command = "ab-online setup session.json"

        tag = f"ab_online/{session.ab_channel}:{session.ab_version.replace('+','')}"
        try:
            Docker.client.images.get(tag)
        except:
            print("  - build Activity Browser image")
            Docker.build_ab(session.ab_channel, session.ab_version)  

        print(plugins_install)
        buildargs = {
            "plugins_install": plugins_install,
            "session_file": f"sessions/{session.esc_name}.json",
            "ab_channel": session.ab_channel,
            "ab_version": session.ab_version.replace('+',''),
            "setup_command": setup_command
        }
        image, build_logs = cls.client.images.build(path=config.STORAGE,
                                 dockerfile=f"Dockerfile_machine",
                                 buildargs=buildargs,
                                 tag=session.tag,
                                 rm=True,
                                 forcerm=True)
        cls.log_docker_output(build_logs)

        if config.DEV:
            Storage.delete_folder("local_code")

    @classmethod
    def log_docker_output(cls, generator, task_name: str = 'docker command execution') -> None:
        """
        Log output to console from a generator returned from docker client
        :param Any generator: The generator to log the output of
        :param str task_name: A name to give the task, i.e. 'Build database image', used for logging
        """
        while True:
            try:
                output = generator.__next__()
                if 'stream' in output:
                    output_str = output['stream'].strip('\r\n').strip('\n')
                    print(output_str)
            except StopIteration:
                print(f'{task_name} complete.')
                break
            except ValueError:
                print(f'Error parsing output from {task_name}: {output}')

    @classmethod
    def build_ab(cls, channel, version):
        """create the activity browser image with
        given channel and version.
        """
        tag = f"ab_online/{channel}:{version.replace('+','')}"
        buildargs = {
            "ab_channel": channel,
            "ab_version": version
        }  
        cls.client.images.build(path=config.INCLUDES,
                                 dockerfile="Dockerfile_ab",
                                 buildargs= buildargs,
                                 tag=tag,
                                 rm=True,
                                 forcerm=True)
        return tag

    @classmethod
    def build_novnc(cls):
        """create the novnc image
        """
        tag = "ab_online/novnc:latest"
        cls.client.images.build(path=config.INCLUDES,
                                 dockerfile="Dockerfile_novnc",
                                 tag=tag,
                                 rm=True,
                                 forcerm=True)
        return tag

