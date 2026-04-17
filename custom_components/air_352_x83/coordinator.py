from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

class X83UpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, hub):
        self.hub = hub
        super().__init__(
            hass,
            _LOGGER,
            name="352_x83_data",
            update_interval=timedelta(seconds=10),
        )

    async def _async_update_data(self):
        await self.hub.async_send_command("query")
        return self.hub.status