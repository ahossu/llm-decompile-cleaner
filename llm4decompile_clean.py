#!/usr/bin/env python3
"""
llm4decompile_clean.py

Clean C functions emitted by *any* decompiler (IDA, Ghidra, Binary Ninja…)
using the llm4decompile-22b-v2 model behind your private HF Inference Endpoint.

Usage:
    python llm4decompile_clean.py -i raw_funcs.c -o clean_funcs.c
"""
from __future__ import annotations
import argparse
import logging
import re
import sys
from pathlib import Path
import requests

from config import HF

LOG = logging.getLogger(__name__)
_SPLIT_RE = re.compile(r'(?=/\* ---- Function:)')
_SIG_RE   = re.compile(r'^\s*(?:[A-Za-z_]\w*\s+)+[A-Za-z_]\w*\s*\(.*\)')

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="LLM-powered cleaner for decompiler C output")
    p.add_argument("-i", "--input",  required=True, type=Path, help="Raw C file")
    p.add_argument("-o", "--output", required=True, type=Path, help="Cleaned C file")
    p.add_argument("--keep-intermediate", type=Path, metavar="FILE",
                   help="Dump model output before post-processing (debug)")
    p.add_argument("-v", "--verbose", action="count", default=0,
                   help="-v info, -vv debug")
    return p.parse_args()

def _split_functions(src: str) -> list[str]:
    return [c for c in _SPLIT_RE.split(src) if c.strip()]

def _call_model(chunk: str) -> str:
    payload = {
        "inputs": chunk,
        "parameters": dict(
            temperature=HF.temperature,
            max_new_tokens=HF.max_new_tokens,
            do_sample=HF.do_sample,
        ),
    }
    r = requests.post(HF.endpoint_url, headers=HF.headers, json=payload, timeout=300)
    r.raise_for_status()
    data = r.json()

    if isinstance(data, dict) and "generated_text" in data:
        return str(data["generated_text"])
    if isinstance(data, list) and data and "generated_text" in data[0]:
        return "".join(p["generated_text"] for p in data)
    raise RuntimeError(f"Unexpected HF response: {data!r}")

def _postprocess(text: str) -> str:
    lines = text.splitlines(keepends=True)
    header, body = lines[0], lines[1:]

    sigs = [i for i, l in enumerate(body) if _SIG_RE.match(l)]
    if len(sigs) >= 2:
        body = body[sigs[1]:]

    out = header + "".join(body)
    out = re.sub(r'\n{3,}', '\n\n', out)          # collapse blank lines
    out = re.sub(r'\{\n(\s*\n)+', '{\n', out)   # trim after '{'
    out = re.sub(r'(\n\s*)+\}', '\n}', out)      # trim before '}'
    return out.strip("\n")

def main() -> None:
    args = _parse_args()
    logging.basicConfig(level=logging.WARNING - 10*min(args.verbose, 2),
                        format="%(message)s")

    if not args.input.is_file():
        LOG.error("Input file %s not found", args.input)
        sys.exit(1)

    src   = args.input.read_text(encoding="utf-8", errors="replace")
    funcs = _split_functions(src)
    LOG.info("Found %d functions", len(funcs))

    cleaned: list[str] = []
    for idx, chunk in enumerate(funcs, 1):
        LOG.info("[%d/%d] Cleaning %s", idx, len(funcs), chunk.splitlines()[0].strip())
        try:
            model_out = _call_model(chunk)
            cleaned.append(_postprocess(model_out))
        except Exception as exc:
            LOG.warning("Skipped due to: %s", exc, exc_info=args.verbose > 1)

    if args.keep_intermediate:
        args.keep_intermediate.write_text("\n\n".join(cleaned), encoding="utf-8")
        LOG.info("Intermediate saved → %s", args.keep_intermediate)

    args.output.write_text("\n\n".join(cleaned), encoding="utf-8")
    LOG.warning("Done – %d cleaned functions written to %s", len(cleaned), args.output)

if __name__ == "__main__":
    main()
