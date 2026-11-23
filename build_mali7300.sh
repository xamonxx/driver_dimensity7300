#!/usr/bin/env bash
# xamonxx mali7300 — Mesa PanVK on mali_kbase for Mali-G615 MC2 (Infinix Note 50X, Dimensity 7300)
#
# Reproduces the zenithblue-oss/panvk-kbase-android v26.3.1 release recipe
# (Mesa 5a07217f + prepare-rc5-tree.sh series, patch level p0175, profile g615-v11-csf, API 29)
# and adds:
#   * CPU tuning for Cortex-A78/A55 (ARMv8.2-A features verified on the device),
#   * patches/xamonxx/0001_frame_pacer.py (precise frame pacer, cap compiled per variant).
#
# Usage (Linux x86_64, CI):  VARIANT=stable30|stable60|nocap  bash build_mali7300.sh
# Output: dist/xamonxx_mali7300V<ver>-<variant>.zip and ...-<variant>-freedreno.zip
set -euo pipefail

VERSION="0.1"
VARIANT="${VARIANT:-stable30}"
case "$VARIANT" in
    stable30) FPS_CAP=30 ;;
    stable60) FPS_CAP=60 ;;
    nocap)    FPS_CAP=0 ;;
    *) echo "Unknown VARIANT=$VARIANT (stable30|stable60|nocap)" >&2; exit 1 ;;
esac
TUNE="${TUNE:-1}"   # 1 = A78/A55 tuning, 0 = upstream flags (fallback)

ZB_REPO="https://github.com/zenithblue-oss/panvk-kbase-android.git"
ZB_COMMIT="3c82008657f3edd44cc5fbed4c2f80f8a29c90fc"   # tag panvk-kbase-v26.3.1
MESA_REPO="https://gitlab.freedesktop.org/mesa/mesa.git"
MESA_COMMIT="5a07217f034b3e50d8c7c7794f97a2df1742613b"  # zenithblue sources.lock
NDK_VER="android-ndk-r29"
API=29

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK="$ROOT/work"
ZB="$WORK/zb"
MESA="$WORK/mesa"
NDK="$WORK/$NDK_VER"
DIST="$ROOT/dist"

green='\033[0;32m'; red='\033[0;31m'; nc='\033[0m'
log() { echo -e "${green}[mali7300] $*${nc}"; }
die() { echo -e "${red}[mali7300] $*${nc}" >&2; exit 1; }

fetch_sources() {
    mkdir -p "$WORK"
    if [ ! -d "$NDK" ]; then
        log "Downloading Android NDK r29"
        curl -fsSL "https://dl.google.com/android/repository/${NDK_VER}-linux.zip" -o "$WORK/ndk.zip"
        unzip -q "$WORK/ndk.zip" -d "$WORK"
        rm -f "$WORK/ndk.zip"
    fi

    log "Fetching zenithblue build layer @ ${ZB_COMMIT:0:12}"
    rm -rf "$ZB"
    git init -q "$ZB"
    git -C "$ZB" remote add origin "$ZB_REPO"
    git -C "$ZB" sparse-checkout set --no-cone /scripts/ /patches/ /profiles/ /meson/ /sources.lock /LICENSES/ /NOTICE.md
    git -C "$ZB" fetch -q --depth=1 origin "$ZB_COMMIT"
    git -C "$ZB" checkout -q FETCH_HEAD
    grep -q "$MESA_COMMIT" "$ZB/sources.lock" || die "sources.lock does not pin $MESA_COMMIT"

    log "Fetching Mesa @ ${MESA_COMMIT:0:12}"
    rm -rf "$MESA"
    git init -q "$MESA"
    git -C "$MESA" config user.name "xamonxx-ci"
    git -C "$MESA" config user.email "ci@xamonxx.invalid"
    git -C "$MESA" remote add origin "$MESA_REPO"
    git -C "$MESA" fetch -q --depth=1 origin "$MESA_COMMIT"
    git -C "$MESA" checkout -q FETCH_HEAD
}

prepare_tree() {
    log "Applying release series (prepare-rc5-tree.sh: csf-v11<=233, jm-v7-wip<=0175)"
    sh "$ZB/scripts/prepare-rc5-tree.sh" --mesa "$MESA"
    [ "$(cat "$MESA/.panvk-patchlevel")" = "p0175" ] || die "unexpected patch level $(cat "$MESA/.panvk-patchlevel")"

    log "Applying xamonxx patches"
    (cd "$MESA" && python3 -B "$ROOT/patches/xamonxx/0001_frame_pacer.py")
    grep -q "xamonxx_frame_pace" "$MESA/src/panfrost/vulkan/panvk_wsi.c" || die "frame pacer patch missing"
}

