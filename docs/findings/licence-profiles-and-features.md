# Licences decide the user profile; some DSS versions reject some licences

**Date:** 2026-09-11
**Status:** measured on live nodes
**Method:** each of the five internal licences applied in turn to 11.2.0, 12.6.7,
13.5.7 and 14.7.3 with `dsscli set-license`, then
`GET /admin/licensing/status` and `GET /admin/users/admin` read back. Every node
was restored to the 2024 licence afterwards. Machine-readable results:
[`data/user-profiles.json`](../../data/user-profiles.json).
Reproduce on any running local node with `tools/licence_sweep.py <nickname>`.

## 1. The profile type comes from the licence, not the DSS version

| Licence file | Offer | Designer profile it offers |
| --- | --- | --- |
| `dev-*-2018.json` | `SAER` | `DATA_SCIENTIST` (+ `DATA_ANALYST`) |
| `dev-*-2024.json` | `enterprise-fy2023-1` | `DESIGNER` |
| `dev-*-2025-*.json` | `*-fy2025-1` | `FULL_DESIGNER` |

Identical on every DSS version tested. The DSS version only adds peripheral
profile types — `AI_CONSUMER` appears from 12.6.6 (absent on 12.4.2, present on
12.6.7 under the same licence), `AI_ACCESS_USER` on 13/14.

This explains the reported "DSS 14.7 needs `FULL_DESIGNER`": that node carried a
2025 licence. Under the 2024 licence, 14.7.3 offers `DESIGNER` and no
`FULL_DESIGNER` at all.

## 2. The admin bug: installed on a profile only the oldest licence offers

Admin's **stored** profile is `DATA_SCIENTIST` on every version tested — the
`SAER`-era default. Only the 2018 licence offers it. Under any other licence DSS
cannot honour it and counts admin under the licence's `fallbackProfile`, which is
`EXPLORER` (`profileLimits.EXPLORER.directCount = 1`).

So admin is not *set* to `EXPLORER`. It is set to an unlicensed profile and
**silently demoted**. Reading `userProfile` alone would show `DATA_SCIENTIST` and
look fine; the demotion is only visible by checking that profile against
`base.userProfiles`.

`dss-12.4.2` showed admin on `DESIGNER` — not the install default, and probably
changed by another session. Unverified.

## 3. Some DSS versions reject some licences — and `set-license` still exits 0

DSS 11.2.0 cannot use any 2025 licence:

```text
Unrecognized standard offer 'ai-ml-fy2025-1', you may need to upgrade this DSS
```

**`dsscli set-license` accepted each of them with exit 0.** The node is left with
a persisted licence it cannot parse, and `GET /admin/licensing/status` then
returns **400** for every caller. `dss-lab`'s readiness probe polls that exact
endpoint, so a node in this state would never read as ready.

Re-applying a compatible licence recovers it.

12.6.7 and later accept all five licences. The version where the fy2025 offers
became usable lies somewhere in (11.2.0, 12.6.7]; 12.4.2 was not tested.

## 4. No single licence enables every feature on DSS 14

"Disabled" excludes four tracking/terms policy flags, where `false` is the
permissive setting.

| Licence | 11.2.0 / 12.6.7 / 13.5.7 | 14.7.3 |
| --- | --- | --- |
| 2018 `SAER` | **nothing disabled** | business apps, enterprise projects, project standards |
| 2024 `fy2023` | model export ×3 | model export ×3 |
| 2025 `enterprise` | model export ×3 (unusable on 11) | model export ×3 |
| 2025 `ai-ml` | 4-5 disabled | 8 disabled |
| 2025 `analytics` | 7-9 disabled | 12 disabled |

"Model export ×3" is `modelsJarExport`, `modelsPMMLExport`, `modelsRawSQLExport`.

- On **11.x-13.x**, the 2018 licence enables everything that exists — and admin
  needs no profile change under it.
- On **14.x**, the 2018 licence lacks three newer features and every other licence
  lacks model export. Full coverage there needs a licence that does not exist in
  the current set.
- The 2025 `ai-ml` and `analytics` offers are deliberately restricted; avoid them
  for anything meant to exercise the whole product.

## 5. A cleanup that silently did nothing

`license_apply` stages the licence at `/tmp/dss-lab-license.json` and then runs
`docker exec <c> rm -f` on it. `docker cp` writes the file as root and
`docker exec` runs as `dataiku`, so the delete fails — and
`>/dev/null 2>&1 || true` hides it. Both running nodes still held the file.
`PROVISIONING.md` states the copy is removed. Fix: `docker exec -u root`.

## Implications for provisioning

- `set-license` exit 0 is **not evidence** a licence took. Gate on
  `GET /admin/licensing/status` returning 200 with the expected offer.
- Fixing admin means checking its stored profile **against the licence's offered
  profiles**, then moving it to the licence's designer profile — per the table in
  section 1.
