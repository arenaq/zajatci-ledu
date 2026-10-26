# Zajatci ledu – pokyny pro další práci

Samospouštěcí webová prezentace v češtině o poslední plavbě Willema Barentse (1596–1597):
rytiny z roku 1598, mluvené vyprávění synchronizované po větách s pohyby kamery, sníh a vítr.
Historie rozhodnutí, mapování panelů na rytiny a zdroje faktů jsou v [docs/projekt.md](docs/projekt.md).

- Web: https://arenaq.github.io/zajatci-ledu/ (GitHub Pages z větve `main`, kořen repozitáře)
- Repozitář: https://github.com/arenaq/zajatci-ledu
- Artefakt na claude.ai (první verze, soukromý): https://claude.ai/artifact/UFPptSYnCRATTSMSqkdJdp

## Uživatel a pravidla

- Komunikace česky, texty prezentace česky.
- **Nic nepushovat, nezakládat ani nemazat na GitHubu bez výslovného souhlasu** pro tu konkrétní akci,
  daného až po tom, co uživatel viděl přesně, co se nahraje. Lokální commity jsou v pořádku.
- API klíče neukládat do proměnných prostředí Windows. Lokálně jen v `.env` (gitignore),
  na GitHubu v repository secretu `ELEVENLABS_API_KEY`. Klíč nikdy nevypisovat do výstupu.
- Při testování v prohlížeči **vždy ztlumit hlas i vítr** (uživatele už jednou překvapil zvuk ze
  skrytého panelu): před kliknutím na start spustit
  `document.getElementById('voice').muted = true` a vypnout vítr tlačítkem `#wind`;
  po testu smazat `localStorage` klíče `zajatci-wind` a `zajatci-cc` a zavřít panel prohlížeče.

## Struktura

| Cesta | Obsah |
| --- | --- |
| `index.html` | celá stránka (CSS + JS inline). Data mezi `/*DATA-START*/` a `/*DATA-END*/` generuje `build_audio.py`, ručně je neupravovat |
| `img/*.webp` | rytiny: `rpNNN` = Rijksmuseum RP-P-OB-80.NNN, `ngNN` = NG-1979-564-NN |
| `audio/<id>.mp3` | jedna nahrávka na snímek |
| `_build/slides.json` | **zdroj pravdy**: věty, data, titulky, kapitoly, rytiny, pohyby kamery, sníh/vítr, fonetické přepisy pro TTS |
| `_build/voice.json` | veřejné nastavení hlasů (ElevenLabs voice_id, model, voice_settings; Piper) |
| `_build/build_audio.py` | TTS po větách s mezipamětí `_build/cache`, sestaví MP3 a vloží data do `index.html` |
| `_build/download_scans.py` | stáhne skeny z Wikimedia Commons do `_build/scans` |
| `_build/prepare_images.py` | vyřízne tiskovou desku, sjednotí tón (duotón), uloží WebP; `MANUAL` = ruční výřezy |
| `.github/workflows/narration.yml` | ruční namluvení v GitHub Actions se secretem |

Gitignore: `.env`, `_build/cache/` (namluvené věty, šetří kredity), `_build/voices/` (Piper model 61 MB),
`_build/scans/`, `ukazky/`.

Mimo repozitář (složka o úroveň výš, jen lokálně): 19 původních fotek panelů `PXL_20261025_*.jpg`,
`denik_prepis_a_preklad.md` (norský přepis + věrný český překlad; norský text muzea je možná
chráněný, proto není ve veřejném repozitáři), `ukazky_hlasu/` (porovnání hlasů), `.claude/launch.json`.

## Datový model snímku (`slides.json`)

- `kind`: `title` | `intro` | `diary` | `context` | `epilogue` | `credits`
- `chapter` (`"II · Zima v ledu"`): při změně se zobrazí kapitolový předěl a zvuk startuje o 3 s později
- `date`, `title`: popisek vlevo dole; `snow`, `wind`: 0–1 intenzita sněhu a větru
- `text`: pole vět; každá věta se namlouvá zvlášť a její čas určuje titulky i kamerové pohyby
- `images`: `[{src, at, moves, spin?}]` – `at` = index věty, kdy se rytina prolne;
  `moves` = `[index_věty, cx, cy, zoom]`, kde cx/cy jsou 0–1 v souřadnicích obrázku a zoom 1 = vyplnit okno.
  Více pohybů se stejným indexem se rozprostře v rámci věty. `spin` = rotující mapa na titulní straně.
- `hold`: délka snímku bez zvuku (závěrečné titulky)
- `tts_replace` (nahoře v souboru): fonetické přepisy jmen a letopočtů pouze pro hlas
  (např. „Gerrit de Veer“ → „Gerit de Vér“, „1596“ → „patnáct set devadesát šest“); titulky ukazují původní text

## Příkazy (z kořene repozitáře, Python jen přes uv)

```bash
# celé vyprávění (namluví jen věty, které nejsou v mezipaměti)
uv run --python 3.12 --with lameenc --with numpy python _build/build_audio.py elevenlabs
# ukázka jednoho snímku do ukazky/ bez zásahu do prezentace
uv run --python 3.12 --with lameenc --with numpy python _build/build_audio.py elevenlabs --only d12
# rytiny
uv run python _build/download_scans.py
uv run --with opencv-python-headless --with numpy python _build/prepare_images.py _build/scans img
# lokální server (bez HTTP Range: přeskakování uvnitř snímku lokálně nefunguje, na Pages ano)
uv run python -m http.server 8765
```

Pozor: `build_audio.py piper` přepíše `audio/` i data v `index.html` hlasem Jirka. Pro srovnání
hlasů používat jen `--only`.

## Zjištění z vývoje

- Python není na PATH, používá se `uv` (Piper vyžaduje `--python 3.12` kvůli onnxruntime).
  Konzole Windows je cp1252, skripty si přepínají stdout/stderr na UTF-8.
- ElevenLabs: bezplatný tarif nepustí hlasy z knihovny přes API (HTTP 402), proto tarif Starter.
  Model `eleven_v4` přijímá `previous_text`/`next_text`; skript při chybě 400/422 přejde na
  prosté volání. Celé vyprávění (8 746 znaků) stálo asi 3 300 kreditů. `preflight()` před syntézou
  ověří zbývající kredity (klíč potřebuje právo User: Read).
- edge-tts: `cs-CZ-AntoninNeural` služba v říjnu 2026 nevracela (NoAudioReceived), Vlasta ano.
- Rytiny z Commons mají 2500–6300 px; automatický výřez podle profilu inkoustu selhává u světlých
  nebes, proto `MANUAL` v `prepare_images.py`.
- Na GitHub Pages Jekyll nepublikuje složky začínající podtržítkem ani tečkou, `_build/` a `.github/`
  tedy na webu nejsou; `_config.yml` vylučuje i dokumentaci.
- GitHub CLI není nainstalované; push jde přes Git Credential Manager (přihlašuje se uživatel sám).
- Stránka musí zůstat soběstačná (jen Google Fonts zvenku), aby fungovala z disku i jako artefakt.
