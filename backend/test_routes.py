import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app

print("Current Registered Routes:")
for route in app.routes:
    print(getattr(route, "path", route.name))
