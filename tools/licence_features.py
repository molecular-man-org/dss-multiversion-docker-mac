#!/usr/bin/env python3
"""List licence features a node has disabled, excluding tracking-policy flags.

Read-only.  Usage: tools/licence_features.py <nickname>
"""
import sys
from _dsslab_common import POLICY_FLAGS, api, instance, offer

code, st = api(instance(sys.argv[1]), "/admin/licensing/status")
if code != 200:
    sys.exit(f"licensing status returned {code}: {st}")
feats = st.get("features", {})
disabled = sorted(k for k, v in feats.items() if v is False and k not in POLICY_FLAGS)
print(f"{sys.argv[1]}  offer={offer(st)}  {len(feats)} feature entries")
print(f"  disabled: {disabled or 'NONE'}")
