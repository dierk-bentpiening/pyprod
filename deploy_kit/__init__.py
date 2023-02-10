import sys
if sys.version_info[0] >= 3:
    from .errkit3 import ProductionErrorKit
else:
    from .errkit2 import ProductionErrorKit
