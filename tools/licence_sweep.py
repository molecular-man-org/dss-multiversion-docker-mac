#!/usr/bin/env python3
"""Apply every licence to a LOCAL node in turn; record profiles and features.

Measures which user profiles and features each licence gives on a given DSS
version, and which licences the version cannot use at all. Restores the
baseline 2024 licence at the end.

This CHANGES the node's licence. It refuses any node whose URL is not
localhost — internet-hosted DSS nodes must never be changed.

Usage: tools/licence_sweep.py <nickname>   e.g. dss-12.6.7
Results from 2026-09-11: docs/findings/licence-profiles-and-features.md
"""
import glob
import os
import subprocess
import sys
import time
from _dsslab_common import (BASELINE_GLOB, LICENSE_DIR, POLICY_FLAGS, api, instance,
                            is_local, licence_files, offer)

nick = sys.argv[1]
inst = instance(nick)
if not is_local(inst["url"]):
    sys.exit(f"refusing: {nick} is at {inst['url']}, not localhost. "
             "This script changes licences and must never touch an internet node.")
# docker inspect succeeds on a stopped container too, so check it is running.
running = subprocess.run(["docker", "inspect", "-f", "{{.State.Running}}", nick],
                         capture_output=True, text=True)
if running.returncode != 0:
    sys.exit(f"refusing: no local container named {nick}")
if running.stdout.strip() != "true":
    sys.exit(f"refusing: {nick} is not running (dss-lab up <version>)")

files = licence_files()
if not files:
    sys.exit(f"no licence files matched in {LICENSE_DIR} (set DSS_LAB_LICENSE_DIR)")


def apply(path):
    subprocess.run(["docker", "cp", path, f"{nick}:/tmp/sweep.json"], check=True, capture_output=True)
    r = subprocess.run(["docker", "exec", nick, "/home/dataiku/dss/bin/dsscli", "set-license",
                        "/tmp/sweep.json"], capture_output=True, text=True)
    # docker cp writes as root; dataiku cannot delete it, so clean up as root.
    subprocess.run(["docker", "exec", "-u", "root", nick, "rm", "-f", "/tmp/sweep.json"],
                   capture_output=True)
    time.sleep(2)
    return r.returncode


for path in files:
    rc = apply(path)
    code, st = api(inst, "/admin/licensing/status")
    name = os.path.basename(path)
    if code != 200:
        # set-license exits 0 even for a licence the node cannot parse.
        print(f"{name:36} set-license exit={rc}  status={code}  UNUSABLE: {str(st)[:70]}")
        continue
    profiles = st["base"].get("userProfiles", [])
    disabled = sorted(k for k, v in st.get("features", {}).items()
                      if v is False and k not in POLICY_FLAGS)
    print(f"{name:36} [{offer(st)}]  profiles={profiles}  disabled={disabled or 'NONE'}")

baseline = sorted(glob.glob(os.path.join(LICENSE_DIR, BASELINE_GLOB)))
if baseline:
    apply(baseline[0])
    code, st = api(inst, "/admin/licensing/status")
    print(f"RESTORED baseline -> status {code}, offer {offer(st) if code == 200 else st}")
else:
    print(f"WARNING: no {BASELINE_GLOB} in {LICENSE_DIR}; node left on the last licence applied")
