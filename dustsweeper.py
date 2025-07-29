
---

## 🧠 `dustsweeper/sweep.py`

```python
from web3 import Web3
import requests
from rich import print
from rich.table import Table

ETHERSCAN_API_KEY = "YourApiKeyToken"
ETHERSCAN_API = "https://api.etherscan.io/api"
MIN_USD_THRESHOLD = 1.00  # $1

# Подгружаем токены и их балансы
def get_token_balances(address):
    url = f"{ETHERSCAN_API}?module=account&action=tokenbalance&contractaddress={{contract}}&address={address}&tag=latest&apikey={ETHERSCAN_API_KEY}"
    tokens = [
        {"name": "Shiba Inu", "symbol": "SHIB", "contract": "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE", "decimals": 18},
        {"name": "Chainlink", "symbol": "LINK", "contract": "0x514910771AF9Ca656af840dff83E8264EcF986CA", "decimals": 18},
        # добавьте токены
    ]
    result = []
    for token in tokens:
        try:
            r = requests.get(url.format(contract=token["contract"])).json()
            raw_balance = int(r["result"])
            balance = raw_balance / (10 ** token["decimals"])
            usd_value = get_token_price_usd(token["symbol"]) * balance
            result.append({
                "name": token["name"],
                "symbol": token["symbol"],
                "balance": balance,
                "usd_value": usd_value,
                "status": analyze_dust(usd_value)
            })
        except Exception:
            continue
    return result

def get_token_price_usd(symbol):
    try:
        r = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd")
        return r.json().get(symbol.lower(), {}).get("usd", 0)
    except:
        return 0

def analyze_dust(usd_value):
    if usd_value == 0:
        return "⚫️ Неизвестно/нулевой баланс"
    elif usd_value < 0.01:
        return "🔴 Можно сжечь/неподдерживаемый dust"
    elif usd_value < MIN_USD_THRESHOLD:
        return "🟡 Предлагается игнорировать или обменять в swap"
    else:
        return "🟢 Значимый актив"

def display(tokens):
    table = Table(title="🧹 Dust Sweeper")
    table.add_column("Token", style="cyan")
    table.add_column("Balance", justify="right")
    table.add_column("USD", justify="right")
    table.add_column("Status", style="magenta")
    for t in tokens:
        table.add_row(t["symbol"], f"{t['balance']:.8f}", f"${t['usd_value']:.6f}", t["status"])
    print(table)
