"""Sensor platform for GroupAlarm."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
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
    async_add_entities([
        GroupAlarmActiveCountSensor(coordinator, entry),
        GroupAlarmLatestAlarmSensor(coordinator, entry),
        GroupAlarmRecentAlarmsSensor(coordinator, entry),
    ])


class GroupAlarmBaseEntity(CoordinatorEntity):
    """Base entity für GroupAlarm."""

    def __init__(self, coordinator: GroupAlarmCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "GroupAlarm",
            "manufacturer": "GroupAlarm GmbH",
            "model": "Cloud Service",
        }


class GroupAlarmActiveCountSensor(GroupAlarmBaseEntity, SensorEntity):
    """Anzahl aktiver Alarme."""

    _attr_icon = "mdi:alarm-light"
    _attr_native_unit_of_measurement = "Alarme"

    def __init__(self, coordinator: GroupAlarmCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_active_alarms"
        self._attr_name = "GroupAlarm Aktive Alarme"

    @property
    def native_value(self):
        if not self.coordinator.data:
            return 0
        return self.coordinator.data.get("active_count", 0)

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}
        alarms = self.coordinator.data.get("alarms", [])
        return {
            "alarm_ids": [a["id"] for a in alarms],
            "keywords": [a.get("keyword", "") for a in alarms],
        }


class GroupAlarmLatestAlarmSensor(GroupAlarmBaseEntity, SensorEntity):
    """Letzter / aktuellster Alarm."""

    _attr_icon = "mdi:alarm-bell"

    def __init__(self, coordinator: GroupAlarmCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_latest_alarm"
        self._attr_name = "GroupAlarm Letzter Alarm"

    @property
    def native_value(self) -> str:
        if not self.coordinator.data:
            return "kein Alarm"
        # Zuerst aktive, dann letzte Alarme prüfen
        alarms = self.coordinator.data.get("alarms", [])
        if not alarms:
            alarms = self.coordinator.data.get("recent_alarms", [])
        if not alarms:
            return "kein Alarm"
        latest = alarms[0]
        event = latest.get("event", {})
        return event.get("name", latest.get("message", str(latest["id"]))[:50])

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}
        alarms = self.coordinator.data.get("alarms", [])
        if not alarms:
            alarms = self.coordinator.data.get("recent_alarms", [])
        if not alarms:
            return {}
        latest = alarms[0]
        event = latest.get("event", {})
        return {
            "alarm_id": latest.get("id"),
            "keyword": event.get("name", ""),
            "message": latest.get("message", ""),
            "address": latest.get("address", ""),
            "created_at": latest.get("startDate", ""),
            "status": "aktiv" if not latest.get("endDate") else "abgeschlossen",
        }


class GroupAlarmRecentAlarmsSensor(GroupAlarmBaseEntity, SensorEntity):
    """Die letzten 10 Alarme (aktiv + abgeschlossen)."""

    _attr_icon = "mdi:history"
    _attr_native_unit_of_measurement = "Alarme"

    def __init__(self, coordinator: GroupAlarmCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_recent_alarms"
        self._attr_name = "GroupAlarm Letzte Alarme"

    @property
    def native_value(self) -> int:
        if not self.coordinator.data:
            return 0
        return len(self.coordinator.data.get("recent_alarms", []))

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {"alarms": []}
        recent = self.coordinator.data.get("recent_alarms", [])
        return {
            "alarms": [
                {
                    "alarm_id": a.get("id"),
                    "keyword": a.get("event", {}).get("name", ""),
                    "message": a.get("message", ""),
                    "address": a.get("address", ""),
                    "created_at": a.get("startDate", ""),
                    "status": "abgeschlossen" if a.get("endDate") else "aktiv",
                }
                for a in recent
            ]
        }
