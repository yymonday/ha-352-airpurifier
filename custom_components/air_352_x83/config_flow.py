import socket
import asyncio
import logging
import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, UDP_PORT, MODELS

_LOGGER = logging.getLogger(__name__)

class X83ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        
        if user_input is not None:
            host = user_input["host"]
            mac = user_input["mac"].replace(":", "").upper()
            model = user_input["model"]
            
            return self.async_create_entry(title=f"352 {model.upper()} ({host})", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("model", default="x83"): vol.In(MODELS),
                vol.Required("host", default="192.168.50.18"): str,
                vol.Required("mac", default="00:95:69:D7:9B:FE"): str,
            }),
            errors=errors,
        )