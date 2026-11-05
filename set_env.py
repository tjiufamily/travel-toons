#!/usr/bin/env python3
"""One-off: set Travel Toons' production secrets on Vercel.
Mirrors Cornerstone's set_env.py. Reads the password from stdin
(never stored, never printed), hashes it with the app's own api/_lib.js
(scrypt), generates a random session secret, and creates both as
'sensitive' production env vars via the Vercel connector.

The password is the SAME password as Cornerstone, so the sign-in
you already know stays the same. Run: python3 set_env.py < then type
the password and press Enter (input is not echoed to a file).
"""
import json, secrets, subprocess, sys
from pathlib import Path

ROOT = Path.home() / "workspace/travel-toons"
CLI = "/opt/hatch/bin/vercel"

def call(name, args):
    r = subprocess.run([CLI, "call-tool", "--name", name,
                        "--arguments-json", json.dumps(args)],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise SystemExit(f"{name} failed: {r.stdout[-400:]} {r.stderr[-200:]}")
    return r.stdout[-200:]

def main():
    pw = sys.stdin.readline().rstrip("\n")
    if not pw:
        raise SystemExit("no password on stdin")
    node_code = ("const fs=require('fs');"
                 "const lib=require(process.argv[1]);"
                 "const pw=fs.readFileSync(0,'utf8').replace(/\\n$/,'');"
                 "process.stdout.write(lib.hashPassword(pw));")
    h = subprocess.run(["node", "-e", node_code, str(ROOT / "api/_lib.js")],
                       input=pw, capture_output=True, text=True)
    if h.returncode != 0:
        raise SystemExit("hash failed: " + h.stderr[-300:])
    pw_hash = h.stdout.strip()
    assert pw_hash.count(":") == 1 and len(pw_hash) > 60, "unexpected hash format"
    session_secret = secrets.token_urlsafe(32)
    project = json.loads((ROOT / ".project.json").read_text())["projectId"]
    for key, value in [("TRAVEL_TOONS_PASSWORD_HASH", pw_hash),
                       ("TRAVEL_TOONS_SESSION_SECRET", session_secret)]:
        call("create_project_env", {"idOrName": project,
                                    "requestBody": {"key": key, "value": value,
                                                    "type": "sensitive",
                                                    "target": ["production"]}})
        print("set", key)
    print("done")

if __name__ == "__main__":
    main()
