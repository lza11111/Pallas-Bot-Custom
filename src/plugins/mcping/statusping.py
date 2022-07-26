import json
from pydoc import describe
import time
import socket
import struct
import re

from mcstatus import BedrockServer, JavaServer

from urllib.parse import urlparse
from typing import Optional, Tuple

from .anthor import StatusPing

def _valid_urlparse(address: str) -> Tuple[str, Optional[int]]:
    """Parses a string address like 127.0.0.1:25565 into host and port parts

    If the address doesn't have a specified port, None will be returned instead.

    :raises ValueError:
        Unable to resolve hostname of given address
    """
    tmp = urlparse("//" + address)
    if not tmp.hostname:
        raise ValueError(f"Invalid address '{address}', can't parse.")

    return tmp.hostname, tmp.port

def parse_address(address: str, *, default_port: Optional[int] = None) -> Tuple[str, Optional[int]]:
        """Parses a string address like 127.0.0.1:25565 into host and port parts

        If the address has a port specified, use it, if not, fall back to default_port.

        :raises ValueError:
            Either the address isn't valid and can't be parsed,
            or it lacks a port and `default_port` wasn't specified.
        """
        hostname, port = _valid_urlparse(address)
        if port is None:
            if default_port is not None:
                port = default_port
            else:
                raise ValueError(
                    f"Given address '{address}' doesn't contain port and default_port wasn't specified, can't parse."
                )
        return hostname, port

def pingmc(host):
    text = ""
    try:
        hostname, port = parse_address(host, default_port=19132)
        server = BedrockServer(hostname, port)
        status = server.status()
        text += f"The server {status.motd} has {status.players_online} players online and replied in {status.latency} ms. \nversion:{status.version.version}"
    except Exception as e:
        text += f"The server {host} isn't BDS. \n{e}\n"
        try:
            hostname, port = parse_address(host, default_port=25565)
            server = JavaServer(hostname, port)
            status = server.status()
            text += f"The server {status.description} has {status.players.online} players online and replied in {status.latency} ms. \nversion:{status.version}"
        except Exception as e:
            text += f"The server {host} fetch failed. \n{e}\n"
            try:
                hostname, port = parse_address(host, default_port=25565)
                get_status = StatusPing(host, port).get_status()
                get_status = json.dumps(get_status)
                get_status = re.sub(r"\\u00a7.", "", get_status)
                get_status = json.loads(get_status)
                description = get_status["description"]["text"]
                ping = get_status["ping"]
                version = get_status["version"]["name"]
                players = get_status["players"]["online"]
                text += f"The server {description} has {players} players online and replied in {ping} ms. \nversion:{version}"
            except Exception as e:
            # print(get_status)
                text += f"The server is offline or the port is wrong. \n{e}\n"
    return text
