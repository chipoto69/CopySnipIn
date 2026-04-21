from __future__ import annotations

from dataclasses import dataclass

from pydantic import ValidationError

from copysnipin.config import format_settings_error, load_settings


@dataclass(frozen=True)
class ScaffoldStatus:
    component: str
    status: str = "scaffold"
    not_implemented: bool = True
    zero_execution: bool = True


def status_line(component: str) -> str:
    status = ScaffoldStatus(component=component)
    try:
        settings = load_settings()
    except ValidationError as exc:
        return (
            f"copysnipin.{status.component}: status=configuration_error "
            f"not_implemented={str(status.not_implemented).lower()} "
            f"zero_execution={str(status.zero_execution).lower()} "
            f"settings_errors={format_settings_error(exc)}"
        )
    return (
        f"copysnipin.{status.component}: status={status.status} "
        f"not_implemented={str(status.not_implemented).lower()} "
        f"zero_execution={str(status.zero_execution).lower()}"
        f" settings={settings.safe_public_status()['settings_mode']}"
    )


def scaffold_main(component: str) -> int:
    line = status_line(component)
    print(line)
    return 1 if "status=configuration_error" in line else 0
