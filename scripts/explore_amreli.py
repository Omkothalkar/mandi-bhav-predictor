import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.services.data_service import data_service

print("Supported Mandis:")
for mandi in data_service.get_supported_mandis():
    print(mandi)
