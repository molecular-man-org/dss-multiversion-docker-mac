# tools

Reusable research and diagnostic scripts. Standard library only. They are not
part of the `dss-lab` CLI and not exercised by `tests/run_tests.sh` beyond a
compile check and the sweep's localhost guard.

Paths follow `bin/lib/provision.sh`: `DKU_CONFIG_FILE` (default
`~/.dataiku/config.json`) and `DSS_LAB_LICENSE_DIR` (default
`~/.dataiku/licenses`).

| Script | Changes the node? | What it does |
| --- | --- | --- |
| `seed_zip_inspect.py <zip>...` | no | A DSS project export's source version, recipe and dataset types, connections, plugin recipes and cross-project refs |
| `licence_profiles.py <nickname>` | no | Licensed user profiles with their limits and `directCount`, and whether admin's stored profile is licensed or silently demoted |
| `licence_features.py <nickname>` | no | Licence features the node has disabled, excluding tracking-policy flags |
| `licence_sweep.py <nickname>` | **yes** | Applies every licence in turn, records profiles and features (or the "unrecognized offer" 400), then restores the 2024 licence |

`licence_sweep.py` refuses any node whose URL is not `localhost`, and any
container that is not running. Internet-hosted DSS nodes must never be changed.
Results it reproduces:
[`docs/findings/licence-profiles-and-features.md`](../docs/findings/licence-profiles-and-features.md).
