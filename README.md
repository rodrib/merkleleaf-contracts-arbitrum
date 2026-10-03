# MerkleLeaf ForestRegistry

A verifiable, tamper-proof forest biometric registry, anchored on Arbitrum.

## The problem

Forestry projects (reforestation, carbon credits, sustainable management) rely today on spreadsheets, photos, and reports that anyone can edit after the fact. There's no easy way to prove that a field measurement — a tree's diameter, its location, its condition — wasn't altered retroactively to inflate results.

**MerkleLeaf** solves this by anchoring every field sample on-chain: once recorded, it's immutable and auditable by anyone, forever.

## How it works

The `ForestRegistry` contract (written in [Vyper](https://vyperlang.org/)) stores, for each sampled tree:

- **Location**: latitude/longitude (decimal degrees × 1e6)
- **Biometrics**: diameter at breast height (DAP), trunk height, total height
- **Spectral data**: NDVI index and its source (e.g. Sentinel-2), to integrate satellite remote sensing
- **Verification hash**: a hash of the original field sheet/photo, to audit that the on-chain record matches the physical one
- **Audit metadata**: who logged the sample and when

Only addresses authorized by the owner can log samples (`log_sample`), intended for field operators or remote-sensing oracles. The owner can transfer their role (`transfer_ownership`) so the registry is never orphaned if a key is lost.

## Deployed contract

| Network | Address | Status |
|---|---|---|
| Arbitrum One (mainnet) | [`0xC14d3a7E78aB0E12fbd736F08D4b222BF509c5f2`](https://arbiscan.io/address/0xC14d3a7E78aB0E12fbd736F08D4b222BF509c5f2) | ✅ Source code verified (Exact Match) |

Deployed with 23 real samples from a Quebracho (Schinopsis) plot in the Gran Chaco (Formosa - Argentina), including their coordinates, DAP, trunk height, and total height.

## Tech stack

- **Vyper 0.4.3** — contract language, chosen for security and simplicity over Solidity
- **[Moccasin](https://cyfrin.github.io/moccasin/)** (`mox`) — development and deployment framework
- **[titanoboa](https://github.com/vyperlang/titanoboa)** — Vyper testing/simulation engine
- **Arbitrum One** — Ethereum L2, chosen for its minimal fees (the full deploy + 23 records cost ~$0.44 USD total)

## Local development

```bash
# install dependencies
pip install -r requirements.txt  # or uv sync, depending on your setup

# run the tests (17 tests, covering validation, permissions, and ownership)
python3 -m pytest tests/test_forest_registry.py -v
```

## Deployment

```bash
# testnet (Arbitrum Sepolia)
mox run deploy_forest_registry --network arbitrum-sepolia --account <your-account>

# mainnet (Arbitrum One)
mox run deploy_forest_registry --network arbitrum-one --account <your-account>
```

The script (`script/deploy_forest_registry.py`) deploys the contract and logs the 23 samples from the example plot, with tolerance for RPC resync errors to avoid duplicate records.

## Security and validation

- Only authorized loggers can write (`authorized_loggers`)
- On-chain range validation: NDVI (-1.0 to 1.0), latitude (-90° to 90°), longitude (-180° to 180°), DAP > 0, total height ≥ trunk height
- Transferable ownership, zero-address guarded
- 17 automated tests cover every revert path

## Roadmap

- [ ] Integrate real NDVI data via satellite remote sensing (Sentinel-2) — currently a placeholder at `0`
- [ ] Read-only UI: interactive map of logged samples
- [ ] Write UI: form for authorized operators to log new samples from the browser

## License

MIT