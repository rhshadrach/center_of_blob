"""Run the app end to end without a window, e.g. to check a frozen build."""

from __future__ import annotations

import os
import sys
import tempfile
import traceback
from pathlib import Path
from types import TracebackType

import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow

from cellcensus import popups
from cellcensus.main import MainWindow


def smoke_test(image: str, centers: str) -> int:
    """Load an image and centers file, redraw, and save; return an exit code."""
    # No window is shown, so this also works on machines without a display.
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    problems: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        out = str(Path(tmp) / "out.csv")

        def record_error(msg: str) -> None:
            problems.append(msg)

        def centers_filename(main_window: QMainWindow, directory: str) -> str:
            return centers

        def csv_filename(main_window: QMainWindow, directory: str) -> str:
            return out

        def record_exception(
            cls: type[BaseException], exc: BaseException, tb: TracebackType | None
        ) -> None:
            problems.append("".join(traceback.format_exception(cls, exc, tb)))

        # Answer the file dialogs, and record error popups and exceptions raised
        # inside Qt slots instead of showing them; an unanswered popup would
        # block forever. setattr because ty doesn't allow assigning to functions.
        replacements = {
            "error_msg": record_error,
            "get_centers_filename": centers_filename,
            "get_csv_save_filename": csv_filename,
        }
        saved = {name: getattr(popups, name) for name in replacements}
        saved_excepthook = sys.excepthook
        for name, replacement in replacements.items():
            setattr(popups, name, replacement)
        sys.excepthook = record_exception
        _app = QApplication.instance() or QApplication(sys.argv[:1])
        window = MainWindow()
        try:
            run_steps(window, image, out, problems)
        except Exception:
            problems.append(traceback.format_exc())
        finally:
            for name, original in saved.items():
                setattr(popups, name, original)
            sys.excepthook = saved_excepthook
            window.close()

    if problems:
        for problem in problems:
            print(f"Smoke test failed: {problem}", file=sys.stderr)
        return 1
    print(
        f"Smoke test passed: {len(window.centers)} centers in "
        f"{len(window.regions)} regions."
    )
    return 0


def run_steps(window: MainWindow, image: str, out: str, problems: list[str]) -> None:
    """Exercise the app, stopping at the first step that reports a problem."""
    window.get_img_file(image)
    if problems:
        return
    if not window.has_img:
        problems.append("The image didn't load.")
        return
    window.get_centers_file()
    if problems:
        return
    if not window.centers:
        problems.append("No centers were loaded.")
        return
    # Reclassifying uses shapely, so this checks it loads and agrees with the
    # regions saved in the file.
    saved_regions = {point: c.region for point, c in window.centers.items()}
    window.classify_centers_by_regions()
    if {point: c.region for point, c in window.centers.items()} != saved_regions:
        problems.append("Reclassifying the centers changed their regions.")
        return
    window.write_csv()
    if problems:
        return
    written = pd.read_csv(out)
    if (written["kind"] == "center").sum() != len(window.centers):
        problems.append("The written CSV doesn't have every center.")
