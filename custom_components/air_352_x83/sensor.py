from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    hub = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        X83Sensor(hub, "PM2.5", "pm25", "µg/m³", "mdi:air-filter"),
        X83Sensor(hub, "风量档位", "speed", "档", "mdi:fan-speed-1"),
        X83Sensor(hub, "累计净化空气量", "total_purification", "m³", "mdi:leaf-circle-outline"),
        X83Sensor(hub, "滤芯状态", "filter_installed", None, "mdi:filter-check-outline")
    ])

class X83Sensor(SensorEntity):
    def __init__(self, hub, name, key, unit, icon):
        self._hub = hub
        self._key = key
        self._attr_has_entity_name = True
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_unique_id = f"sensor_{hub.mac}_{key}"

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
    def native_value(self):
        return self._hub.status.get(self._key)