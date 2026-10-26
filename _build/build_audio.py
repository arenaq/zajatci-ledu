"""Namluví vyprávění ze slides.json, uloží audio/<id>.mp3 a data.js s časováním vět.

Každá věta se syntetizuje zvlášť a ukládá do _build/cache, takže po úpravě textu
se přegenerují jen změněné věty. Hlas se volí prvním argumentem:

  piper       offline, rodilý český hlas Jirka (výchozí, zdarma)
  elevenlabs  čte api_key, voice_id a model (výchozí eleven_v4) ze soukromého souboru
              _build/elevenlabs.json. Před syntézou zkontroluje zbývající kredity.
  azure       potřebuje AZURE_SPEECH_KEY a AZURE_SPEECH_REGION (hlas cs-CZ-AntoninNeural,
              jiný přes AZURE_VOICE)
  edge        zdarma online přes edge-tts (hlas EDGE_VOICE, výchozí cs-CZ-AntoninNeural)

Spuštění (ze složky prezentace):
  uv run --python 3.12 --with piper-tts --with lameenc --with numpy --with edge-tts --with miniaudio python _build/build_audio.py piper
Ukázka jednoho snímku do složky ukazky_hlasu, bez zásahu do prezentace:
  ... python _build/build_audio.py elevenlabs --only d12
"""
import asyncio
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from xml.sax.saxutils import escape

import lameenc
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "_build")
CACHE = os.path.join(BUILD, "cache")

LEAD = 0.45        # ticho na začátku snímku
GAP = 0.5          # pauza mezi větami
GAP_COMMA = 0.22   # pauza po větě končící čárkou
TAIL = 0.6         # ticho na konci snímku


# ---------------------------------------------------------------- hlasy

class Piper:
    label = "Jirka (Piper, offline)"

    def __init__(self):
        from piper import PiperVoice, SynthesisConfig
        model = os.environ.get("PIPER_MODEL", os.path.join(BUILD, "voices", "cs_CZ-jirka-medium.onnx"))
        self.key = "piper:" + os.path.basename(model)
        self.voice = PiperVoice.load(model)
        self.cfg = SynthesisConfig(length_scale=1.07)

    def synth(self, text, prev, nxt):
        chunks = list(self.voice.synthesize(text, syn_config=self.cfg))
        return np.concatenate([c.audio_int16_array for c in chunks]), chunks[0].sample_rate


def local_settings(name):
    """Soukromé nastavení ze _build/<name>.json (klíče se neukládají do proměnných prostředí)."""
    path = os.path.join(BUILD, name + ".json")
    return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}


class ElevenLabs:
    API = "https://api.elevenlabs.io/v1"

    def __init__(self):
        cfg = local_settings("elevenlabs")
        self.api_key = cfg.get("api_key") or os.environ.get("ELEVENLABS_API_KEY")
        self.voice_id = cfg.get("voice_id") or os.environ.get("ELEVENLABS_VOICE_ID")
        if not self.api_key or not self.voice_id:
            sys.exit("Chybí api_key nebo voice_id v _build/elevenlabs.json, nic se negeneruje.")
        self.model = cfg.get("model") or os.environ.get("ELEVENLABS_MODEL") or "eleven_v4"
        self.key = f"elevenlabs:{self.voice_id}:{self.model}"
        self.simple = False  # model neumí navazování vět nebo nastavení hlasu
        try:
            self.label = self._get(f"/voices/{self.voice_id}")["name"] + " (ElevenLabs)"
        except Exception:
            self.label = f"ElevenLabs ({self.voice_id})"

    def _get(self, path):
        req = urllib.request.Request(self.API + path, headers={"xi-api-key": self.api_key})
        return json.load(urllib.request.urlopen(req, timeout=30))

    def credits_left(self):
        try:
            sub = self._get("/user/subscription")
            return sub["character_limit"] - sub["character_count"]
        except Exception:
            return None

    def preflight(self, chars):
        """Před placenou syntézou zkontroluje zbývající kredity, ať se nevyčerpá měsíční kvóta."""
        print(f"Hlas: {self.label}, model {self.model}, k syntéze {chars} znaků.")
        left = self.credits_left()
        if left is None:
            print("Zbývající kredity nejdou ověřit (klíč nemá právo User: Read), pokračuji.")
            return
        print(f"Zbývá {left} kreditů.")
        if chars > left:
            sys.exit("Na celé vyprávění nezbývá dost kreditů, nic se negeneruje.")

    def synth(self, text, prev, nxt):
        body = {"text": text, "model_id": self.model}
        if not self.simple:
            body.update(previous_text=prev, next_text=nxt,
                        voice_settings={"stability": 0.5, "similarity_boost": 0.8, "style": 0.1, "use_speaker_boost": True})
        req = urllib.request.Request(
            f"{self.API}/text-to-speech/{self.voice_id}?output_format=pcm_24000",
            data=json.dumps(body).encode(), headers={"xi-api-key": self.api_key, "Content-Type": "application/json"})
        try:
            return np.frombuffer(urllib.request.urlopen(req, timeout=120).read(), np.int16), 24000
        except urllib.error.HTTPError as e:
            if e.code in (400, 422) and not self.simple:
                print(f"Model {self.model} odmítl navazování vět ({e.code}), zkouším bez něj.")
                self.simple = True
                return self.synth(text, prev, nxt)
            raise SystemExit(f"ElevenLabs vrátil chybu {e.code}: {e.read()[:300]!r}")


