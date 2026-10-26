# Zajatci ledu

Webová prezentace s mluveným českým vyprávěním o poslední plavbě Willema Barentse (1596–1597).
Vychází z deníku Gerrita de Veera, jak je vystavený na panelech v norském Tromsø, a z rytin
z první knihy o výpravě (1598). Po spuštění běží sama: rytiny se pomalu přibližují podle vyprávění,
v zimních scénách sněží a pod hlasem fouká vítr. Délka asi 12 minut.

**Web:** https://arenaq.github.io/zajatci-ledu/

## Spuštění

Otevřete `index.html` v prohlížeči (stačí dvojklik) a klikněte na **Spustit vyprávění**.
Bez internetu se jen místo historického písma použije náhradní.

Ovládání: mezerník pauza, šipky předchozí/další snímek, `C` titulky, `M` vítr, `F` celá obrazovka,
kliknutí na časovou osu skočí na konkrétní den deníku.

## Struktura

| Cesta | Obsah |
| --- | --- |
| `index.html` | celá stránka včetně dat (texty, časování vět, pohyby kamery) |
| `img/` | rytiny ve WebP |
| `audio/` | namluvené snímky v MP3 |
| `_build/slides.json` | scénář: věty, data, titulky, rytiny a pohyby kamery |
| `_build/voice.json` | hlas, kterým je vyprávění namluvené (ElevenLabs Radan-Deep, model Eleven v4) |
| `_build/build_audio.py` | namluví vyprávění a vloží data do `index.html` |
| `_build/download_scans.py`, `_build/prepare_images.py` | stáhnou a upraví rytiny |
| `.github/workflows/narration.yml` | namluvení v GitHub Actions |
| `docs/projekt.md` | historie projektu, mapování panelů na rytiny, zdroje faktů |
| `CLAUDE.md` | pokyny pro navázání v Claude Code |

## Klíč k ElevenLabs

Klíč do repozitáře nepatří a `.gitignore` ho vyřazuje. Vytvoříte ho na elevenlabs.io: avatar →
**API Keys** → **Create API Key**, s právy Text to Speech, Voices: Read a User: Read
a s limitem kreditů. Hlasy z knihovny ElevenLabs přes API vyžadují placený tarif.

- **Lokálně:** zkopírujte `.env.example` jako `.env` a doplňte `ELEVENLABS_API_KEY`.
- **Na GitHubu:** **Settings → Secrets and variables → Actions → New repository secret**,
  název `ELEVENLABS_API_KEY`. Secret je šifrovaný, nikdo ho po uložení nepřečte a používají ho
  jen workflow v tomto repozitáři.

## Úprava textu a nové namluvení

Upravte `_build/slides.json`. Hotové věty se ukládají do mezipaměti, takže se platí jen za změněné.

**Lokálně** (potřebuje [uv](https://docs.astral.sh/uv/)), z kořene repozitáře:

```bash
uv run --python 3.12 --with lameenc --with numpy python _build/build_audio.py elevenlabs
```

Ukázku jednoho snímku do složky `ukazky/` bez zásahu do prezentace vytvoří `--only <id>`,
třeba `--only d12`. Před syntézou skript zkontroluje zbývající kredity.

**Na GitHubu:** **Actions → Namluvit vyprávění → Run workflow**. Prázdné pole namluví celé vyprávění
a nové nahrávky commitne; s vyplněným id snímku vytvoří jen ukázku ke stažení. Mezipaměť vět se
mezi běhy přenáší.

Offline náhradní hlas Piper Jirka: model stáhněte příkazem
`uv run --python 3.12 --with piper-tts python -m piper.download_voices --download-dir _build/voices cs_CZ-jirka-medium`
a spusťte `build_audio.py piper` (přidejte `--with piper-tts`). Pozor, přepíše aktuální nahrávky.

## Rytiny

```bash
uv run python _build/download_scans.py
uv run --with opencv-python-headless --with numpy python _build/prepare_images.py _build/scans img
```

## Nasazení

GitHub Pages: **Settings → Pages → Deploy from a branch**, větev `main`, složka `/ (root)`.
Každý push do `main` web aktualizuje. Jekyll nepublikuje `_build/`, `.github/` ani dokumentaci
(viz `_config.yml`).

## Zdroje a práva

- Rytiny: Rijksmuseum Amsterdam (RP-P-OB-80.205–229, NG-1979-564-15 a -22), volné dílo CC0,
  přes Wikimedia Commons.
- Text: Gerrit de Veer, *Waerachtighe beschryvinghe van drie seylagien*, Amsterdam 1598, převzato
  z norských panelů v Tromsø a přeloženo do češtiny. Původní deník je volné dílo, norské
  převyprávění na panelech může být chráněné, proto před širším zveřejněním doporučuji
  souhlas muzea.
- Hlas: Radan-Deep, ElevenLabs (model Eleven v4), tarif s komerční licencí.