inject_flags() {
    # build-android.sh / build-android-deps.sh derive their cross files from this template.
    local ini="$ZB/meson/android-aarch64.ini"
    local args="'-DXAMONXX_FPS_CAP=$FPS_CAP'"
    if [ "$TUNE" = 1 ]; then
        args="$args, '-march=armv8.2-a+crypto+dotprod+fp16+rcpc', '-mtune=cortex-a78'"
    fi
    printf "\n[built-in options]\nc_args = [%s]\ncpp_args = [%s]\n" "$args" "$args" >> "$ini"
    log "Cross-file built-in options: $args"
}

build_driver() {
    export ANDROID_NDK_ROOT="$NDK"
    export PANVK_JOBS="${PANVK_JOBS:-$(nproc)}"
    log "Building PanVK (profile g615-v11-csf, API $API, VARIANT=$VARIANT FPS_CAP=$FPS_CAP TUNE=$TUNE)"
    MESA="$MESA" "$ZB/scripts/build-android.sh" --profile g615-v11-csf --api "$API" --ndk "$NDK" \
        || { tail -n 60 "$ZB/build/android-bionic.log" 2>/dev/null || true; die "build-android.sh failed"; }
    SO="$ZB/dist/android-g615-v11-csf/libvulkan_panfrost.so"
    [ -f "$SO" ] || die "libvulkan_panfrost.so not produced"
    grep -aq "xamonxx mali7300: frame pacer" "$SO" || die "frame pacer not linked into the driver"
}

package() {
    mkdir -p "$DIST"
    local mesa_sha title name base
    mesa_sha="$(git -C "$MESA" rev-parse --short=10 HEAD)"
    title="$(echo "${VARIANT:0:1}" | tr a-z A-Z)${VARIANT:1}"
    name="xamonxx mali7300 V${VERSION} ${title}"
    base="xamonxx_mali7300V${VERSION}-${VARIANT}"
    cp "$ROOT/NOTICE.md" "$WORK/NOTICE.txt"

    for layout in panfrost freedreno; do
        local lib zip stage
        lib="libvulkan_${layout}.so"
        zip="$DIST/${base}.zip"
        [ "$layout" = freedreno ] && zip="$DIST/${base}-freedreno.zip"
        stage="$WORK/stage-$layout"
        rm -rf "$stage"; mkdir -p "$stage"
        cp "$SO" "$stage/$lib"
        cp "$WORK/NOTICE.txt" "$stage/NOTICE.txt"
        python3 - "$stage/meta.json" "$name" "$VERSION-$VARIANT" "$mesa_sha" "$FPS_CAP" "$TUNE" "$lib" <<'PY'
import json, sys
out, name, ver, sha, cap, tune, lib = sys.argv[1:]
cap = int(cap)
pacer = f"frame pacer {cap} fps" if cap else "no frame cap"
cpu = "A78/A55 tuned" if tune == "1" else "upstream flags"
meta = {
    "schemaVersion": 1,
    "name": name,
    "description": ("Mesa PanVK on mali_kbase for Mali-G615 MC2 (Infinix Note 50X, Dimensity 7300). "
                    f"zenithblue v26.3.1 series p0175 + xamonxx {pacer}, {cpu}. Mesa {sha}."),
    "author": "xamonxx",
    "packageVersion": ver,
    "vendor": "Mesa",
    "driverVersion": f"Mesa 26.3.0-devel p0175 xamonxx {ver}",
    "minApi": 29,
    "libraryName": lib,
}
open(out, "w", encoding="utf-8").write(json.dumps(meta, indent=2) + "\n")
PY
        rm -f "$zip"
        (cd "$stage" && zip -9 -q -X "$zip" meta.json "$lib" NOTICE.txt)
        unzip -tq "$zip"
        log "Packaged $(basename "$zip")"
    done
}

main() {
    fetch_sources
    prepare_tree
    inject_flags
    build_driver
    package
    python3 -I "$ROOT/tools/audit_mali_driver.py" "$DIST" \
        --expect "xamonxx mali7300: frame pacer" --expect "Mali-G615"
}

main "$@"
