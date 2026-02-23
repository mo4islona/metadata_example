### Endpoints

**GET `/datasets`**  
Returns the list of datasets (current / default behavior).

```json
[
  {
    "dataset": "base-mainnet",
    "kind": "evm",
    "aliases": [
      "base"
    ],
    "real_time": true,
  }
]
```

---

**GET `/datasets?expand[]=metadata`**  
Returns the same list, but additionally includes metadata for each dataset.

```json5
[
  {
    "dataset": "base-mainnet",
    "kind": "evm",
    "aliases": [
      "base"
    ],
    "real_time": true,

    // We can make it at the root level.
    // I don't think it is important.
    "metadata": {  
       "display_name": "Ethereum",
       "logo_url": "https://cdn.subsquid.io/img/networks/ethereum.svg"
       // ...
    }
  }
]
```
---
Ideally
**GET `/datasets/{dataset}?expand[]=metadata&expand[]=schema`**

or we can use the old `/datasets/{dataset}/metadata`, however
`/datasets/{dataset}` is preferrable as it is REST API best practice.

Returns:

- dataset metadata
- dataset schema (i.e., available entities and their block ranges)

---

## Example: Metadata for a custom dataset

```yaml
datasets:
  ethereum-mainnet:
    metadata:
      display_name: Ethereum
      logo_url: https://cdn.subsquid.io/img/networks/ethereum.svg
      type: testnet
      evm:
        chain_id: 1
    schema:
      blocks:
      transactions:
      logs:
      state_diffs:
      traces:
```


[Metadata for the Ethereum mainnet dataset](./example.yaml)

---

## File Size Considerations

With the full EVM schema (5 entities, 102 fields per dataset), a single dataset entry is ~9 KB of YAML. At scale this adds up:

| Datasets | YAML (raw) | JSON minified (raw) | YAML + gzip | YAML + brotli |
|----------|-----------|---------------------|-------------|---------------|
| 200      | 1.7 MB    | 1.0 MB              | 23.5 KB     | 3.0 KB        |
| 500      | 4.4 MB    | 2.4 MB              | 57.3 KB     | 6.4 KB        |
| 1000     | 8.8 MB    | 4.9 MB              | 113.7 KB    | 11.5 KB       |

Because every dataset shares the same schema structure, compression is extremely effective — brotli reduces 1000 datasets from 8.8 MB down to **11.5 KB** (0.12% of original). With `Content-Encoding: br` enabled on the HTTP layer, file size is a non-issue.

Full benchmark details: [benchmark-results.md](./benchmark-results.md)
Reproduce with: `python3 generate_metadata.py 1000 ./out` and `./benchmark.sh`
