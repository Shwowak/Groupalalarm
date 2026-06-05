"""Binary sensor platform for GroupAlarm."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import GroupAlarmCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: GroupAlarmCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([GroupAlarmActiveSensor(coordinator, entry)])


class GroupAlarmActiveSensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor: True wenn mindestens 1 Alarm aktiv ist."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_icon = "mdi:alarm-light-outline"

    def __init__(self, coordinator: GroupAlarmCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_alarm_active"
        self._attr_name = "GroupAlarm Alarm Aktiv"
        self._entry = entry

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get("active_count", 0) > 0

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "GroupAlarm",
            "manufacturer": "GroupAlarm GmbH",
            "model": "Cloud Service",
        }
