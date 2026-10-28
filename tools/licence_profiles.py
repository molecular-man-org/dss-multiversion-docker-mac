#!/usr/bin/env python3
"""Show the licensed user profiles on a node and whether admin is demoted.

Read-only.  Usage: tools/licence_profiles.py <nickname>   e.g. dss-14.7.3
"""
import sys
from _dsslab_common import api, instance, offer

inst = instance(sys.argv[1])
code, st = api(inst, "/admin/licensing/status")
if code != 200:
    sys.exit(f"licensing status returned {code}: {st}")
base, limits = st.get("base", {}), st.get("limits", {}).get("profileLimits", {})
profiles = base.get("userProfiles", [])
print(f"{sys.argv[1]}  offer={offer(st)}  fallbackProfile={base.get('fallbackProfile')}")
for p in sorted(set(profiles) | set(limits)):
    lim = limits.get(p, {})
    ll = (lim.get("licensed") or {}).get("licensedLimit")
    print(f"  {p:26} limit={'unlimited' if ll == -1 else ll}  directCount={lim.get('directCount', 0)}")
_, admin = api(inst, "/admin/users/admin")
stored = admin.get("userProfile") if isinstance(admin, dict) else None
state = "licensed" if stored in profiles else "NOT licensed -> silently demoted to the fallback profile"
print(f"  admin stored profile: {stored}  ({state})")
