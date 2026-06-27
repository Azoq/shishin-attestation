# Shishin attestation log

A public, tamper-evident, timestamped record of the daily signals and net asset value (NAV) published by [Shishin](https://shishin.io).

Shishin is a non-advisory quantitative research publisher. This log exists so anyone can independently verify that a signal or NAV figure we published was committed to in advance and has not been altered since. You do not have to trust us. You can check the math yourself with open tools.

## What this proves, and what it does not

**It proves:**
- each day's published signals and NAV were committed to at a specific time, so calling a move in advance is provable, and
- the published record has not been altered since.

**It does not prove:**
- that any trade was a real broker fill. The Shishin track record is **paper-traded**; this log attests the *predictions*, not executions.
- that the strategy is or will be profitable.

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
