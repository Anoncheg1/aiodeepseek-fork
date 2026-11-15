from __future__ import annotations

import ctypes
import ctypes.util
from pathlib import Path


def _load_library() -> ctypes.CDLL:
    """Load the compiled _pow shared library next to this file."""
    candidates: list[str] = []
    here = Path(__file__).resolve().parent
    for name in (
        "_pow_c.so",
        "_pow_c",
        "_pow.so",
        "_pow_c.dylib",
        "_pow_c.dll",
        "_pow.cpython-314-x86_64-linux-gnu.so",
    ):
        p = here / name
        if p.exists():
            candidates.append(str(p))

    found = ctypes.util.find_library("pow_c")
    if found:
        candidates.append(found)

    if not candidates:
        raise ImportError(
            "Could not locate the compiled _pow library. "
            "Did you build it with g++ -O3 -Wall -shared -std=c++17 -fPIC _pow.cpp -o _pow_c.so ?"
        )

    last_err: Exception | None = None
    for path in candidates:
        try:
            lib = ctypes.CDLL(path)
            lib.solve.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int64]
            lib.solve.restype = ctypes.c_int64
            return lib
        except (AttributeError, OSError) as e:
            last_err = e

    raise ImportError(f"Failed to load _pow library: {last_err}")


_lib = _load_library()


def solve(base: str | bytes, challenge_hex: str | bytes, difficulty: int) -> int:
    base_b = base.encode("utf-8") if isinstance(base, str) else base
    challenge_b = challenge_hex.encode("ascii") if isinstance(challenge_hex, str) else challenge_hex
    return int(_lib.solve(base_b, challenge_b, int(difficulty)))


__all__ = ["solve"]
