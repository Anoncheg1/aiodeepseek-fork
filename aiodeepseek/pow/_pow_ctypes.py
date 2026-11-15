# g++ -O3 -Wall -shared -std=c++17 -fPIC _pow.cpp -o _pow.so
# OR:
# g++ -O3 -Wall -shared -std=c++17 -fPIC -DENABLE_AVX2 -mavx2 _pow.cpp -o _pow$(python3 -c "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))")
# g++ -O3 -flto -Wall -shared -std=c++17 -fPIC $(python3 -m pybind11 --includes) _pow.cpp -o _pow$(python3-config --extension-suffix)
from __future__ import annotations

import ctypes
import ctypes.util
import sys
from pathlib import Path

_ABI_VERSION = 1


def _load_library() -> ctypes.CDLL:
    # Prefer the compiled extension shipped next to this file; fall back to
    # a bare name on PATH for dev / debugging.
    candidates: list[str] = []
    here = Path(__file__).parent
    for name in ("_pow_c", "_pow_c.so", "_pow.so", "_pow_c.dylib", "_pow_c.dll", "_pow.cpython-314-x86_64-linux-gnu.so"):
        p = here / name
        if p.exists():
            candidates.append(str(p))
    found = ctypes.util.find_library("pow_c")
    if found:
        candidates.append(found)
    if not candidates:
        raise ImportError(
            "Could not locate the compiled _pow library. "
            "Did you build the extension (pip install -e .)?"
        )

    last_err: Exception | None = None
    for path in candidates:
        try:
            return ctypes.CDLL(path)   # CDLL releases the GIL
        except OSError as e:
            last_err = e
    raise ImportError(f"Failed to load _pow library: {last_err}")


_lib = _load_library()

_lib.ds_pow_solve.argtypes = [
    ctypes.c_char_p, ctypes.c_size_t,
    ctypes.c_char_p, ctypes.c_size_t,
    ctypes.c_int64,
]
_lib.ds_pow_solve.restype = ctypes.c_int64

if hasattr(_lib, "ds_pow_abi_version"):
    _lib.ds_pow_abi_version.argtypes = []
    _lib.ds_pow_abi_version.restype = ctypes.c_int32
    if _lib.ds_pow_abi_version() != _ABI_VERSION:
        raise ImportError(
            f"_pow ABI mismatch: {_lib.ds_pow_abi_version()} != {_ABI_VERSION}"
        )


class PowSolverError(RuntimeError):
    pass


def solve_pow(base: str, challenge_hex: str, difficulty: int) -> int:
    """Brute-force a PoW nonce.

    Returns the matching nonce (>= 0), raises PowSolverError on failure.
    """
    if not isinstance(challenge_hex, str) or len(challenge_hex) != 64:
        raise ValueError("challenge_hex must be a 64-character hex string")
    if difficulty <= 0:
        raise ValueError("difficulty must be positive")

    base_b = base.encode("utf-8")
    hex_b = challenge_hex.encode("ascii")

    rc = _lib.ds_pow_solve(
        base_b, len(base_b),
        hex_b, len(hex_b),
        ctypes.c_int64(difficulty),
    )
    if rc == -2:
        raise PowSolverError("CPU does not support AVX2")
    if rc < 0:
        raise PowSolverError(
            f"PoW solver returned {rc} (invalid base/challenge/difficulty?)"
        )
    return int(rc)
