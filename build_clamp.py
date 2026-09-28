"""
build_clamp.py (Shim / Forwarding Script)

Provides backwards compatibility for scripts or pipelines that import or invoke build_clamp.
The implementation and CAD outputs now reside in accessories/tower_clamp/.
"""
import os
import sys

_ACCESSORY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'accessories', 'tower_clamp')
if _ACCESSORY_DIR not in sys.path:
    sys.path.insert(0, _ACCESSORY_DIR)

from build_clamp import *

if __name__ == '__main__':
    main()
