# llm-decompile-cleaner
![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue?logo=python)


_Decompiler‑agnostic post‑processing powered by **llm4decompile‑22b‑v2**_

```bash
# After editing config.py with your endpoint & token:
python llm4decompile_clean.py -i raw_funcs.c -o clean_funcs.c
```

Works with any tool that can dump its C output to a file (IDA, Ghidra, Binary Ninja, radare2, Snowman, Godbolt CE, …).
The only requirement is that every function block begins with a comment such as:

```c
/* ---- Function: foo ---- */
```

(Adjust `_SPLIT_RE` in the script if your marker differs.)

## Options

| Flag                     | What it does                                                |
|--------------------------|-------------------------------------------------------------|
| `--input / -i`           | Raw C file to clean                                         |
| `--output / -o`          | Destination file for cleaned code                           |
| `--keep-intermediate`    | Save model output *before* whitespace & signature trimming  |
| `--verbose / -v / -vv`   | `-v` shows progress, `-vv` adds tracebacks on errors        |

## Requirements

```text
python >= 3.9
requests >= 2.32
```

Install via:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Contributing

PRs are welcome. Run `ruff`, `black`, and `pyright` before committing (see `requirements-dev.txt`).

## License

Apache-2.0 © 2025–present Alexandru Hossu – see the [LICENSE](LICENSE) file for details.
