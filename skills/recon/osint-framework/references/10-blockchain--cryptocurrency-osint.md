# 10. Blockchain & Cryptocurrency OSINT

```python
BLOCKCHAIN_OSINT = {
    # BTC explorers
    'blockchain.com': 'Most popular, address/tx visualization',
    'blockchair': 'Multi-blockchain, address clustering hints',
    'oxt.me': 'Advanced BTC analysis, privacy metrics',
    'walletexplorer': 'Wallet clustering (algorithmic grouping)',
    'crystalblockchain': 'Visual transaction graph (paid)',
    
    # ETH/ EVM explorers
    'etherscan': 'ETH main explorer — contract code, events, tokens',
    'ethplorer': 'Token-focused ETH explorer',
    'debank': 'DeFi portfolio tracker — see all wallets',
    'zapper': 'Multi-chain DeFi dashboard',
    
    # Multi-chain
    'blockscan': 'Multi-chain by Etherscan team',
    'breadcrumbs': 'Transaction tracing and risk scoring (paid)',
    'chainalysis': 'Enterprise blockchain intelligence',
    'elliptic': 'Crypto compliance and forensics',
    
    # Entity attribution
    'arkham': 'Blockchain deanonymization (paid, powerful)',
    'nansen': 'Smart money tracking, wallet labeling (paid)',
}

# Quick Blockchain Recon
def blockchain_recon(address: str):
    """Gather intelligence from a blockchain address."""
    import requests
    
    results = {}
    
    # Check multiple explorers
    for chain, api in [
        ('ETH', f'https://api.etherscan.io/api?module=account&action=txlist&address={address}'),
        ('BTC', f'https://blockchain.info/rawaddr/{address}'),
    ]:
        try:
            r = requests.get(api)
            results[chain] = r.json()
        except:
            pass
    
    return results

# NFT OSINT
NFT_OSINT = {
    'opensea_activity': 'Track NFT purchases, transfers, holdings',
    'nftgo': 'NFT portfolio analytics',
    'icy_tools': 'NFT market intelligence',
    'context': 'NFT social graph and feed',
}

# Crypto AML red flags
CRYPTO_RED_FLAGS = [
    'Transactions involving OFAC-sanctioned addresses',
    'Deposits from darknet market wallets',
    'Mixing/tumbling service interactions',
    'Chain-hopping (ETH → BTC → XMR) — privacy coin conversion',
    'Peel chains — splitting large amounts into small tx',
    'Use of non-KYC exchanges (Bisq, HodlHodl)',
    'Flash loan attacks — borrowed funds → exploit → repay',
    'Dust attacks — small amounts sent to deanonymize wallets',
]
```

---
