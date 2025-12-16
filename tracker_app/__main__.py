import sys
from pathlib import Path

# Add project root to sys.path to allow running as script
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from tracker_app.cli import app

if __name__ == "__main__":
    app()
