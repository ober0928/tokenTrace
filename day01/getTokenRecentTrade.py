import asyncio
import httpx

# --- 配置区 ---
API_KEY = "269c7d6e-b884-41ca-8f58-***"
# 这是一个示例 Token (比如某个近期热门的币)
TOKEN_MINT_ADDRESS = "a3W4qutoEJA4232T2gwZUfgYJTetr96pU4SJMwppump"  # 这里是 USDC 的地址，你可以换成别的


async def get_token_profit_rank(token_mint):
    # Helius 的解析交易 API 地址
    url = f"https://api.helius.xyz/v0/addresses/{token_mint}/transactions?api-key={API_KEY}"

    print(f"正在从链上获取 {token_mint} 的交易数据...")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30)
            transactions = response.json()

            if not transactions:
                print("未获取到交易记录，请检查 Mint 地址或 API Key。")
                return

            wallet_stats = {}

            for tx in transactions:
                # 遍历每笔交易的代币转移记录
                for transfer in tx.get('tokenTransfers', []):
                    # 如果该笔转账涉及我们关注的 Token
                    if transfer['mint'] == token_mint:
                        wallet = transfer['toUserAccount']
                        amount = float(transfer['tokenAmount'])

                        # 初始化钱包统计
                        if wallet not in wallet_stats:
                            wallet_stats[wallet] = {'buy_volume': 0, 'tx_count': 0}

                        wallet_stats[wallet]['buy_volume'] += amount
                        wallet_stats[wallet]['tx_count'] += 1

            # 按买入量排序 (简单演示，进阶需结合买入/卖出差值)
            top_wallets = sorted(
                wallet_stats.items(),
                key=lambda x: x[1]['buy_volume'],
                reverse=True
            )[:10]

            print("\n--- 该 Token 买入量最大的前 10 名钱包 ---")
            for i, (addr, data) in enumerate(top_wallets, 1):
                print(f"{i}. 地址: {addr[:10]}... | 总买入量: {data['buy_volume']:,.2f} | 交易次数: {data['tx_count']}")

        except Exception as e:
            print(f"运行出错: {e}")


if __name__ == "__main__":
    # 运行异步函数
    asyncio.run(get_token_profit_rank(TOKEN_MINT_ADDRESS))