"""Services for retrieving real environmental context."""

import json
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from urllib.parse import urlencode


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_open_meteo_weather(
    latitude: float,
    longitude: float,
) -> dict:
    """Fetch current weather context from Open-Meteo."""

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,precipitation",
        "temperature_unit": "celsius",
        "precipitation_unit": "mm",
        "timezone": "UTC",
    }

    url = f"{OPEN_METEO_URL}?{urlencode(params)}"

    request = Request(
        url,
        headers={
            "User-Agent": "AquaGuard-AI/0.1",
        },
    )

    try:
        with urlopen(request, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(
            f"Open-Meteo request failed: {exc}"
        ) from exc

    current = data.get("current")

    if not current:
        raise RuntimeError(
            "Open-Meteo returned no current weather data."
        )

    return {
        "latitude": latitude,
        "longitude": longitude,
        "observed_at": current.get(
            "time",
            datetime.now(timezone.utc).isoformat(),
        ),
        "temperature_2m": current.get("temperature_2m"),
        "precipitation": current.get("precipitation"),
        "source": "open_meteo",
        "is_simulated": False,
    }