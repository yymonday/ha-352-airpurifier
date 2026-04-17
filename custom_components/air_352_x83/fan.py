from homeassistant.components.fan import FanEntity, FanEntityFeature
from .const import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    hub = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([X83FanEntity(hub)])

class X83FanEntity(FanEntity):
    def __init__(self, hub):
        self._hub = hub
        self._attr_has_entity_name = True
        self._attr_name = None
        self._attr_unique_id = f"fan_{hub.mac}"
        
        self._attr_supported_features = (
            FanEntityFeature.SET_SPEED | 
            FanEntityFeature.TURN_ON | 
            FanEntityFeature.TURN_OFF |
            FanEntityFeature.PRESET_MODE
        )
        self._attr_speed_count = 6 
        self._attr_preset_modes = ["auto", "sleep", "turbo", "manual"]

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._hub.mac)},
            "name": f"352 {self._hub.model.upper()}空气净化器",
            "manufacturer": "352",
            "model": self._hub.model.upper()
        }

    @property
    def should_poll(self):
        return False

    async def async_added_to_hass(self):
        self._hub.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        self._hub.remove_callback(self.async_write_ha_state)

    @property
    def is_on(self):
        return self._hub.status.get("power") == "ON"

    @property
    def percentage(self):
        speed = self._hub.status.get("speed", 0)
        return int((speed / 6) * 100) if speed > 0 else 0

    @property
    def preset_mode(self):
        return self._hub.status.get("mode")

    async def async_turn_on(self, percentage=None, preset_mode=None, **kwargs):
        self._hub.status["power"] = "ON"
        self.async_write_ha_state()

        await self._hub.async_control("on")
        
        if percentage:
            await self.async_set_percentage(percentage)
        if preset_mode:
            await self.async_set_preset_mode(preset_mode)

    async def async_turn_off(self, **kwargs):
        self._hub.status["power"] = "OFF"
        self.async_write_ha_state()

        await self._hub.async_control("off")

    async def async_set_percentage(self, percentage):
        if percentage == 0:
            await self.async_turn_off()
            return
            
        speed_idx = max(1, min(6, round((percentage / 100) * 6)))
        self._hub.status["power"] = "ON"
        self._hub.status["speed"] = speed_idx
        self.async_write_ha_state()

        await self._hub.async_control(f"speed_{speed_idx}")

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        if preset_mode in self._attr_preset_modes:
            self._hub.status["power"] = "ON"
            self._hub.status["mode"] = preset_mode
            self.async_write_ha_state()

            await self._hub.async_control(preset_mode)