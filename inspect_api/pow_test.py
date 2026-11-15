import asyncio
import os
import statistics
import time

from dotenv import load_dotenv

from aiodeepseek import DeepSeekClient
from aiodeepseek.data.constants import COMPLETION_PATH
from aiodeepseek.pow.pow import solve_pow

load_dotenv()

async def solve_single_pow(client: DeepSeekClient, token: str, index: int):
    challenge = await client._get_pow_challenge(
        token,
        COMPLETION_PATH,
    )

    salt = challenge["salt"]
    expire_at = challenge["expire_at"]
    difficulty = int(challenge["difficulty"])
    challenge_hex = challenge["challenge"]

    started = time.perf_counter()
    nonce = solve_pow(
        f"{salt}_{expire_at}_",
        challenge_hex,
        difficulty,
    )

    elapsed = time.perf_counter() - started

    return {
        "index": index,
        "difficulty": difficulty,
        "nonce": nonce,
        "elapsed": elapsed,
    }


async def main(n_runs: int = 10) -> int:
    token = os.environ["DEEPSEEK_TOKEN"]
    async with DeepSeekClient(token=token) as client:
        # warm-up: exclude from stats
        await solve_single_pow(client, token, 0)

        results = await asyncio.gather(
            *(solve_single_pow(client, token, i + 1) for i in range(n_runs)),
            return_exceptions=True,
        )

    errors = [r for r in results if isinstance(r, BaseException)]
    ok = [r for r in results if not isinstance(r, BaseException)]

    for e in errors:
        print(f"FAILED: {e!r}")
    if not ok:
        return 1

    for r in ok:
        print(f"[{r['index']}] difficulty={r['difficulty']} "
              f"nonce={r['nonce']!s:.16}… time={r['elapsed']*1000:.4f} ms")

    times = [r["elapsed"] for r in ok]
    print(f"\nRuns: {len(ok)}  Failures: {len(errors)}")
    print(f"Average solve_pow: {statistics.mean(times)*1000:.4f} ms")
    print(f"Min: {min(times)*1000:.4f} ms   Max: {max(times)*1000:.4f} ms")
    return 0

if __name__ == "__main__":
    asyncio.run(main())
