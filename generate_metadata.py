#!/usr/bin/env python3
"""Generate metadata YAML and JSON files with N EVM datasets for benchmarking."""

import json
import sys
import os

CHAINS = [
    "ethereum", "polygon", "arbitrum", "optimism", "base", "avalanche", "bsc",
    "fantom", "gnosis", "celo", "moonbeam", "moonriver", "astar", "aurora",
    "boba", "cronos", "evmos", "harmony", "heco", "kava", "klaytn", "metis",
    "milkomeda", "okx", "scroll", "zksync", "linea", "mantle", "manta",
    "blast", "mode", "fraxtal", "zora", "redstone", "cyber", "degen",
    "ham", "stack", "swan", "xai", "immutable", "beam", "apex", "kinto",
    "sanko", "rari", "proof", "gold", "mint", "lisk",
]

SUFFIXES = [
    "mainnet", "testnet", "sepolia", "goerli", "devnet", "staging",
    "holesky", "fuji", "mumbai", "amoy", "baobab", "alfajores",
    "chiado", "pegasus", "phoenix", "rio", "nova", "one", "era", "alpha",
]


def yaml_field(name, typ, nullable=False):
    line = f"                - name: {name}\n                  type: {typ}"
    if nullable:
        line += "\n                  nullable: true"
    return line


def json_field(name, typ, nullable=False):
    d = {"name": name, "type": typ}
    if nullable:
        d["nullable"] = True
    return d


def block_fields(fmt):
    f = yaml_field if fmt == "yaml" else json_field
    return [
        f("number", "int32"),
        f("hash", "string"),
        f("parent_hash", "string"),
        f("nonce", "string", True),
        f("sha3_uncles", "string", True),
        f("logs_bloom", "string"),
        f("transactions_root", "string"),
        f("state_root", "string"),
        f("receipts_root", "string"),
        f("mix_hash", "string", True),
        f("miner", "string"),
        f("difficulty", "string", True),
        f("total_difficulty", "string", True),
        f("extra_data", "string"),
        f("size", "int32"),
        f("gas_used", "string"),
        f("gas_limit", "string"),
        f("timestamp", "int32"),
        f("base_fee_per_gas", "string", True),
        f("l1_block_number", "int32", True),
        f("blob_gas_used", "string", True),
        f("excess_blob_gas", "string", True),
    ]


def tx_fields(fmt):
    f = yaml_field if fmt == "yaml" else json_field
    return [
        f("block_number", "int32"),
        f("transaction_index", "int32"),
        f("hash", "string"),
        f("from", "string"),
        f("to", "string", True),
        f("gas", "string"),
        f("gas_price", "string", True),
        f("max_fee_per_gas", "string", True),
        f("max_priority_fee_per_gas", "string", True),
        f("input", "string"),
        f("nonce", "int32"),
        f("value", "string"),
        f("v", "string", True),
        f("r", "string", True),
        f("s", "string", True),
        f("y_parity", "int32", True),
        f("chain_id", "int32", True),
        f("max_fee_per_blob_gas", "string", True),
        f("blob_versioned_hashes", "string[]", True),
        f("sighash", "string", True),
        f("gas_used", "string"),
        f("cumulative_gas_used", "string"),
        f("effective_gas_price", "string", True),
        f("type", "int32", True),
        f("status", "int32"),
        f("contract_address", "string", True),
        f("l1_fee", "string", True),
        f("l1_fee_scalar", "string", True),
        f("l1_gas_price", "string", True),
        f("l1_gas_used", "string", True),
        f("l1_blob_base_fee", "string", True),
        f("l1_blob_base_fee_scalar", "int32", True),
        f("l1_base_fee_scalar", "int32", True),
    ]


def log_fields(fmt):
    f = yaml_field if fmt == "yaml" else json_field
    return [
        f("block_number", "int32"),
        f("log_index", "int32"),
        f("transaction_index", "int32"),
        f("transaction_hash", "string"),
        f("address", "string"),
        f("data", "string"),
        f("topics", "string[]"),
        f("topic0", "string", True),
        f("topic1", "string", True),
        f("topic2", "string", True),
        f("topic3", "string", True),
    ]


