"""Stáhne skeny rytin z Wikimedia Commons (Rijksmuseum, CC0) do _build/scans.

Z nich prepare_images.py vyřízne tiskovou desku a uloží img/*.webp:
  uv run python _build/download_scans.py
  uv run --with opencv-python-headless --with numpy python _build/prepare_images.py _build/scans img
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "_build", "scans")
WIDTH = 2560  # šířka náhledu z Commons; originály mají až 6300 px
UA = {"User-Agent": "zajatci-ledu/1.0 (https://github.com/arenaq/zajatci-ledu)"}

TITLES = [
    "File:Kaart van het noordelijk halfrond, NG-1979-564-15.jpg",
    "File:Binnen in het Behouden Huys, 1596-1597, NG-1979-564-22.jpg",
    "File:De twee schepen en een hemelverschijnsel, 1596, RP-P-OB-80.205.jpg",
    "File:Gevecht met de ijsbeer, 1596, RP-P-OB-80.206.jpg",
    "File:Het schip dreigt bij Oranje-eiland in het ijs vast te raken, 1596, RP-P-OB-80.207.jpg",
    "File:Kaart van Spitsbergen, 1596 delineatio Spitsbergiae (titel op object), RP-P-OB-80.208.jpg",
    "File:Het schip raakt vast in het ijs, 1596, RP-P-OB-80.209.jpg",
    "File:Het schip vastgelopen in het ijs, 1596, RP-P-OB-80.210.jpg",
    "File:Drie ijsberen bij het vastgelopen schip, 1596, RP-P-OB-80.211.jpg",
    "File:Slepen van hout op sleden naar de plaats waar het huis gebouwd wordt, 1596, RP-P-OB-80.212.jpg",
    "File:Timmeren van het Behouden Huys, 1596, RP-P-OB-80.213.jpg",
    "File:Overvallen door ijsberen bij het laden van de sleden, 1596, RP-P-OB-80.214.jpg",
    "File:Aanleggen van vossenvallen bij het Behouden Huys, 1596, RP-P-OB-80.215.jpg",
    "File:Schieten en villen van een ijsbeer, 1597, RP-P-OB-80.216.jpg",
    "File:Timmerwerk aan de sloep, 1597, RP-P-OB-80.218.jpg",
    "File:Het vrijmaken van een pad door het ijs naar de zee, 1597, RP-P-OB-80.219.jpg",
    "File:De sloepen worden te water gelaten, 1597, RP-P-OB-80.220.jpg",
    "File:De sloepen worden uit het water gehaald, 1597, RP-P-OB-80.221.jpg",
    "File:Aanval door drie ijsberen op de sloepen, 1597, RP-P-OB-80.222.jpg",
    "File:De verpletterde sloep wordt uitgeladen, 1597, RP-P-OB-80.223.jpg",
    "File:Het vertrek van het eiland, 1597, RP-P-OB-80.224.jpg",
    "File:De ontmoeting met de bemanning van twee Russische lodja's, 1597, RP-P-OB-80.225.jpg",
    "File:De ontmoeting met een Russische lodja, 1597, RP-P-OB-80.226.jpg",
    "File:Kaart van de Russische kust met het plaatsje Kola, 1597, RP-P-OB-80.227.jpg",
    "File:Kaartje van de rivermond met het plaatsje Kola, 1597, RP-P-OB-80.228.jpg",
    "File:Kaartje van Nova Zembla, 1597 Caerte van Nova Zembla de Weygats de custe van Tartarien en Ruslandt tot Kilduyn toe (titel op object), RP-P-OB-80.229.jpg",
]


def get(url):
    for attempt in range(5):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
        except (urllib.error.URLError, TimeoutError):
            pass
        time.sleep(10 * (attempt + 1))
    raise SystemExit(f"Nepodařilo se stáhnout {url}")


def main():
    os.makedirs(OUT, exist_ok=True)
    for k in range(0, len(TITLES), 25):
        query = urllib.parse.urlencode(dict(action="query", titles="|".join(TITLES[k:k + 25]), prop="imageinfo",
                                            iiprop="url", iiurlwidth=WIDTH, format="json"))
        pages = json.loads(get("https://commons.wikimedia.org/w/api.php?" + query))["query"]["pages"]
        for page in pages.values():
            name = re.search(r"(RP-P-OB-80\.\d+|NG-1979-564-\d+)", page["title"]).group(1) + ".jpg"
            path = os.path.join(OUT, name)
            if os.path.exists(path) and os.path.getsize(path) > 0:
                continue
            data = get(page["imageinfo"][0]["thumburl"])
            with open(path, "wb") as f:
                f.write(data)
            print(name, len(data) // 1024, "kB")
            time.sleep(1.5)
    print("Hotovo:", OUT)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
