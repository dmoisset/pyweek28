#!/usr/bin/env python3
from pathlib import Path
import os
import sys

# Setup import path
runner_path = Path(__file__)
runner_dir = runner_path.parent
os.environ["RUNNER_DIRECTORY"] = str(runner_dir)
sys.path[:0] = [str(runner_dir / "src")]

from ui import UI  # noqa
from controllers.intro import IntroController  # noqa

if __name__ == "__main__":
    # Check dependencies
    if sys.version_info < (3, 6, 0):
        print("Python 3.6 or newer is required!")
    try:
        from wasabi2d import keymods  # noqa
    except ImportError:
        print("run: pip install git+https://github.com/lordmauve/wasabi2d.git@669e0072")

    try:
        import typing_extensions  # noqa
    except ImportError:
        print("run: pip install typing_extensions")

    try:
        import dataclasses  # noqa
    except ImportError:
        print("run: pip install dataclasses")

    # Run game
    UI.push(IntroController())
    UI.run()
