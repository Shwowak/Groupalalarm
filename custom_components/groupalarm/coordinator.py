"""DataUpdateCoordinator for GroupAlarm."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, EVENT_ALARM_RECEIVED, EVENT_ALARM_CLOSED
from .groupalarm_api import GroupAlarmApi, GroupAlarmApiError

_LOGGER = logging.getLogger(__name__)


class GroupAlarmCoordinator(DataUpdateCoordinator):
    """Koordiniert den Datenabruf von GroupAlarm."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: GroupAlarmApi,
        scan_interval: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.api = api
        self._known_alarm_ids: set[int] = set()

    async def _async_update_data(self) -> dict[str, Any]:
        """Daten von der API abrufen und Events feuern."""
        try:
            alarms = await self.api.get_active_alarms()
            recent_alarms = await self.api.get_all_alarms(limit=10)
            organization = await self.api.get_organization()
        except GroupAlarmApiError as err:
            raise UpdateFailed(f"Fehler beim Abrufen der Daten: {err}") from err

        current_alarm_ids = {alarm["id"] for alarm in alarms}

        # Neue Alarme → Event feuern
        for alarm in alarms:
            if alarm["id"] not in self._known_alarm_ids:
                _LOGGER.info("Neuer Alarm empfangen: %s", alarm.get("keyword", alarm["id"]))
                self.hass.bus.async_fire(
                    EVENT_ALARM_RECEIVED,
                    {
                        "alarm_id": alarm["id"],
                        "keyword": alarm.get("keyword", ""),
                        "message": alarm.get("message", ""),
                        "address": alarm.get("address", ""),
                        "created_at": alarm.get("created_at", ""),
                        "organization_id": alarm.get("organization_id"),
                    },
                )

        # Geschlossene Alarme → Event feuern
        for alarm_id in self._known_alarm_ids - current_alarm_ids:
            _LOGGER.info("Alarm geschlossen: %s", alarm_id)
            self.hass.bus.async_fire(
                EVENT_ALARM_CLOSED,
                {"alarm_id": alarm_id},
            )

        self._known_alarm_ids = current_alarm_ids

        return {
            "alarms": alarms,
            "active_count": len(alarms),
            "recent_alarms": recent_alarms,
            "organization": organization,
        }
