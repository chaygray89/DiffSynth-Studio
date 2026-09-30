from pathlib import Path
import base64
import hashlib
import tarfile

EXPECTED = "cc258e2015b18988adb01026894559b7f45857eb005822874042c0b64bc73885"

root = Path(__file__).resolve().parent
parts_dir = root / "parts"
parts = sorted(parts_dir.glob("part*.b64"))

if len(parts) != 13:
    raise SystemExit(f"Expected 13 bundle parts, found {len(parts)}")

raw = "".join(p.read_text(encoding="utf-8").strip() for p in parts)
data = base64.b64decode(raw, validate=True)
actual = hashlib.sha256(data).hexdigest()

if actual != EXPECTED:
    raise SystemExit(f"Bundle checksum mismatch: {actual} != {EXPECTED}")

archive = root / "bundle.tar.gz"
archive.write_bytes(data)

runtime = root / "runtime"
runtime.mkdir(parents=True, exist_ok=True)
runtime_resolved = runtime.resolve()

with tarfile.open(archive, "r:gz") as tf:
    members = tf.getmembers()
    for member in members:
        target = (runtime / member.name).resolve()
        if target != runtime_resolved and runtime_resolved not in target.parents:
            raise SystemExit(f"Unsafe path in archive: {member.name}")
    tf.extractall(runtime)

print(f"Kavqor bundle verified: {actual}")
