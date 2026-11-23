"""Audit Mali (PanVK / kbase) driver zips for AdrenoTools-style loaders.

Usage:
    python -I tools/audit_mali_driver.py <zip|folder> [...] [--sums SHA256SUMS] [--expect STRING ...]

Checks per zip:
  * SHA256 (and match against a SHA256SUMS file when given), CRC, path traversal
  * file list (only .so / meta.json / NOTICE / README / LICENSE expected)
  * meta.json fields and that libraryName exists in the zip
  * ELF: 64-bit, aarch64, shared object, DT_NEEDED libraries, exported dynamic symbols
  * Vulkan ICD entry points (vk_icdGetInstanceProcAddr / vkGetInstanceProcAddr / HMI)
  * Mali-specific strings: kbase, /dev/mali0, Mali-G615, panvk, Mesa version
  * suspicious strings (shell exec, su, curl/wget, URLs other than known docs)
Exit code 0 only if every zip passes the hard checks.
"""
import hashlib
import json
import os
import re
import struct
import sys
import zipfile

ANDROID_SYSTEM_LIBS = {
    "libc.so", "libm.so", "libdl.so", "liblog.so", "libz.so", "libsync.so",
    "libnativewindow.so", "libhardware.so", "libandroid.so", "libcutils.so",
    "libutils.so", "libui.so", "libvndksupport.so", "libEGL.so",
}
ALLOWED_EXTRA = re.compile(r"(?i)(notice|license|readme|copying|sha256sums)[^/]*$")
SUSPICIOUS = re.compile(
    rb"(/system/bin/sh\x00|/system/xbin/su|\bsu -c\b|chmod 777|curl |wget |"
    rb"Runtime\.getRuntime|/data/local/tmp/[a-z]+\.sh|nc -e)"
)


# --------------------------------------------------------------------------- ELF
def parse_elf(data):
    """Minimal ELF64 little-endian parser: header, DT_NEEDED, dynamic symbols."""
    info = {"ok": False}
    if data[:4] != b"\x7fELF":
        return info
    info["class64"] = data[4] == 2
    info["little"] = data[5] == 1
    if not (info["class64"] and info["little"]):
        return info
    e_type, e_machine = struct.unpack_from("<HH", data, 16)
    info["type"] = {2: "EXEC", 3: "DYN"}.get(e_type, str(e_type))
    info["aarch64"] = e_machine == 183
    e_shoff = struct.unpack_from("<Q", data, 0x28)[0]
    e_shentsize, e_shnum, e_shstrndx = struct.unpack_from("<HHH", data, 0x3A)
    sections = []
    for i in range(e_shnum):
        off = e_shoff + i * e_shentsize
        if off + 64 > len(data):
            break
        name, stype, _flags, _addr, soff, ssize, link, _info, _align, entsize = struct.unpack_from(
            "<IIQQQQIIQQ", data, off)
        sections.append(dict(name=name, type=stype, off=soff, size=ssize, link=link, entsize=entsize))

    def cstr(base, idx):
        end = data.find(b"\x00", base + idx)
        return data[base + idx:end].decode("utf-8", "replace")

    needed, symbols = [], []
    for s in sections:
        if s["type"] == 6:  # SHT_DYNAMIC
            strtab = sections[s["link"]]["off"]
            for j in range(0, s["size"], 16):
                tag, val = struct.unpack_from("<qQ", data, s["off"] + j)
                if tag == 0:
                    break
                if tag == 1:  # DT_NEEDED
                    needed.append(cstr(strtab, val))
        if s["type"] == 11:  # SHT_DYNSYM
            strtab = sections[s["link"]]["off"]
            for j in range(0, s["size"], 24):
                st_name, st_info, _o, st_shndx = struct.unpack_from("<IBBH", data, s["off"] + j)
                bind = st_info >> 4
                if st_name and st_shndx != 0 and bind in (1, 2):  # defined GLOBAL/WEAK
                    symbols.append(cstr(strtab, st_name))
    info.update(ok=True, needed=needed, symbols=symbols)
    return info


# --------------------------------------------------------------------------- audit
def load_sums(path):
    sums = {}
    if path and os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            parts = line.split()
            if len(parts) == 2:
                sums[parts[1].lstrip("*")] = parts[0].lower()
    return sums


