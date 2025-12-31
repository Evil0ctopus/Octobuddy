import sys
from octo.core import OctoBuddy
from octo.config import CONFIG

def main():
    # Allow running: python -m examples.demo_run event_name
    event = sys.argv[1] if len(sys.argv) > 1 else "studied_python"

    buddy = OctoBuddy(CONFIG)
    buddy.handle_event(event)

if __name__ == "__main__":
    main()
