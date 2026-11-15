from __future__ import annotations

import time
from typing import Optional

from aiodeepseek.http import _config
from aiodeepseek.log import _log_str
# from aiodeepseek.pow._pow import solve as _cpp
from aiodeepseek.pow._pow_ctypes import PowSolverError, solve_pow as _ctypes_solve

def solve_pow(base: str, challenge_hex: str, difficulty: int) -> int:
    """Brute-force a proof-of-work nonce for the DeepSeek API.

    Uses the compiled C library (loaded via :mod:`ctypes`) for performance.

    Args:
        base: Salt string prefix shared by the server.
        challenge_hex: Expected hash digest as a 64-char hex string.
        difficulty: Maximum number of nonce values to try.

    Returns:
        The first valid nonce (>= 0).

    Raises:
        ValueError: On malformed ``challenge_hex`` or non-positive ``difficulty``.
        PowSolverError: If the solver fails (e.g. CPU without AVX2).
    """
    total_start: Optional[float] = None
    if _config._LOG_POW_TIME or _config._DEV_MODE:
        total_start = time.perf_counter()

    nonce: int = _ctypes_solve(base, challenge_hex, difficulty)

    if total_start is not None:
        _log_str(
            f"[pow done {(time.perf_counter() - total_start) * 1000:.2f} ms]: "
            f"{base, challenge_hex, difficulty}"
        )
    return nonce


__all__ = ["solve_pow"]
