"""GroupAlarm API client."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp

from .const import API_BASE_URL, API_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class GroupAlarmApiError(Exception):
    """General API error."""


class GroupAlarmAuthError(GroupAlarmApiError):
    """Authentication error."""


class GroupAlarmApi:
    """Async GroupAlarm API client."""

    def __init__(self, api_key: str, organization_id: int, session: aiohttp.ClientSession) -> None:
        self._api_key = api_key
        self._organization_id = organization_id
        self._session = session

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Personal-Access-Token": self._api_key,
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> Any:
        url = f"{API_BASE_URL}{endpoint}"
        try:
            async with self._session.request(
                method,
                url,
                headers=self._headers,
                timeout=aiohttp.ClientTimeout(total=API_TIMEOUT),
                **kwargs,
            ) as resp:
                if resp.status == 401:
                    raise GroupAlarmAuthError("Ungültiger API-Key")
                if resp.status == 403:
                    raise GroupAlarmAuthError("Kein Zugriff auf diese Organisation")
                resp.raise_for_status()
                return await resp.json()
        except aiohttp.ClientError as err:
            raise GroupAlarmApiError(f"Verbindungsfehler: {err}") from err

    async def validate_auth(self) -> bool:
        """Validate API key by fetching organization info."""
        await self._request("GET", f"/organization/{self._organization_id}")
        return True

    async def get_organization(self) -> dict[str, Any]:
        """Get organization details."""
        return await self._request("GET", f"/organization/{self._organization_id}")

    async def get_active_alarms(self) -> list[dict[str, Any]]:
        """Get all currently active alarms for the organization."""
        result = await self._request(
            "GET",
            "/alarm",
            params={"organization_id": self._organization_id, "status": "active"},
        )
        if isinstance(result, list):
            return result
        return result.get("alarms", [])

    async def get_all_alarms(self, limit: int = 10, offset: int = 0) -> list[dict[str, Any]]:
        """Get all alarms (active + closed) for the organization, newest first."""
        result = await self._request(
            "GET",
            "/alarms",
            params={
                "organization": self._organization_id,
                "type": "all",
                "limit": min(limit, 50),
                "offset": offset,
            },
        )
        if isinstance(result, list):
            return result
        return result.get("alarms", [])

    async def get_alarm(self, alarm_id: int) -> dict[str, Any]:
        """Get details of a specific alarm."""
        return await self._request("GET", f"/alarm/{alarm_id}")

    async def get_units(self) -> list[dict[str, Any]]:
        """Get all units in the organization."""
        result = await self._request(
            "GET",
            "/unit",
            params={"organization_id": self._organization_id},
        )
        if isinstance(result, list):
            return result
        return result.get("units", [])

    async def send_feedback(self, alarm_id: int, feedback: str) -> None:
        """Send alarm feedback (yes/no/later)."""
        feedback_map = {"yes": 1, "no": 2, "later": 3}
        feedback_value = feedback_map.get(feedback, 1)
        await self._request(
            "POST",
            f"/alarm/{alarm_id}/feedback",
            json={"status": feedback_value},
        )
