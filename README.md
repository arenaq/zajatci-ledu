# Zajatci ledu

Webová prezentace s mluveným českým vyprávěním o poslední plavbě Willema Barentse (1596–1597).
Vychází z deníku Gerrita de Veera, jak je vystavený na panelech v norském Tromsø, a z rytin
z první knihy o výpravě (1598). Po spuštění běží sama: rytiny se pomalu přibližují podle vyprávění,
v zimních scénách sněží a pod hlasem fouká vítr. Délka asi 12 minut.

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
| `_build/build_audio.py` | namluví vyprávění a vloží data do `index.html` |
| `_build/prepare_images.py` | vyřízne a sjednotí rytiny ze skenů Rijksmusea |

## Úprava textu a nové namluvení

Upravte `_build/slides.json` a spusťte ze složky s `index.html`
(potřebuje [uv](https://docs.astral.sh/uv/)):

```bash
uv run --python 3.12 --with piper-tts --with lameenc --with numpy python _build/build_audio.py elevenlabs
```

Hotové věty se ukládají do `_build/cache`, takže se přegenerují jen změněné.
Ukázku jednoho snímku bez zásahu do prezentace vytvoří `--only <id>`, třeba `--only d12`.

Hlasy:

- `elevenlabs`: zkopírujte `_build/elevenlabs.example.json` jako `_build/elevenlabs.json` a doplňte
  API klíč. Hlasy z knihovny ElevenLabs vyžadují placený tarif. Před syntézou skript zkontroluje
  zbývající kredity.
- `piper`: offline český hlas Jirka. Model stáhněte příkazem
  `uv run --python 3.12 --with piper-tts python -m piper.download_voices --download-dir _build/voices cs_CZ-jirka-medium`.

## Nasazení na GitHub Pages

1. Vytvořte na GitHubu veřejný repozitář a nahrajte do něj tuto složku.
2. V repozitáři otevřete **Settings → Pages**, zvolte **Deploy from a branch**, větev `main`
   a složku `/ (root)`.
3. Za minutu bude stránka na adrese `https://<uživatel>.github.io/<repozitář>/`.

GitHub Pages zpracovává web Jekyllem, který složky začínající podtržítkem nepublikuje,
takže `_build/` zůstane jen v repozitáři.

## Zdroje a práva

- Rytiny: Rijksmuseum Amsterdam (RP-P-OB-80.205–229, NG-1979-564-15 a -22), volné dílo CC0,
  přes Wikimedia Commons.
- Text: Gerrit de Veer, *Waerachtighe beschryvinghe van drie seylagien*, Amsterdam 1598, převzato
  z norských panelů v Tromsø a přeloženo do češtiny. Původní deník je volné dílo, norské
  převyprávění na panelech může být chráněné, proto před veřejným zveřejněním doporučuji
  souhlas muzea.
- Hlas: Radan-Deep, ElevenLabs (model Eleven v4), tarif s komerční licencí.
