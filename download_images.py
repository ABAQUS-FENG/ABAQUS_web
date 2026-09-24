import os
import sys
import json
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parent
PRODUCTS = json.loads((ROOT / "products.json").read_text(encoding="utf-8"))
IMAGES = ROOT / "images"
IMAGES.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com/",
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
}

def download(url, dest):
    req = Request(url, headers=HEADERS)
    with urlopen(req, timeout=30) as r:
        data = r.read()
    dest.write_bytes(data)

print("=" * 66)
print("Abaqus Tools - Product Image Downloader")
print("=" * 66)
print(f"Website folder: {ROOT}")
print(f"Images folder : {IMAGES}")
print()

ok = 0
failed = []

for i, p in enumerate(PRODUCTS, 1):
    url = p["image"]
    rel = p["local_image"]
    dest = ROOT / rel
    dest.parent.mkdir(parents=True, exist_ok=True)

    if dest.exists() and dest.stat().st_size > 1000:
        print(f"[{i:02d}/{len(PRODUCTS)}] EXISTS  {dest.name}")
        ok += 1
        continue

    try:
        print(f"[{i:02d}/{len(PRODUCTS)}] GET     {p['no']} - {p['name']}")
        download(url, dest)
        if dest.stat().st_size < 1000:
            raise RuntimeError("Downloaded file is unexpectedly small.")
        print(f"           SAVED   {dest.name} ({dest.stat().st_size/1024:.1f} KB)")
        ok += 1
        time.sleep(0.25)
    except Exception as e:
        print(f"           FAILED  {e}")
        failed.append((p["no"], p["name"], url, str(e)))

print()
print("=" * 66)
print(f"Finished: {ok}/{len(PRODUCTS)} images downloaded.")
if failed:
    print(f"{len(failed)} image(s) failed. A text file has been created:")
    report = ROOT / "image_download_failures.txt"
    with report.open("w", encoding="utf-8") as f:
        for no, name, url, err in failed:
            f.write(f"{no} | {name}\n{url}\nERROR: {err}\n\n")
    print(report)
    print()
    print("If Bilibili temporarily blocks a file, run this script again later.")
else:
    print("All product images are ready.")
    fail_report = ROOT / "image_download_failures.txt"
    if fail_report.exists():
        fail_report.unlink()

print()
print("Next step:")
print("Upload the ENTIRE website folder to GitHub, including the images folder.")
input("\nPress Enter to close...")
