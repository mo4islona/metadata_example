# Metadata File Size Benchmark

Benchmark of EVM metadata file sizes across different dataset counts, formats, and compression algorithms.

Each dataset contains the full EVM schema: **5 entities** (blocks, transactions, logs, traces, statediffs) with **102 fields** total.

## Raw File Sizes

| Format | 200 datasets | 500 datasets | 1000 datasets |
|---|---|---|---|
| YAML | 1.7 MB | 4.4 MB | 8.8 MB |
| JSON (pretty) | 2.9 MB | 7.3 MB | 14.7 MB |
| JSON (minified) | 1.0 MB | 2.4 MB | 4.9 MB |

Raw sizes scale linearly. YAML sits between pretty and minified JSON. JSON pretty-print adds ~67% overhead vs YAML due to braces and quotes. Minified JSON is ~44% smaller than YAML.

## Compressed File Sizes

| Format | Compression | 200 datasets | 500 datasets | 1000 datasets |
|---|---|---|---|---|
| YAML | gzip | 23.5 KB | 57.3 KB | 113.7 KB |
| YAML | brotli | 3.0 KB | 6.4 KB | 11.5 KB |
| YAML | zstd | 4.0 KB | 8.5 KB | 16.3 KB |
| JSON (pretty) | gzip | 35.9 KB | 88.3 KB | 175.5 KB |
| JSON (pretty) | brotli | 3.2 KB | 6.8 KB | 12.3 KB |
| JSON (pretty) | zstd | 4.5 KB | 9.6 KB | 18.3 KB |
| JSON (minified) | gzip | 10.3 KB | 24.4 KB | 47.9 KB |
| JSON (minified) | brotli | 3.0 KB | 6.4 KB | 11.8 KB |
| JSON (minified) | zstd | 3.7 KB | 8.0 KB | 15.1 KB |

## Compression Ratio (vs raw YAML baseline)

| Format + Compression | 200 datasets | 500 datasets | 1000 datasets |
|---|---|---|---|
| YAML + gzip | 1.29% | 1.26% | 1.25% |
| YAML + brotli | 0.17% | 0.14% | 0.12% |
| YAML + zstd | 0.22% | 0.18% | 0.18% |
| JSON (pretty) + gzip | 1.98% | 1.95% | 1.93% |
| JSON (pretty) + brotli | 0.18% | 0.15% | 0.13% |
| JSON (pretty) + zstd | 0.25% | 0.21% | 0.20% |
| JSON (min) + gzip | 0.57% | 0.54% | 0.52% |
| JSON (min) + brotli | 0.17% | 0.14% | 0.13% |
| JSON (min) + zstd | 0.20% | 0.17% | 0.16% |

## Per-Dataset Cost (at 1000 datasets)

| Format | Raw | gzip | brotli |
|---|---|---|---|
| YAML | 9.0 KB | 116 B | 11 B |
| JSON (pretty) | 15.1 KB | 179 B | 12 B |
| JSON (minified) | 5.1 KB | 49 B | 12 B |

## Key Takeaways

1. **Brotli dominates**: all formats compress to ~12 KB at 1000 datasets (~0.13% of raw YAML). The source format is nearly irrelevant once brotli is applied.

2. **gzip still shows format differences**: YAML+gzip (114 KB) is 2.4x smaller than JSON+gzip (176 KB), and minified JSON+gzip (48 KB) beats both. If only gzip is available, minified JSON wins.

3. **Raw format matters without compression**: minified JSON (4.9 MB) is 44% smaller than YAML (8.8 MB) and 67% smaller than pretty JSON (14.7 MB).

4. **Linear scaling**: all formats and compressions scale linearly with dataset count. No surprises at scale.

5. **Marginal cost per dataset with brotli is ~12 bytes** regardless of format. With gzip, YAML costs ~116 B/dataset, minified JSON costs ~49 B/dataset.

6. **Recommendation**: for HTTP APIs serving this data, enable `Content-Encoding: br` (brotli) and the choice of YAML vs JSON becomes purely a developer experience decision, not a performance one.

## Reproduction

```bash
# Generate files for a specific count
python3 generate_metadata.py 1000 ./out

# Run full benchmark (200, 500, 1000)
./benchmark.sh
```
