import sys

from .client import Client

def run_ab_online():

    client = Client()
    args = sys.argv[1:]

    if len(args) == 0:
        while(True):
            cmd = input("ab-online > ")
            client.run(cmd)
    else:
        client.run(args)
