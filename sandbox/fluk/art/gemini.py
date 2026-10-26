"""Gemini Image API для рисунков Флюка. Ключ берётся из remotion-skill/.env и нигде не печатается.

python gemini.py models                       — проверить ключ (бесплатный запрос)
python gemini.py gen <имя> <prompt.txt> [model] — сгенерировать out/<имя>.png
"""
import base64
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ENV = Path(r"C:\projects\claude\remotion-skill\.env")
API = "https://generativelanguage.googleapis.com/v1beta"


def key():
    for line in ENV.read_text(encoding="utf-8").splitlines():
        if line.startswith("GEMINI_API_KEY="):
            k = line.split("=", 1)[1].strip().strip('"')
            if k:
                return k
    sys.exit("GEMINI_API_KEY пуст")


def call(url, body=None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None,
                                 headers={"x-goog-api-key": key(), "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:  # текст ошибки без ключа
        sys.exit(f"HTTP {e.code}: {e.read().decode()[:600]}")


def main():
    if sys.argv[1] == "models":
        names = [m["name"] for m in call(f"{API}/models?pageSize=200")["models"]]
        print("ключ жив, моделей:", len(names))
        print("\n".join(n for n in names if "image" in n))
        return
    name, prompt_file = sys.argv[2], sys.argv[3]
    model = sys.argv[4] if len(sys.argv) > 4 else "gemini-2.5-flash-image"
    body = {"contents": [{"parts": [{"text": Path(prompt_file).read_text(encoding="utf-8")}]}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "16:9"}}}
    res = call(f"{API}/models/{model}:generateContent", body)
    for part in res["candidates"][0]["content"]["parts"]:
        if "inlineData" in part:
            out = Path("out") / f"{name}.png"
            out.write_bytes(base64.b64decode(part["inlineData"]["data"]))
            print("сохранено", out, "токены:", res.get("usageMetadata", {}))
            return
    print("картинки нет:", json.dumps(res)[:600])


if __name__ == "__main__":
    main()
