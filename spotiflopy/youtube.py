import subprocess
import json


def search_youtube(query, limit=5):
    try:
        result = subprocess.run(
            ["yt-dlp", f"ytsearch{limit}:{query}", "--dump-json"],
            capture_output=True,
            text=True
        )

        lines = result.stdout.strip().split("\n")
        results = []

        for line in lines:
            if not line.strip():
                continue

            data = json.loads(line)

            results.append({
                "title": data.get("title"),
                "url": data.get("webpage_url"),
            })

        return results

    except Exception as e:
        print("[YT ERROR]", e)
        return []