def trace_fields(fmt):
    f = yaml_field if fmt == "yaml" else json_field
    return [
        f("block_number", "int32"),
        f("transaction_index", "int32"),
        f("trace_address", "int32[]"),
        f("subtraces", "int32"),
        f("type", "string"),
        f("error", "string", True),
        f("revert_reason", "string", True),
        f("create_from", "string", True),
        f("create_value", "string", True),
        f("create_gas", "string", True),
        f("create_init", "string", True),
        f("create_result_gas_used", "string", True),
        f("create_result_code", "string", True),
        f("create_result_address", "string", True),
        f("call_from", "string", True),
        f("call_to", "string", True),
        f("call_value", "string", True),
        f("call_gas", "string", True),
        f("call_sighash", "string", True),
        f("call_input", "string", True),
        f("call_type", "string", True),
        f("call_result_gas_used", "string", True),
        f("call_result_output", "string", True),
        f("suicide_address", "string", True),
        f("suicide_refund_address", "string", True),
        f("suicide_balance", "string", True),
        f("reward_author", "string", True),
        f("reward_value", "string", True),
        f("reward_type", "string", True),
    ]


def statediff_fields(fmt):
    f = yaml_field if fmt == "yaml" else json_field
    return [
        f("block_number", "int32"),
        f("transaction_index", "int32"),
        f("address", "string"),
        f("key", "string"),
        f("kind", "string"),
        f("prev", "string", True),
        f("next", "string", True),
    ]


def generate_names(count):
    names = []
    for chain in CHAINS:
        for suffix in SUFFIXES:
            names.append(f"{chain}-{suffix}")
            if len(names) >= count:
                return names
    i = 0
    while len(names) < count:
        names.append(f"{CHAINS[i % len(CHAINS)]}-l2-{i}")
        i += 1
    return names[:count]


def generate_yaml(count, output_path):
    names = generate_names(count)
    lines = ["datasets:"]
    for i, name in enumerate(names):
        chain_base = name.split("-")[0]
        net_type = "mainnet" if "mainnet" in name else "testnet"
        display = name.replace("-", " ").title()
        lines.append(f"""  {name}:
    kind: evm
    metadata:
      display_name: {display}
      logo_url: https://cdn.subsquid.io/img/networks/{chain_base}.svg
      type: {net_type}
      evm:
        chain_id: {i + 1}
    schema:
      - range:
          from: 0
          entities:
            blocks:
              fields:
{chr(10).join(block_fields("yaml"))}
            transactions:
              fields:
{chr(10).join(tx_fields("yaml"))}
            logs:
              fields:
{chr(10).join(log_fields("yaml"))}
            traces:
              fields:
{chr(10).join(trace_fields("yaml"))}
            statediffs:
              fields:
{chr(10).join(statediff_fields("yaml"))}""")

    with open(output_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"  YAML: {output_path} ({count} datasets)")


def generate_json(count, output_path, minified_path):
    names = generate_names(count)
    datasets = {}
    for i, name in enumerate(names):
        chain_base = name.split("-")[0]
        net_type = "mainnet" if "mainnet" in name else "testnet"
        datasets[name] = {
            "kind": "evm",
            "metadata": {
                "display_name": name.replace("-", " ").title(),
                "logo_url": f"https://cdn.subsquid.io/img/networks/{chain_base}.svg",
                "type": net_type,
                "evm": {"chain_id": i + 1},
            },
            "schema": [{
                "range": {
                    "from": 0,
                    "entities": {
                        "blocks": {"fields": block_fields("json")},
                        "transactions": {"fields": tx_fields("json")},
                        "logs": {"fields": log_fields("json")},
                        "traces": {"fields": trace_fields("json")},
                        "statediffs": {"fields": statediff_fields("json")},
                    },
                }
            }],
        }

    root = {"datasets": datasets}
    with open(output_path, "w") as f:
        json.dump(root, f, indent=2)
    with open(minified_path, "w") as f:
        json.dump(root, f, separators=(",", ":"))
    print(f"  JSON: {output_path} + {minified_path} ({count} datasets)")


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <count> [output_dir]")
        print(f"  count      - number of datasets to generate (e.g. 200, 500, 1000)")
        print(f"  output_dir - output directory (default: ./out)")
        sys.exit(1)

    count = int(sys.argv[1])
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./out"
    os.makedirs(output_dir, exist_ok=True)

    print(f"Generating {count} datasets in {output_dir}/")
    generate_yaml(count, os.path.join(output_dir, f"metadata_{count}.yaml"))
    generate_json(
        count,
        os.path.join(output_dir, f"metadata_{count}.json"),
        os.path.join(output_dir, f"metadata_{count}.min.json"),
    )
    print("Done.")


if __name__ == "__main__":
    main()
