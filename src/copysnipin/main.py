from __future__ import annotations

from fastapi import FastAPI

from copysnipin import __version__
from copysnipin._scaffold import scaffold_main

app = FastAPI(title="CopySnipIn", version=__version__)


@app.get("/health")
async def health() -> dict[str, object]:
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


def run_api_server() -> None:
    """Run the FastAPI application via uvicorn."""
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8090)


def main() -> int:
    """Scaffold status check; use run_api_server() to launch the actual server."""
    return scaffold_main("api")


if __name__ == "__main__":
    raise SystemExit(main())