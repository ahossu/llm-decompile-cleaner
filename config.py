"""
config.py – central place to paste your Hugging Face endpoint + token.

If you publish this repo, either:
  • rename to config_local.py and add to .gitignore, or
  • store secrets in environment variables (still works).

Edit the two placeholders below, save, run.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict
import os

@dataclass(slots=True)
class HFSettings:
    # ──── EDIT THESE TWO LINES ────
    endpoint_url: str = "https://YOUR-ENDPOINT.huggingface.cloud"
    hf_token: str     = "hf_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    # ──────────────────────────────

    temperature: float = 0.01
    max_new_tokens: int = 512
    do_sample: bool = False

    @classmethod
    def load(cls) -> "HFSettings":
        cfg = cls()
        cfg.endpoint_url = os.getenv("LLM4DEC_ENDPOINT", cfg.endpoint_url)
        cfg.hf_token     = os.getenv("LLM4DEC_TOKEN",     cfg.hf_token)
        return cfg

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.hf_token}",
            "Content-Type":  "application/json",
        }

HF = HFSettings.load()

if HF.endpoint_url.startswith("https://YOUR-ENDPOINT") or HF.hf_token.startswith("hf_XXXXXXXXXXXXXXXX"):
    raise RuntimeError("config.py still contains placeholders – please fill in your endpoint_url and hf_token.")