class Azure:
    def __init__(self):
        self.api_key = os.environ["AZURE_SPEECH_KEY"]
        self.region = os.environ["AZURE_SPEECH_REGION"]
        self.voice = os.environ.get("AZURE_VOICE", "cs-CZ-AntoninNeural")
        self.key = "azure:" + self.voice
        self.label = f"{self.voice} (Azure)"

    def synth(self, text, prev, nxt):
        ssml = (f"<speak version='1.0' xml:lang='cs-CZ'><voice name='{self.voice}'>"
                f"<prosody rate='-6%'>{escape(text)}</prosody></voice></speak>")
        req = urllib.request.Request(
            f"https://{self.region}.tts.speech.microsoft.com/cognitiveservices/v1", data=ssml.encode(),
            headers={"Ocp-Apim-Subscription-Key": self.api_key, "Content-Type": "application/ssml+xml",
                     "X-Microsoft-OutputFormat": "raw-24khz-16bit-mono-pcm", "User-Agent": "barentsz-prezentace"})
        return np.frombuffer(urllib.request.urlopen(req, timeout=120).read(), np.int16), 24000


class Edge:
    def __init__(self):
        self.voice = os.environ.get("EDGE_VOICE", "cs-CZ-AntoninNeural")
        self.key = "edge:" + self.voice
        self.label = f"{self.voice} (Edge)"

    def synth(self, text, prev, nxt):
        import edge_tts
        import miniaudio

        async def run():
            buf = b""
            async for msg in edge_tts.Communicate(text, self.voice, rate="-6%").stream():
                if msg["type"] == "audio":
                    buf += msg["data"]
            return buf

        dec = miniaudio.decode(asyncio.run(run()), output_format=miniaudio.SampleFormat.SIGNED16,
                               nchannels=1, sample_rate=24000)
        return np.frombuffer(dec.samples.tobytes(), np.int16), 24000


BACKENDS = {"piper": Piper, "elevenlabs": ElevenLabs, "azure": Azure, "edge": Edge}


# ---------------------------------------------------------------- sestavení

def tts_text(text, replacements):
    for a, b in replacements:
        text = text.replace(a, b)
    return text


def cache_path(backend, text):
    return os.path.join(CACHE, hashlib.sha1(f"{backend.key}|{text}".encode()).hexdigest()[:16] + ".npz")


def cached_synth(backend, text, prev, nxt):
    path = cache_path(backend, text)
    if os.path.exists(path):
        z = np.load(path)
        return z["pcm"], int(z["sr"])
    pcm, sr = backend.synth(text, prev, nxt)
    pcm = trim(pcm, sr)
    np.savez_compressed(path, pcm=pcm, sr=sr)
    return pcm, sr


def trim(pcm, sr, thr=250):
    """Ořízne ticho na začátku a konci věty, ať jsou pauzy přesně pod kontrolou."""
    loud = np.flatnonzero(np.abs(pcm.astype(np.int32)) > thr)
    if len(loud) == 0:
        return pcm
    pad = int(0.04 * sr)
    return pcm[max(0, loud[0] - pad):loud[-1] + pad]


