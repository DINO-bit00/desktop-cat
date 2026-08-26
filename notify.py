"""
CLI Trigger & Notification Utility for Desktop Cat
Usage:
  python notify.py "Halo dunia!"
  python notify.py --state thinking --msg "Sedang memproses AI..."
  python notify.py --state celebrate --msg "Task Selesai! 🎉"
  python notify.py --state sleep
  python notify.py --state work --msg "Fokus coding!"
"""

import sys
import argparse
import os

# Add src to pythonpath
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.local_watcher import trigger_event


def main():
    parser = argparse.ArgumentParser(description="Send notifications and state changes to your desktop cat.")
    parser.add_argument("text", nargs="?", default=None, help="Message text to display in speech bubble.")
    parser.add_argument("-s", "--state", default=None,
                        choices=["idle", "walk", "sleep", "work", "pet", "celebrate", "thinking", "jump",
                                 "peek", "peek_left", "peek_right", "peek_bottom", "unpeek"],
                        help="Animation state to switch to.")
    parser.add_argument("-m", "--msg", default=None, help="Explicit message text (alternative to positional argument).")
    parser.add_argument("-d", "--duration", type=int, default=5, help="Duration in seconds (default: 5s).")

    args = parser.parse_args()

    message = args.msg if args.msg else args.text

    if not args.state and not message:
        parser.print_help()
        sys.exit(1)

    success = trigger_event(state=args.state, message=message, duration=args.duration)
    if success:
        print(f"[CatNotifier] Sent to cat: state={args.state}, message='{message}'")
    else:
        print("[CatNotifier] Failed to send.")


if __name__ == "__main__":
    main()
