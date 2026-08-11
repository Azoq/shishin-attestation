# Shishin attestation log

A public, tamper-evident, timestamped record of the daily signals and net asset value (NAV) published by [Shishin](https://shishin.io).

Shishin is a non-advisory quantitative research publisher. This log exists so anyone can independently verify that a signal or NAV figure we published was committed to at a provable time and has not been altered since. You do not have to trust us. You can check the math yourself with open tools.

## What this proves, and what it does not

**It proves:**
- each day's published signals and NAV existed, unaltered, at the moment the commitment was timestamped, which is **before that day's trades executed and before the day's outcome was known** (the commitment lands within minutes of the 09:30 ET open; entries fill later the same session), and
- the published record has not been altered since.

**It does not prove:**
- **that the selection predates the market open.** It cannot, by construction: the scanner runs after the open and uses the day's opening price as a scoring input, so the picks do not exist until a few minutes into the session. The commitment is made as soon as they exist. See [When the commitment lands](#when-the-commitment-lands) for the exact clock.
- that any trade was a real broker fill. The Shishin track record is **paper-traded**; this log attests the *predictions*, not executions.
- that the strategy is or will be profitable.

## When the commitment lands

The precise timeline matters more than a general claim of being "in advance", so here it is:

| Time (ET) | What happens |
|---|---|
| 09:30 | Market opens. |
| ~09:36 | The scanner finishes. It consumes the day's opening print, so **the selection does not exist before this point.** |
| ~09:40 | **The hash is committed here** and sent to OpenTimestamps. |
| later in the session | Entries fill. The day's outcome is still unknown at commit time. |

The window that a commitment cannot cover is the ~10 minutes between the open and the moment the selection exists. We publish that limitation rather than round it away. Everything the record is used for , whether a published pick preceded its own result , sits comfortably inside the proven window.

## How it works: commit, then reveal

Each trading day is recorded in two steps, on two clocks.

1. **Commit (same day, immediately).** We build the day's payload (signals, NAV, a ledger digest, and a random nonce), hash it together with the previous day's hash, and publish only that hash in `chain/<date>.json`. We also timestamp the hash with [OpenTimestamps](https://opentimestamps.org), which anchors it to the Bitcoin blockchain (`*.ots`). A hash reveals nothing about its contents, and the random nonce makes the picks impossible to brute-force, so this step leaks no signal while locking in what we chose and when.
2. **Reveal (after the free-tier delay).** Once a day's signals are already available to free users, we publish the full payload in `reveals/<date>.json`. Anyone can then recompute the hash and confirm it matches the commitment we timestamped earlier.

The delayed reveal is deliberate: it stops the public log from giving paid subscribers' signals away early, while the commit step still proves we called them in advance.

## The hash chain

```
H[t] = SHA256( canonical(payload[t]) || "|" || H[t-1] )
```

- `canonical(payload)` is the payload serialized as compact JSON with sorted keys (UTF-8, separators `,` and `:`), with every number encoded as a string so the result is reproducible in any language.
- `H[t-1]` is the previous day's hash (hex). Each day folds in the previous hash, so altering any past day breaks every later hash.
- Genesis (the `prev_hash` for the first day): `H[-1] = SHA256("shishin-attestation/v1")` = `7f84c4acde0c8d97e477c3bf57f9032a6c516a8c4328d3ebfb60cd3758aac391`.

## Verify it yourself

```
python verify.py 2026-06-27
```

`verify.py` reads `reveals/<date>.json` and `chain/<date>.json`, recomputes the chained hash with the standard library only, and checks it against the published commitment. To verify the timestamp, install the OpenTimestamps client and run `ots verify chain/<date>.json.ots`.

## Layout

- `chain/<date>.json` — the daily commitment: `{date, commit_hash, prev_hash, committed_utc}`, plus a `.ots` timestamp proof.
- `reveals/<date>.json` — the revealed payload, published after the free-tier delay.
- `verify.py` — recompute and check any revealed day, standard library only.

## Ledger notes

Anything irregular about a specific day is recorded here rather than left for a reader to discover.

- **2026-06-26 is a backfill.** This log was created on 2026-06-27. Its first entry, the trading day 2026-06-26, was committed retroactively that morning (`committed_utc` 2026-06-27T08:39:27Z, about 33 hours after the trading date), so **that day's commitment carries no forward-looking claim**: the outcome was already known when the hash was made. It is included for chain continuity, not as evidence. Every day from **2026-06-29** onward, the log's first live day, was committed during its own trading session. `committed_utc` in each `chain/<date>.json` states the real commit time, and the OpenTimestamps proof is independent of anything we assert, so this is checkable rather than merely disclosed.