def audit(path, sums, expects):
    hard_ok = True
    notes = []
    print("=" * 78)
    print(os.path.basename(path), f"({os.path.getsize(path):,} bytes)")
    digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
    print("SHA256 ", digest)
    if sums:
        want = sums.get(os.path.basename(path))
        if want is None:
            print("  checksum: not listed in SHA256SUMS")
        elif want == digest:
            print("  checksum: MATCH (SHA256SUMS)")
        else:
            print("  checksum: MISMATCH !!")
            hard_ok = False

    z = zipfile.ZipFile(path)
    bad = z.testzip()
    print("CRC    ", bad or "OK")
    hard_ok &= bad is None

    names = [i.filename for i in z.infolist() if not i.is_dir()]
    for i in z.infolist():
        trav = i.filename.startswith("/") or ".." in i.filename.split("/")
        hard_ok &= not trav
        print(f"  {i.filename:55} {i.file_size:>11,}" + ("  !!PATH" if trav else ""))

    meta = None
    for n in names:
        if n.endswith("meta.json"):
            try:
                meta = json.loads(z.read(n))
                print("  meta:", json.dumps(meta, ensure_ascii=False))
            except Exception as e:  # noqa: BLE001
                print("  meta.json INVALID:", e)
                hard_ok = False
    if meta and meta.get("libraryName"):
        lib = meta["libraryName"]
        if not any(n.endswith("/" + lib) or n == lib for n in names):
            print(f"  !! libraryName {lib} not present in zip")
            hard_ok = False

    for n in names:
        data = z.read(n)
        base = n.rsplit("/", 1)[-1]
        if data[:4] == b"\x7fELF":
            e = parse_elf(data)
            if not e["ok"]:
                print(f"  ELF {base}: unsupported (not ELF64 LE)")
                hard_ok = False
                continue
            print(f"  ELF {base}: 64-bit aarch64={e['aarch64']} type={e['type']}")
            hard_ok &= e["aarch64"] and e["type"] == "DYN"
            nonstd = [x for x in e["needed"] if x not in ANDROID_SYSTEM_LIBS]
            print(f"    NEEDED: {', '.join(e['needed'])}")
            if nonstd:
                notes.append(f"{base}: non-system NEEDED {nonstd}")
                print(f"    !! non-system NEEDED: {nonstd}")
            syms = set(e["symbols"])
            icd = sorted(s for s in syms if s in ("HMI", "vk_icdGetInstanceProcAddr",
                                                  "vk_icdNegotiateLoaderICDInterfaceVersion",
                                                  "vkGetInstanceProcAddr"))
            print(f"    exported entry points: {icd or 'NONE'}  (dynsym defined: {len(syms)})")
            if not icd:
                hard_ok = False
            mesa = sorted({m.decode() for m in re.findall(rb"Mesa \d+\.\d+\.\d+[-\w]*(?: \(git-[0-9a-f]+[^)\x00]{0,40}\))?", data)})[:2]
            flags = {k: (k.encode() in data) for k in ("kbase", "/dev/mali", "Mali-G615", "panvk", "CSF")}
            print(f"    mesa: {mesa}")
            print(f"    strings: {flags}")
            if not (flags["kbase"] and flags["/dev/mali"]):
                notes.append(f"{base}: no kbase backend strings (will not run on stock Android Mali)")
            for ex in expects:
                found = ex.encode() in data
                print(f"    expect '{ex}': {found}")
                hard_ok &= found
            sus = sorted({m.decode(errors='replace') for m in SUSPICIOUS.findall(data)})
            if sus:
                notes.append(f"{base}: suspicious strings {sus}")
                print(f"    !! suspicious: {sus}")
        elif base == "meta.json" or ALLOWED_EXTRA.search(base) or base.endswith(".json"):
            continue
        else:
            notes.append(f"unexpected file {n}")
            print(f"  !! unexpected file: {n} head={data[:12]!r}")

    for n_ in notes:
        print("  NOTE:", n_)
    print("RESULT:", "PASS" if hard_ok else "FAIL", f"({len(notes)} note(s))")
    return hard_ok


def main(argv):
    sums_path, expects, targets = None, [], []
    it = iter(argv)
    for a in it:
        if a == "--sums":
            sums_path = next(it)
        elif a == "--expect":
            expects.append(next(it))
        else:
            targets.append(a)
    files = []
    for t in targets or ["dist"]:
        if os.path.isdir(t):
            files += [os.path.join(t, f) for f in sorted(os.listdir(t)) if f.endswith(".zip")]
        else:
            files.append(t)
    sums = load_sums(sums_path)
    results = [audit(f, sums, expects) for f in files]
    sys.exit(0 if results and all(results) else 1)


if __name__ == "__main__":
    main(sys.argv[1:])
