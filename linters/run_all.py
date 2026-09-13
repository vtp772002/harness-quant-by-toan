"""Run all linters — Ralph Wiggum Loop bước 1."""
import subprocess, sys
ok = True
for f in ["linters/layering.py", "linters/no_lookahead.py", "linters/determinism.py", "linters/taste.py"]:
    r = subprocess.run([sys.executable, f])
    ok &= r.returncode == 0
sys.exit(0 if ok else 1)
