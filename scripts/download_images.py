#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Job:
    url: str
    rel_out: str


def parse_jobs(list_path: Path) -> list[Job]:
    jobs: list[Job] = []
    for i, raw in enumerate(list_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            raise ValueError(f"Línea {i}: se esperaba '<url> <ruta_salida>'")
        url = parts[0]
        rel_out = " ".join(parts[1:]).strip()
        jobs.append(Job(url=url, rel_out=rel_out))
    return jobs


def fetch(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "probusiness-downloader/1.0 (+python urllib)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} al descargar {url}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Error de red al descargar {url}: {e.reason}") from e


def write_atomic(dest: Path, data: bytes) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, dest)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", required=True, help="Archivo txt con '<url> <ruta_relativa>' por línea.")
    ap.add_argument("--out", required=True, help="Directorio base de salida, ej: public")
    ap.add_argument("--force", action="store_true", help="Re-descargar aunque exista.")
    args = ap.parse_args(argv)

    list_path = Path(args.list).resolve()
    out_dir = Path(args.out).resolve()

    jobs = parse_jobs(list_path)
    if not jobs:
        print("Lista vacía.", file=sys.stderr)
        return 2

    ok = skipped = failed = 0
    for job in jobs:
        dest = out_dir / job.rel_out.replace("\\", "/")
        try:
            if dest.exists() and not args.force:
                skipped += 1
                continue
            data = fetch(job.url)
            write_atomic(dest, data)
            ok += 1
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"[ERROR] {job.url} -> {job.rel_out}: {e}", file=sys.stderr)

    print(f"Listo. descargadas={ok} omitidas={skipped} errores={failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

