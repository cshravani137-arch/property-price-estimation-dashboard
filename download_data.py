"""Download public housing CSVs into data/raw/external.

The bundled dashboard does not require this script. Run it only when internet is available.
"""
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data" / "raw" / "external"
SOURCES = {
    "Mumbai.csv": "https://raw.githubusercontent.com/happygoluckycodeeditor/pricepredictionmodel/main/Mumbai.csv",
    "Delhi.csv": "https://raw.githubusercontent.com/happygoluckycodeeditor/pricepredictionmodel/main/Delhi.csv",
    "Bengaluru_House_RawData.csv": "https://raw.githubusercontent.com/Anamikaa-MK/Bengaluru-House-Price-Analysis/main/Data/Bengaluru_House_RawData.csv",
}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    success = 0
    for filename, url in SOURCES.items():
        destination = OUT / filename
        print(f"Downloading {filename} ...")
        try:
            request = Request(url, headers={"User-Agent": "PropertyPriceEstimationDashboard/1.0"})
            with urlopen(request, timeout=25) as response:
                content = response.read()
            if not content or len(content) < 100:
                raise ValueError("Downloaded file appears empty or incomplete")
            destination.write_bytes(content)
            print(f"  Saved {destination} ({len(content):,} bytes)")
            success += 1
        except Exception as exc:
            print(f"  Could not download {filename}: {exc}")
            print(f"  Source URL: {url}")
    print(f"\nCompleted: {success}/{len(SOURCES)} files downloaded.")
    if not success:
        print("The Streamlit dashboard still works with its bundled educational sample dataset.")

if __name__ == "__main__":
    main()
