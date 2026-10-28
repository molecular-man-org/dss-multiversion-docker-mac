"""Shared helpers for the tools/ research scripts. Stdlib only.

Paths follow the same conventions as bin/lib/provision.sh:
  DKU_CONFIG_FILE      default ~/.dataiku/config.json
  DSS_LAB_LICENSE_DIR  default ~/.dataiku/licenses
"""
import base64
import glob
import json
import os
import urllib.error
import urllib.parse
import urllib.request

CONFIG = os.environ.get("DKU_CONFIG_FILE", os.path.expanduser("~/.dataiku/config.json"))
LICENSE_DIR = os.environ.get(
    "DSS_LAB_LICENSE_DIR", os.path.expanduser("~/.dataiku/licenses"))

# Sweep order: oldest licence model first. This is NOT provision.sh's preference
# order (LICENSE_GLOBS there tries the 2024 licence first); a sweep applies them
# all, so order only affects the output. Globs, never exact names: the user
# portion of the filename belongs to one person's licence set.
LICENSE_GLOBS = ["dev-*-2018.json", "dev-*-2024.json", "dev-*-2025-aiml.json",
                 "dev-*-2025-analytics.json", "dev-*-2025-enterprise.json"]
BASELINE_GLOB = "dev-*-2024.json"

# Tracking/terms policy flags where False is the permissive setting, not a
# disabled feature.
POLICY_FLAGS = {"forbiddenTracking", "lockedTracking", "mandatoryMinimalTracking",
                "aiServicesTermsPreAccepted"}


def instance(nickname):
    with open(CONFIG) as f:
        return json.load(f)["dss_instances"][nickname]


def is_local(url):
    return urllib.parse.urlparse(url).hostname in ("localhost", "127.0.0.1")


def api(inst, path):
    """GET a public-API path. Returns (status, parsed body or error message)."""
    req = urllib.request.Request(f"{inst['url']}/public/api{path}")
    token = base64.b64encode(f"{inst['api_key']}:".encode()).decode()
    req.add_header("Authorization", f"Basic {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as ex:
        try:
            return ex.code, json.loads(ex.read().decode()).get("message", "")
        except Exception:
            return ex.code, ""


def licence_files():
    """Licence files in preference order, one per glob."""
    out = []
    for g in LICENSE_GLOBS:
        hits = sorted(glob.glob(os.path.join(LICENSE_DIR, g)))
        if hits:
            out.append(hits[0])
    return out


def offer(status_body):
    props = (status_body.get("base", {}).get("licenseContent", {}) or {}).get("properties", {}) or {}
    return props.get("standardOffer") or props.get("licenseLimitsVersion")
