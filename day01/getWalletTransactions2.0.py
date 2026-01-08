import httpx
import asyncio


async def get_specific_token_history(wallet_address, token_mint, api_key):
    # 增强型交易接口
    url = f"https://api.helius.xyz/v0/addresses/{wallet_address}/transactions"
    params = {
        "api-key": api_key,
        "limit": 50  # 增加搜索范围，以便过滤出目标币种交易
    }

    print(f"\n🔍 正在检索钱包中关于代币 [{token_mint[:8]}...] 的交易...\n")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=15)
            response.raise_for_status()
            transactions = response.json()

            found_any = False
            for tx in transactions:
                # 过滤逻辑：检查这笔交易的代币转移记录中是否有我们要找的 Mint
                relevant_transfers = [
                    tt for tt in tx.get('tokenTransfers', [])
                    if tt['mint'] == token_mint
                ]

                if relevant_transfers:
                    found_any = True
                    print(f"⏰ 时间: {tx['timestamp']}")
                    print(f"📝 描述: {tx.get('description', '无描述')}")

                    # 打印具体的代币变动数值
                    for tt in relevant_transfers:
                        direction = "收到" if tt['toUserAccount'] == wallet_address else "送出"
                        print(f"📊 动作: {direction} {tt['tokenAmount']} 个代币")

                    print("-" * 40)

            if not found_any:
                print("❌ 在最近的记录中未发现该币种的交易。")

        except Exception as e:
            print(f"❌ 运行出错: {e}")


async def main():
    print("=== Solana 特定币种交易查询工具 ===")
    api_key = input("1. 请输入 Helius API Key: ").strip()
    wallet_address = input("2. 请输入钱包地址: ").strip()
    token_mint = input("3. 请输入币种 Mint 地址 (Token Address): ").strip()

    if not all([api_key, wallet_address, token_mint]):
        print("❌ 所有字段均为必填项！")
        return

    await get_specific_token_history(wallet_address, token_mint, api_key)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass