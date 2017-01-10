"""
This module exposes Home Assistant via Zeroconf.

Zeroconf is also known as Bonjour, Avahi or Multicast DNS (mDNS).

For more details about Zeroconf, please refer to the documentation at
https://home-assistant.io/components/zeroconf/
"""
import logging
import socket

from homeassistant.const import (EVENT_HOMEASSISTANT_STOP, __version__)

REQUIREMENTS = ["zeroconf==0.17.6"]

DEPENDENCIES = ["api"]

_LOGGER = logging.getLogger(__name__)

DOMAIN = "zeroconf"

ZEROCONF_TYPE = "_domo._tcp.local."

from zeroconf import Zeroconf, ServiceInfo, BadTypeInNameException

zeroconf = Zeroconf()

def setup(hass, config):
    """Set up Zeroconf and make Home Assistant discoverable."""

    zeroconf_name = "{}.{}".format(hass.config.location_name,
                                   ZEROCONF_TYPE)
    # logging.getLogger('zeroconf').setLevel(logging.DEBUG)

    requires_api_password = (hass.config.api.api_password is not None)
    params = {"version": __version__, "base_url": hass.config.api.base_url,
              "requires_api_password": requires_api_password}

    info = ServiceInfo(ZEROCONF_TYPE, zeroconf_name,
                       socket.inet_aton(hass.config.api.host),
                       hass.config.api.port, 0, 0, params)
    _LOGGER.info("Zeroconf service information: %s", info)
    try:
        zeroconf.register_service(info)
    except BadTypeInNameException:
        _LOGGER.error("Exception raised by zeroconf register_service, "
                      "data that was tried to register: %s", info)

    def stop_zeroconf(event):
        """Stop Zeroconf."""
        zeroconf.unregister_service(info)
        zeroconf.close()

    hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, stop_zeroconf)

    return True
