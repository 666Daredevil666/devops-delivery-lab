"""Check a running stack; creates one note and reads it back."""

import argparse
import json
from urllib.request import Request, urlopen


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    base_url = parser.parse_args().base_url.rstrip("/")

    def request(path: str, payload: dict | None = None):
        body = json.dumps(payload).encode() if payload is not None else None
        req = Request(base_url + path, data=body, headers={"Content-Type": "application/json"})
        with urlopen(req, timeout=10) as response:
            return response.status, json.load(response)

    for path in ["/health/live", "/health/ready"]:
        status, body = request(path)
        if status != 200 or body != {"status": "ok"}:
            raise RuntimeError(f"Health check failed: {path}")
    status, note = request("/notes", {"title": "Smoke check", "content": "Create and read"})
    if status != 201:
        raise RuntimeError("Note creation failed")
    status, stored = request(f"/notes/{note['id']}")
    if status != 200 or stored != note:
        raise RuntimeError("Stored note differs from created note")
    print(f"Smoke check passed; note id={note['id']}")


if __name__ == "__main__":
    main()
