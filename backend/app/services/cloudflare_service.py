from __future__ import annotations

import structlog
import httpx

logger = structlog.get_logger()

_CF_BASE = "https://api.cloudflare.com/client/v4"


class CloudflareService:
    def __init__(self, api_token: str, zone_id: str) -> None:
        self.api_token = api_token
        self.zone_id = zone_id

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    # ------------------------------------------------------------------ #
    # Cache purge                                                          #
    # ------------------------------------------------------------------ #

    async def purge_everything(self) -> dict:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                f"{_CF_BASE}/zones/{self.zone_id}/purge_cache",
                headers=self._headers,
                json={"purge_everything": True},
            )
            response.raise_for_status()
            data = response.json()
            logger.info("cf_purge_everything", zone=self.zone_id, success=data.get("success"))
            return data

    async def purge_files(self, urls: list[str]) -> dict:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                f"{_CF_BASE}/zones/{self.zone_id}/purge_cache",
                headers=self._headers,
                json={"files": urls},
            )
            response.raise_for_status()
            data = response.json()
            logger.info("cf_purge_files", zone=self.zone_id, count=len(urls))
            return data

    async def purge_subdomain(self, subdomain: str, base_domain: str) -> dict:
        prefix = f"https://{subdomain}.{base_domain}"
        files = [prefix + "/", prefix + "/index.html"]
        return await self.purge_files(files)

    # ------------------------------------------------------------------ #
    # Cache rules                                                          #
    # ------------------------------------------------------------------ #

    async def list_cache_rules(self) -> list[dict]:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                f"{_CF_BASE}/zones/{self.zone_id}/rulesets/phases/http_request_cache_settings/entrypoint",
                headers=self._headers,
            )
            if response.status_code == 404:
                return []
            response.raise_for_status()
            data = response.json()
            return data.get("result", {}).get("rules", [])

    # ------------------------------------------------------------------ #
    # Analytics                                                            #
    # ------------------------------------------------------------------ #

    async def get_cache_analytics(self, since_hours: int = 24) -> dict:
        query = """
        {
          viewer {
            zones(filter: {zoneTag: "%s"}) {
              httpRequests1hGroups(
                limit: %d
                filter: {datetime_geq: "now-%dh"}
              ) {
                sum { cachedBytes cachedRequests bytes requests }
                dimensions { datetimeHour }
              }
            }
          }
        }
        """ % (
            self.zone_id,
            since_hours,
            since_hours,
        )
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.cloudflare.com/client/v4/graphql",
                headers=self._headers,
                json={"query": query},
            )
            response.raise_for_status()
            return response.json()
