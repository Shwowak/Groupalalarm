"""GroupAlarm Home Assistant Integration."""
from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    PLATFORMS,
    CONF_API_KEY,
    CONF_ORGANIZATION_ID,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    SERVICE_SEND_FEEDBACK,
    ATTR_ALARM_ID,
    ATTR_FEEDBACK,
    FEEDBACK_YES,
    FEEDBACK_NO,
    FEEDBACK_LATER,
)
from .coordinator import GroupAlarmCoordinator
from .groupalarm_api import GroupAlarmApi

_LOGGER = logging.getLogger(__name__)

FEEDBACK_SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ALARM_ID): int,
        vol.Required(ATTR_FEEDBACK): vol.In([FEEDBACK_YES, FEEDBACK_NO, FEEDBACK_LATER]),
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up GroupAlarm from a config entry."""
    api_key = entry.data[CONF_API_KEY]
    org_id = entry.data[CONF_ORGANIZATION_ID]
    scan_interval = entry.options.get(
        CONF_SCAN_INTERVAL, entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    )

    session = async_get_clientsession(hass)
    api = GroupAlarmApi(api_key, org_id, session)
    coordinator = GroupAlarmCoordinator(hass, api, scan_interval)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "api": api,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Service: Rückmeldung senden
    async def handle_send_feedback(call: ServiceCall) -> None:
        alarm_id = call.data[ATTR_ALARM_ID]
        feedback = call.data[ATTR_FEEDBACK]
        await api.send_feedback(alarm_id, feedback)
        _LOGGER.info("Rückmeldung '%s' für Alarm %s gesendet", feedback, alarm_id)

    hass.services.async_register(
        DOMAIN,
        SERVICE_SEND_FEEDBACK,
        handle_send_feedback,
        schema=FEEDBACK_SERVICE_SCHEMA,
    )

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, SERVICE_SEND_FEEDBACK)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload entry on options change."""
    await hass.config_entries.async_reload(entry.entry_id)
