#!/usr/bin/env python3
"""
package_skill.py — Bundle the thesis-engine Antigravity port (.agent/ tree) into an archive.
Run: python package_skill.py
Output: thesis-engine.skill (zip archive, rename to .skill)

Port note: the Claude Code original resolved SKILL_DIR off skills/thesis-engine/scripts/
(two levels up). In the Antigravity port the scripts live flat under .agent/scripts/, so
the bundle root is .agent/ — one level up from this file.
"""

import zipfile
from pathlib import Path

BUNDLE_DIR = Path(__file__).parent.parent  # .agent/
OUTPUT_NAME = "thesis-engine.skill"

def package():
    out = Path(OUTPUT_NAME)
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in BUNDLE_DIR.rglob('*'):
            if file.is_file() and '.git' not in str(file) and '__pycache__' not in str(file):
                arcname = file.relative_to(BUNDLE_DIR.parent)
                zf.write(file, arcname)
    print(f"Packaged: {out.resolve()}")
    print(f"   Install by placing .agent/ in your Antigravity workspace.")

if __name__ == '__main__':
    package()
