import asyncio
import httpx

# --- 配置区 ---
API_KEY = "269c7d6e-b884-41ca-8f58-***"
# 举例：这是一个最近比较活跃的代币地址 (请去 DexScreener 找一个最新的替换它)
TARGET_TOKEN = "a3W4qutoEJA4232T2gwZUfgYJTetr96pU4SJMwppump"


async def get_rich_list(token_mint):
    url = f"https://api.helius.xyz/v0/addresses/{token_mint}/transactions?api-key={API_KEY}"

    async with httpx.AsyncClient() as client:
        print(f"正在深度扫描代币交易: {token_mint}...")
        try:
            response = await client.get(url, timeout=30)
            txs = response.json()

            if not txs:
                print("未找到交易数据，请检查 API Key 或地址。")
                return

            # 盈亏分析字典
            ledger = {}  # {钱包地址: {'buy_sol': 0, 'buy_token': 0}}

            for tx in txs:
                # 仅处理包含 Token 转移的交易
                token_transfers = tx.get('tokenTransfers', [])
                native_transfers = tx.get('nativeTransfers', [])

                # 寻找买入行为：谁收到了目标 Token，且谁付出了 SOL
                for tt in token_transfers:
                    if tt['mint'] == token_mint:
                        buyer = tt['toUserAccount']
                        amount_token = float(tt['tokenAmount'])

                        if buyer not in ledger:
                            ledger[buyer] = {'buy_sol': 0, 'buy_token': 0}

                        ledger[buyer]['buy_token'] += amount_token

                        # 尝试寻找该笔交易中对应的 SOL 支出
                        for nt in native_transfers:
                            if nt['fromUserAccount'] == buyer:
                                ledger[buyer]['buy_sol'] += nt['amount'] / 1e9

            # 过滤掉数据不全的地址，按买入 Token 数量排序
            sorted_rich = sorted(
                [k for k, v in ledger.items() if v['buy_token'] > 0],
                key=lambda x: ledger[x]['buy_token'],
                reverse=True
            )[:10]

            print("\n" + "=" * 60)
            print(f"{'排名':<4} {'钱包缩略地址':<15} {'买入Token总量':<15} {'预估成本(SOL)':<10}")
            for i, addr in enumerate(sorted_rich, 1):
                data = ledger[addr]
                print(f"{i:<4} {addr[:12]}... {data['buy_token']:>15,.2f} {data['buy_sol']:>10.2f}")
            print("=" * 60)

        except Exception as e:
            print(f"解析失败: {e}")


if __name__ == "__main__":
    asyncio.run(get_rich_list(TARGET_TOKEN))