from pathlib import Path
import os
import sys

# Setup import path
runner_path = Path(__file__)
runner_dir = runner_path.parent
os.environ["RUNNER_DIRECTORY"] = str(runner_dir)
sys.path[:0] = [str(runner_dir / "src")]

from ui import UI, MapController  # noqa

if __name__ == "__main__":
    UI.push(MapController())
    UI.run()
