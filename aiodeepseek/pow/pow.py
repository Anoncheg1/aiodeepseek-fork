from __future__ import annotations

from pathlib import Path
import time
from typing import Optional

try:
    from ._pow_ctypes import solve as _cpp
except ImportError:
    # Fallback when the library is not local yet; keep the symbol available.
    def _cpp(base: str, challenge_hex: str, difficulty: int) -> int:
        raise ImportError("The ctypes-backed PoW library is not available")


def solve_pow(base: str, challenge_hex: str, difficulty: int) -> int:
    """Brute-force a proof-of-work nonce for the DeepSeek API."""
    total_start: Optional[float] = None
    if Path(__file__).parent.name == "pow":
        total_start = time.perf_counter()

    nonce: int = _cpp(base, challenge_hex, difficulty)

    if total_start is not None:
        elapsed_ms = (time.perf_counter() - total_start) * 1000.0
        print(f"[pow done {elapsed_ms:.2f} ms]: {(base, challenge_hex, difficulty)}")
    return nonce


__all__ = ["solve_pow"]
