import asyncio
import socket
import logging
from homeassistant.core import HomeAssistant
from .const import DOMAIN, UDP_PORT
from .hub import X83Hub

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry):
    host = entry.data.get("host")
    mac = entry.data.get("mac")
    model = entry.data.get("model", "x83")
    
    hub = X83Hub(hass, host, mac, model)
    
    class X83Protocol(asyncio.DatagramProtocol):
        def datagram_received(self, data, addr):
            hub.parse_data(data)

    loop = asyncio.get_running_loop()
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except AttributeError:
        pass
        
    try:
        sock.bind(('0.0.0.0', UDP_PORT))
    except OSError:
        pass

    try:
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: X83Protocol(), sock=sock
        )
        hub.transport = transport
    except Exception as e:
        _LOGGER.error("无法创建 UDP 监听: %s", e)
        return False

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = hub
    await hass.config_entries.async_forward_entry_setups(entry, ["fan", "sensor", "light"])
    

    hass.loop.create_task(hub.async_control("query"))
    return True

async def async_unload_entry(hass: HomeAssistant, entry):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["fan", "sensor", "light"])
    if unload_ok:
        hub = hass.data[DOMAIN].pop(entry.entry_id)
        if hasattr(hub, 'transport') and hub.transport:
            hub.transport.close()
    return unload_ok