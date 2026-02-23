#!/usr/bin/env bash
# Benchmark metadata file sizes across different dataset counts and compression algorithms.
# Usage: ./benchmark.sh
# Output: results are printed to stdout as a markdown table.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUT_DIR="$SCRIPT_DIR/out"
COUNTS=(200 500 1000)

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"

# --- Generate files ---
echo "Generating metadata files..."
for n in "${COUNTS[@]}"; do
    python3 "$SCRIPT_DIR/generate_metadata.py" "$n" "$OUT_DIR"
done
echo ""

# --- Compress ---
echo "Compressing..."
for n in "${COUNTS[@]}"; do
    for ext in yaml json min.json; do
        src="$OUT_DIR/metadata_${n}.${ext}"
        [ -f "$src" ] || continue
        gzip  -k -9 "$src"
        brotli -k -9 "$src" 2>/dev/null || true
        zstd  -19 -q -k "$src" -o "${src}.zst" 2>/dev/null || true
    done
done
echo ""

# --- Collect results ---
human_size() {
    local bytes=$1
    if   (( bytes >= 1048576 )); then printf "%.1f MB" "$(echo "scale=1; $bytes / 1048576" | bc)"
    elif (( bytes >= 1024 ));    then printf "%.1f KB" "$(echo "scale=1; $bytes / 1024" | bc)"
    else printf "%d B" "$bytes"
    fi
}

get_size() {
    stat -f%z "$1" 2>/dev/null || stat -c%s "$1" 2>/dev/null
}

echo "=== RAW FILE SIZES ==="
echo ""
echo "| Format | 200 datasets | 500 datasets | 1000 datasets |"
echo "|--------|-------------|--------------|---------------|"

for label_ext in "YAML:yaml" "JSON (pretty):json" "JSON (minified):min.json"; do
    label="${label_ext%%:*}"
    ext="${label_ext##*:}"
    row="| $label"
    for n in "${COUNTS[@]}"; do
        f="$OUT_DIR/metadata_${n}.${ext}"
        if [ -f "$f" ]; then
            sz=$(get_size "$f")
            row+=" | $(human_size "$sz")"
        else
            row+=" | -"
        fi
    done
    echo "$row |"
done

echo ""
echo "=== COMPRESSED FILE SIZES ==="
echo ""
echo "| Format | Compression | 200 datasets | 500 datasets | 1000 datasets |"
echo "|--------|-------------|-------------|--------------|---------------|"

for label_ext in "YAML:yaml" "JSON (pretty):json" "JSON (minified):min.json"; do
    label="${label_ext%%:*}"
    ext="${label_ext##*:}"
    for comp_suffix in "gzip:gz" "brotli:br" "zstd:zst"; do
        comp="${comp_suffix%%:*}"
        suffix="${comp_suffix##*:}"
        row="| $label | $comp"
        for n in "${COUNTS[@]}"; do
            f="$OUT_DIR/metadata_${n}.${ext}.${suffix}"
            if [ -f "$f" ]; then
                sz=$(get_size "$f")
                raw_sz=$(get_size "$OUT_DIR/metadata_${n}.${ext}")
                ratio=$(echo "scale=1; $sz * 100 / $raw_sz" | bc)
                row+=" | $(human_size "$sz") (${ratio}%)"
            else
                row+=" | -"
            fi
        done
        echo "$row |"
    done
done

echo ""
echo "=== COMPRESSION RATIO VS RAW YAML ==="
echo ""
echo "| Format + Compression | 200 datasets | 500 datasets | 1000 datasets |"
echo "|----------------------|-------------|--------------|---------------|"

for label_ext in "YAML:yaml" "JSON (pretty):json" "JSON (minified):min.json"; do
    label="${label_ext%%:*}"
    ext="${label_ext##*:}"
    for comp_suffix in "gzip:gz" "brotli:br" "zstd:zst"; do
        comp="${comp_suffix%%:*}"
        suffix="${comp_suffix##*:}"
        row="| $label + $comp"
        for n in "${COUNTS[@]}"; do
            f="$OUT_DIR/metadata_${n}.${ext}.${suffix}"
            yaml_raw="$OUT_DIR/metadata_${n}.yaml"
            if [ -f "$f" ] && [ -f "$yaml_raw" ]; then
                sz=$(get_size "$f")
                yaml_sz=$(get_size "$yaml_raw")
                ratio=$(echo "scale=2; $sz * 100 / $yaml_sz" | bc)
                row+=" | $(human_size "$sz") (${ratio}%)"
            else
                row+=" | -"
            fi
        done
        echo "$row |"
    done
done

echo ""
echo "=== PER-DATASET COST ==="
echo ""
echo "| Format | Per dataset (raw) | Per dataset (gzip) | Per dataset (brotli) |"
echo "|--------|-------------------|-------------------|---------------------|"

for label_ext in "YAML:yaml" "JSON (pretty):json" "JSON (minified):min.json"; do
    label="${label_ext%%:*}"
    ext="${label_ext##*:}"
    n=1000
    raw=$(get_size "$OUT_DIR/metadata_${n}.${ext}")
    gz=$(get_size "$OUT_DIR/metadata_${n}.${ext}.gz")
    br=$(get_size "$OUT_DIR/metadata_${n}.${ext}.br")
    per_raw=$((raw / n))
    per_gz=$((gz / n))
    per_br=$((br / n))
    echo "| $label | $(human_size $per_raw) | $(human_size $per_gz) | $(human_size $per_br) |"
done
