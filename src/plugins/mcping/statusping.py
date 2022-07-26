import json
import time
import socket
import struct
import re

from mcstatus import BedrockServer

def pingmc(host):
    try:
        server = BedrockServer.lookup(host)
        status = server.status()
        return f"The server {status.motd} has {status.players_online} players online and replied in {status.latency} ms. \nversion:{status.version.version}"
    except Exception as e:
        return f"The server is offline or the port is wrong: {e}"
