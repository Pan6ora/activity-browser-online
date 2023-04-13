import os
import shutil
import pkg_resources

import docker

from .session import Session

class Controller:

    def __init__(self):
        self.data_path = pkg_resources.resource_filename(__name__, 'data')
        self.includes_path = pkg_resources.resource_filename(__name__, 'includes')
        self.storage_path = pkg_resources.resource_filename(__name__, 'storage')
        self.client = docker.from_env()
        self.sessions = self.read_sessions(f"{self.data_path}/sessions")
        
    def read_sessions(self,path):
        sessions = {}
        for file in os.listdir(path):
            session = Session(f"{path}/{file}")
            sessions[session.esc_name] = session
        return sessions

    def stop_session(self, session, reset_storage=False):

        if isinstance(session, str):
            session = self.sessions[session]

        print("  - stop existing containers")
        self.stop_containers(session)
        
        print(f"  - remove existing '{session.esc_name}' network")
        self.remove_network(session)

        if reset_storage:
            print(f"  - delete session storage")
            self.delete_storage(session)


    def start_session(self, session, force_build=False, reset_storage=False):
        """start all machines from the given session

        session: a Session object or the name of a session file from data/sessions
        force_build: wether to build session container if already exist
        reset_storage: wether to delete past runs session storage
        """
        if isinstance(session, str):
            session = self.sessions[session]
            
        print(f"Starting '{session.name}' session...")

        print("  - stop existing session")
        self.stop_session(session, reset_storage)
        
        print(f"  - create '{session.esc_name}' network")
        self.client.networks.create(session.esc_name)

        tag = "ab_online/novnc:latest"
        try:
            self.client.images.get(tag)
        except:
            print("  - build novnc image")
            self.build_novnc()         

        tag = f"ab_online/{session.ab_channel}:{session.ab_version.replace('+','')}"
        try:
            self.client.images.get(tag)
        except:
            print("  - build Activity Browser image")
            self.build_ab(session.ab_channel, session.ab_version)       
        
        try:
            self.client.images.get(session.tag)
        except docker.errors.ImageNotFound:
            force_build = True
        if force_build:
            print("  - build session image")
            self.build_machine(session)
        
        print(f"  - create storage")
        self.create_storage(session,reset_storage)
        
        print(f"  - create tokens")
        self.generate_tokens_file(session)        
        
        print(f"  - start novnc container")
        self.start_novnc_gate(session)
        
        print(f"  - start {session.machines} containers from image {session.tag}")
        for id in range(session.machines):
            self.start_machine(session, id=id)
        
        print("Done !")

    def stop_containers(self, session):
        for c in self.client.containers.list(filters={"network": session.esc_name}):
            c.stop()
        self.client.containers.prune()

    def remove_network(self, session):
        for network in self.client.networks.list():
            if network.name == session.esc_name:
                network.remove()
        self.client.networks.prune()

    def delete_storage(self, session):
        shutil.rmtree(f"{self.storage_path}/{session.esc_name}")

    def create_storage(self, session, reset_storage):
        if reset_storage:
            self.delete_storage(session)
        os.makedirs(f"{self.storage_path}/{session.esc_name}", exist_ok=True)
        #for i in range(session.machines):
        #    os.makedirs(f"{self.storage_path}/{session.esc_name}/{i}", exist_ok=True) 

    def generate_tokens_file(self, session):
        os.makedirs(f"{self.storage_path}/{session.esc_name}/novnc", exist_ok=True)
        with open(f"{self.storage_path}/{session.esc_name}/novnc/token.list", "w") as file:
            for i in range(session.machines):
                file.write(f"{i}: {session.esc_name}-{i}:5900\n")

    def start_novnc_gate(self, session):
        """create tokens and start the docker container
        with novnc client
        """
        name = f"{session.esc_name}-gate"
        self.client.containers.run("ab_online/novnc:latest",
                                   detach=True,
                                   ports= {"8080/tcp": 8080},
                                   name=name,
                                   hostname=name,
                                   network=session.esc_name,
                                   volumes={f"{self.storage_path}/{session.esc_name}/novnc": {'bind': '/root/storage', 'mode': 'ro'}}
                                   )        

    def start_machine(self, session, id=0):
        """start a new machine taking settings
        from the given session
        """
        name = f"{session.esc_name}-{id}"

        self.client.containers.run(session.tag,
                                   detach=True,
                                   name=name,
                                   hostname=name,
                                   network=session.esc_name,
                                   #volumes={f"{self.storage_path}/{session.esc_name}/{id}": {'bind': '/home/mambauser/.local/share/Brightway3', 'mode': 'rw'}}
                                   )
        

    def build_all(self):
        for session in self.sessions.values():
            self.build_machine(session)

    def build_machine(self, session):
        """create a docker image for the given session.
        This can take some time depending the amount of 
        plugins/databases but has to be done only once
        """
        plugins_install = "micromamba install -y -n base"
        plugins_list = ""
        for plugin in session.plugins.values():
            if plugin.ab_channel != "local":
                plugins_install += f" -c {plugin.ab_channel}"
                plugins_list += f" ab-plugin-{plugin.name}"
        plugins_install += f" -c conda-forge{plugins_list}"

        buildargs = {
            "plugins_install": plugins_install,
            "session_file": f"data/sessions/{session.filename}",
            "ab_channel": session.ab_channel,
            "ab_version": session.ab_version.replace('+','')
        }
        self.client.images.build(path=pkg_resources.resource_filename(__name__, '.'),
                                 dockerfile=f"{self.includes_path}/Dockerfile_machine",
                                 buildargs=buildargs,
                                 tag=session.tag,
                                 rm=True,
                                 forcerm=True)
        return session.tag

    def build_ab(self, channel, version):
        """create the activity browser image with
        given channel and version.
        """
        tag = f"ab_online/{channel}:{version.replace('+','')}"
        buildargs = {
            "ab_channel": channel,
            "ab_version": version
        }  
        self.client.images.build(path=self.includes_path,
                                 dockerfile="Dockerfile_ab",
                                 buildargs= buildargs,
                                 tag=tag,
                                 rm=True,
                                 forcerm=True)
        return tag

    def build_novnc(self):
        """create the novnc image
        """
        tag = "ab_online/novnc:latest"
        self.client.images.build(path=self.includes_path,
                                 dockerfile="Dockerfile_novnc",
                                 tag=tag,
                                 rm=True,
                                 forcerm=True)
        return tag

