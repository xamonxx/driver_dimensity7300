"""Map offsets from xamonxx_mali7300_crash.log to function names.

Usage:
    python -I tools/symbolize_crash.py <unstripped libvulkan_panfrost.so> <crash.log | 0xOFFSET ...>

The unstripped library comes from the CI artifact "symbols-debug30" of the same build
(identical code layout to the released, stripped driver). Lines in the crash log of the form
"in libvulkan driver at offset 0x..." are resolved to the nearest preceding function symbol.
"""
import bisect
import re
import struct
import sys


def load_functions(path):
    data = open(path, "rb").read()
    if data[:4] != b"\x7fELF" or data[4] != 2:
        sys.exit("not an ELF64 file")
    e_shoff = struct.unpack_from("<Q", data, 0x28)[0]
    e_shentsize, e_shnum, _ = struct.unpack_from("<HHH", data, 0x3A)
    secs = []
    for i in range(e_shnum):
        off = e_shoff + i * e_shentsize
        _n, stype, _f, _a, soff, ssize, link, _i, _al, _es = struct.unpack_from("<IIQQQQIIQQ", data, off)
        secs.append((stype, soff, ssize, link))
    funcs = {}
    for stype, soff, ssize, link in secs:
        if stype not in (2, 11):  # SHT_SYMTAB, SHT_DYNSYM
            continue
        stroff = secs[link][1]
        for j in range(0, ssize, 24):
            st_name, st_info, _o, st_shndx, st_value, st_size = struct.unpack_from("<IBBHQQ", data, soff + j)
            if (st_info & 0xF) == 2 and st_value and st_shndx:  # STT_FUNC, defined
                end = data.find(b"\x00", stroff + st_name)
                funcs[st_value] = (data[stroff + st_name:end].decode("utf-8", "replace"), st_size)
    if not funcs:
        sys.exit("no function symbols: use the UNSTRIPPED library from the symbols-debug30 artifact")
    addrs = sorted(funcs)
    return addrs, funcs


def resolve(addrs, funcs, off):
    i = bisect.bisect_right(addrs, off) - 1
    if i < 0:
        return "?"
    base = addrs[i]
    name, size = funcs[base]
    inside = "" if not size or off < base + size else " (past end, nearest)"
    return f"{name}+0x{off - base:x}{inside}"


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    addrs, funcs = load_functions(sys.argv[1])
    targets = sys.argv[2:]
    if len(targets) == 1 and not targets[0].startswith("0x"):
        for line in open(targets[0], encoding="utf-8", errors="replace"):
            line = line.rstrip("\n")
            m = re.search(r"at offset (0x[0-9a-f]+)", line)
            print(line + (f"   => {resolve(addrs, funcs, int(m.group(1), 16))}" if m else ""))
    else:
        for t in targets:
            print(t, "=>", resolve(addrs, funcs, int(t, 16)))


if __name__ == "__main__":
    main()
