#!/usr/bin/env python3
"""Cross-platform GUI for generating tracksheet Excel files using pywebview."""

import json
import sys
import threading
import webbrowser
from datetime import datetime
from pathlib import Path

import webview

from gen_tracksheet import build_tracksheet


class Api:
    def __init__(self) -> None:
        self._window = None

    def set_window(self, window) -> None:
        self._window = window

    def add_files(self) -> list[dict] | None:
        result = self._window.create_file_dialog(
            webview.FileDialog.OPEN,
            allow_multiple=True,
            file_types=("CSV files (*.csv)",),
        )
        if not result:
            return None
        return [{"name": Path(p).name, "path": p} for p in result]

    def generate(self, paths: list[str]) -> dict:
        now = datetime.now()
        generated = []
        errors = []

        for p in paths:
            csv_path = Path(p)
            if not csv_path.exists():
                errors.append(f"{csv_path.name}: File not found")
                continue
            try:
                build_tracksheet(csv_path, now)
                generated.append(csv_path.stem)
            except Exception as e:
                errors.append(f"{csv_path.name}: {e}")

        return {"count": len(generated), "errors": errors}


def main() -> None:
    api = Api()

    html_path = Path(__file__).parent / "assets" / "index.html"
    url = html_path.as_uri() if html_path.exists() else ""

    window = webview.create_window(
        title="Tracksheet Generator",
        url=url,
        js_api=api,
        width=640,
        height=520,
        resizable=True,
        min_size=(480, 400),
    )
    api.set_window(window)

    webview.start(debug="--debug" in sys.argv)


if __name__ == "__main__":
    main()
