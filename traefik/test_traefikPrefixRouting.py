"""
Test
"""
import traefikUtils

import pytest
import requests

from subprocess import Popen, PIPE

def traefikRoutesToCorrectBackend(path, expectedPort):
    baseUrl = "http://localhost:" + str(traefikUtils.getPort("traefik"))
    resp = requests.get(baseUrl + path)
    """
        If we get the expected port, it means traefik
        routed the request to the right backend
    """
    assert int(resp.text) == expectedPort

def test_routing():
    traefikPort        = traefikUtils.getPort("traefik")
    defaultBackendPort = traefikUtils.getPort("defaultBackend")
    firstBackendPort   = traefikUtils.getPort("firstBackend")
    secondBackendPort  = traefikUtils.getPort("secondBackend")

    traefik        = Popen(["traefik", "-c traefik.toml"],
                            stdout=PIPE)
    defaultBackend = Popen(["python", "dummyHttpServer.py",str(defaultBackendPort)],
                            stdout=PIPE)
    firstBackend   = Popen(["python", "dummyHttpServer.py", str(firstBackendPort)],
                            stdout=PIPE)
    secondBackend  = Popen(["python", "dummyHttpServer.py", str(secondBackendPort)],
                            stdout=PIPE)

    try:
        """
            Before sending HTTP requests to traefik (and to the backends)
            we need to make sure the services are up and ready
        """
        assert traefikUtils.checkHostUp("localhost", traefikPort)        == True
        assert traefikUtils.checkHostUp("localhost", defaultBackendPort) == True
        assert traefikUtils.checkHostUp("localhost", firstBackendPort)   == True
        assert traefikUtils.checkHostUp("localhost", secondBackendPort)  == True

        traefikRoutesToCorrectBackend("/otherthings", defaultBackendPort)
        traefikRoutesToCorrectBackend("/user/somebody", defaultBackendPort)
        traefikRoutesToCorrectBackend("/user/first", firstBackendPort)
        traefikRoutesToCorrectBackend("/user/second", secondBackendPort)
        traefikRoutesToCorrectBackend("/user/first/otherthings", firstBackendPort)
        traefikRoutesToCorrectBackend("/user/second/otherthings", secondBackendPort)

    finally:
        defaultBackend.kill()
        firstBackend.kill()
        secondBackend.kill()
        traefik.kill()

        defaultBackend.wait()
        firstBackend.wait()
        secondBackend.wait()
        traefik.wait()
