import os
import urllib.request
import time

# Create directories
directories = [
    "data/raw",
    "data/processed",
    "ml/preprocessing",
    "ml/training",
    "ml/evaluation",
    "ml/models",
    "backend/app/api",
    "backend/app/services",
    "frontend",
    "scripts",
    "docs",
    "notebooks"
]

for d in directories:
    os.makedirs(d, exist_ok=True)

print("Directories created successfully.")

# Download configuration
base_url = "https://raw.githubusercontent.com/iancovert/Agmarknet/master"
crops = ["Wheat", "Rice"]
years = ["2012", "2013", "2014", "2015", "2016", "2017"]
data_dir = "data/raw"

def download_file(url, filepath):
    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        print(f"Already exists: {filepath}")
        return
        
    print(f"Downloading {url} -> {filepath}")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=10) as response, open(filepath, 'wb') as out_file:
                data = response.read()
                out_file.write(data)
            print(f"Success: {filepath} ({len(data)} bytes)")
            break
        except Exception as e:
            print(f"Error downloading {url} on attempt {attempt+1}: {e}")
            if attempt == max_retries - 1:
                print(f"Failed to download {url} after {max_retries} attempts.")
            time.sleep(2)
    time.sleep(1) # Be nice to the server

for crop in crops:
    crop_dir = os.path.join(data_dir, crop)
    os.makedirs(crop_dir, exist_ok=True)
    for year in years:
        url = f"{base_url}/{crop}/{year}.csv"
        filepath = os.path.join(crop_dir, f"{year}.csv")
        download_file(url, filepath)

print("Download complete.")
