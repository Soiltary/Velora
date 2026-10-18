import sys
import traceback
from pathlib import Path

if __name__ == '__main__':
    try:
        from velora.app import main
        raise SystemExit(main())
    except Exception:
        path = Path(__file__).resolve().parent / 'velora-error.log'
        path.write_text(traceback.format_exc(), encoding='utf-8')
        if sys.stderr:
            traceback.print_exc()
        raise SystemExit(1)
