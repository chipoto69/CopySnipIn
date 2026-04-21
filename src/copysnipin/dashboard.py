from __future__ import annotations

from textual.app import App

from copysnipin._scaffold import scaffold_main


class CopySnipInDashboard(App[None]):
    pass


def main() -> int:
    return scaffold_main("dashboard")


if __name__ == "__main__":
    raise SystemExit(main())