def encode_mp3(pcm, sr, path):
    enc = lameenc.Encoder()
    enc.set_bit_rate(64)
    enc.set_in_sample_rate(sr)
    enc.set_channels(1)
    enc.set_quality(2)
    with open(path, "wb") as f:
        f.write(enc.encode(pcm.tobytes()) + enc.flush())


def inline_data(data):
    """Vloží data přímo do index.html, aby stránka fungovala i otevřená z disku."""
    path = os.path.join(ROOT, "index.html")
    html = open(path, encoding="utf-8").read()
    payload = "window.PRESENTATION = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";"
    html = re.sub(r"/\*DATA-START\*/.*?/\*DATA-END\*/", lambda m: f"/*DATA-START*/\n{payload}\n/*DATA-END*/",
                  html, count=1, flags=re.S)
    open(path, "w", encoding="utf-8").write(html)


def render_slide(backend, sentences, replacements):
    """Namluví větu po větě a složí je s pauzami. Vrací (pcm, sr, časy vět)."""
    sr, parts, times, t = None, [], [], LEAD
    for i, text in enumerate(sentences):
        spoken = tts_text(text, replacements)
        prev = tts_text(sentences[i - 1], replacements) if i else ""
        nxt = tts_text(sentences[i + 1], replacements) if i + 1 < len(sentences) else ""
        pcm, sr = cached_synth(backend, spoken, prev, nxt)
        dur = len(pcm) / sr
        times.append([round(t, 2), round(t + dur, 2)])
        parts.append(pcm)
        t += dur
        if i + 1 < len(sentences):
            gap = GAP_COMMA if text.rstrip().endswith(",") else GAP
            parts.append(np.zeros(int(gap * sr), np.int16))
            t += gap
    lead = np.zeros(int(LEAD * sr), np.int16)
    tail = np.zeros(int(TAIL * sr), np.int16)
    return np.concatenate([lead, *parts, tail]), sr, times


def main(name, only=None):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    spec = json.load(open(os.path.join(BUILD, "slides.json"), encoding="utf-8"))
    slides = [s for s in spec["slides"] if only is None or s["id"] == only]
    if not slides:
        sys.exit(f"Snímek {only} ve slides.json není.")
    backend = BACKENDS[name]()
    os.makedirs(CACHE, exist_ok=True)
    os.makedirs(os.path.join(ROOT, "audio"), exist_ok=True)
    if hasattr(backend, "preflight"):
        pending = {tts_text(x, spec["tts_replace"]) for s in slides for x in s.get("text", [])}
        backend.preflight(sum(len(x) for x in pending if not os.path.exists(cache_path(backend, x))))

    if only:
        # Ukázka jednoho snímku k poslechu; prezentace zůstane beze změny
        pcm, sr, _ = render_slide(backend, slides[0]["text"], spec["tts_replace"])
        out = os.path.join(os.path.dirname(ROOT), "ukazky_hlasu", f"{name}_{only}.mp3")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        encode_mp3(pcm, sr, out)
        print(f"Ukázka uložena: {out} ({len(pcm) / sr:.1f} s)")
        if hasattr(backend, "credits_left"):
            print(f"Po ukázce zbývá {backend.credits_left()} kreditů.")
        return

    out_slides = []
    for slide in slides:
        s = {k: v for k, v in slide.items() if k != "text"}
        sentences = slide.get("text", [])
        if not sentences:
            s.update(audio=None, duration=slide.get("hold", 10), sentences=[])
            out_slides.append(s)
            continue
        pcm, sr, times = render_slide(backend, sentences, spec["tts_replace"])
        fname = f"audio/{slide['id']}.mp3"
        encode_mp3(pcm, sr, os.path.join(ROOT, fname))
        s.update(audio=fname, duration=round(len(pcm) / sr, 2),
                 sentences=[{"text": x, "t": tm} for x, tm in zip(sentences, times)])
        out_slides.append(s)
        print(f"{slide['id']}: {s['duration']:6.1f} s, {len(sentences)} vět")
    data = {"title": spec["title"], "subtitle": spec["subtitle"], "voice": backend.label, "slides": out_slides}
    inline_data(data)
    total = sum(x["duration"] for x in out_slides)
    print(f"Celkem {total / 60:.1f} min, hlas: {backend.label}")


if __name__ == "__main__":
    args = sys.argv[1:]
    only = args[args.index("--only") + 1] if "--only" in args else None
    main(args[0] if args and not args[0].startswith("--") else "piper", only)
