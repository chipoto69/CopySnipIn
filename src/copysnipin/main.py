from __future__ import annotations

from fastapi import FastAPI
from pydantic import ValidationError

from copysnipin import __version__
from copysnipin._scaffold import scaffold_main
from copysnipin.config import format_settings_error, load_settings

app = FastAPI(title="CopySnipIn", version=__version__)


@app.get("/health")
async def health() -> dict[str, object]:
    try:
        load_settings()
    except ValidationError as exc:
        return {
            "status": "configuration_error",
            "mode": "scaffold",
            "zero_execution": True,
            "configuration_errors": format_settings_error(exc),
            "components": {
                "api": "configuration_error",
                "scanner": "not_implemented",
                "tracker": "not_implemented",
                "simulator": "not_implemented",
                "pyth_feed": "not_implemented",
                "dashboard": "not_implemented",
            },
        }
    return {
        "status": "ok",
        "mode": "scaffold",
        "zero_execution": True,
        "components": {
            "api": "ok",
            "scanner": "not_implemented",
            "tracker": "not_implemented",
            "simulator": "not_implemented",
            "pyth_feed": "not_implemented",
            "dashboard": "not_implemented",
        },
    }


def main() -> int:
    return scaffold_main("api")


if __name__ == "__main__":
    raise SystemExit(main())
