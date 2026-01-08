import httpx
import asyncio


async def get_trading_activity(wallet_address, api_key):
    url = f"https://api.helius.xyz/v0/addresses/{wallet_address}/transactions"
    params = {
        "api-key": api_key,
        "limit": 50  # 检索最近的50笔记录
    }

    # 定义我们想要的交易类型（排除简单的 TRANSFER）
    TRADING_TYPES = ["SWAP", "MINT", "BURN", "NFT_SALE", "LIQUIDITY_POOL_DEPOSIT", "LIQUIDITY_POOL_WITHDRAW"]

    print(f"\n📊 正在查询钱包 {wallet_address[:8]}... 的【非转账】交易活动...\n")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=15)
            response.raise_for_status()
            transactions = response.json()

            found_any = False
            for tx in transactions:
                # 核心过滤：只看交易类型属于 TRADING_TYPES 的记录
                # 或者检查 description 中是否包含关键词 "swapped"
                if tx['type'] in TRADING_TYPES or "swapped" in tx.get('description', '').lower():
                    found_any = True
                    print(f"⏰ 时间: {tx['timestamp']}")
                    print(f"🏷️ 类型: {tx['type']}")
                    print(f"📝 描述: {tx.get('description', '无详细描述')}")

                    # 展示涉及的所有币种变动
                    token_moves = tx.get('tokenTransfers', [])
                    if token_moves:
                        print("💎 涉及代币变动:")
                        for tm in token_moves:
                            # 确定是流入还是流出
                            flow = "📥 收到" if tm['toUserAccount'] == wallet_address else "📤 送出"
                            print(f"   {flow} {tm['tokenAmount']} (Mint: {tm['mint'][:8]}...)")

                    print("-" * 50)

            if not found_any:
                print("ℹ️ 最近 50 笔交易中未发现复杂的交易记录（均为普通转账或系统操作）。")

        except Exception as e:
            print(f"❌ 运行出错: {e}")


async def main():
    print("=== Solana 钱包【币种交易】分析工具 ===")
    api_key = input("1. 请输入 Helius API Key: ").strip()
    wallet_address = input("2. 请输入钱包地址: ").strip()

    if not api_key or not wallet_address:
        print("❌ API Key 和钱包地址不能为空！")
        return

    await get_trading_activity(wallet_address, api_key)


if __name__ == "__main__":
    asyncio.run(main())