from random import randint
from typing import TYPE_CHECKING, Dict, Sequence

from app.models.proxy import ProxyHostSecurity
from app.utils.store import DictStorage
from app.utils.system import check_port
from app.xray import operations
from app.xray.config import XRayConfig
from app.xray.core import XRayCore
from app.xray.node import XRayNode
from config import XRAY_ASSETS_PATH, XRAY_EXECUTABLE_PATH, XRAY_JSON
from xray_api import XRay as XRayAPI
from xray_api import exceptions
from xray_api import exceptions as exc
from xray_api import types

# Search for a free API port
try:
    for api_port in range(randint(10000, 60000), 65536):
        if not check_port(api_port):
            break
finally:
    config = XRayConfig(XRAY_JSON, api_port=api_port)
    del api_port


core = XRayCore(XRAY_EXECUTABLE_PATH, XRAY_ASSETS_PATH)
api = XRayAPI(config.api_host, config.api_port)
nodes: Dict[int, XRayNode] = {}


if TYPE_CHECKING:
    from app.db.models import ProxyHost


@DictStorage
def hosts(storage: dict):
    from app.db import GetDB, crud

    storage.clear()
    with GetDB() as db:
        for inbound_tag in config.inbounds_by_tag:
            inbound_hosts: Sequence[ProxyHost] = crud.get_hosts(db, inbound_tag)

            storage[inbound_tag] = [
                {
                    "remark": host.remark,
                    "address": host.address,
                    "port": host.port,
                    "sni": host.sni,
                    "host": host.host,
                    # None means the tls is not specified by host itself and
                    #  complies with its inbound's settings.
                    "tls": None
                    if host.security == ProxyHostSecurity.inbound_default
                    else host.security == ProxyHostSecurity.tls,
                } for host in inbound_hosts
            ]


__all__ = [
    "config",
    "hosts",
    "core",
    "api",
    "nodes",
    "operations",
    "exceptions",
    "exc",
    "types",
    "XRayConfig",
    "XRayCore",
    "XRayNode",
]
