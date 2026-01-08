import asyncio
import httpx

# --- 配置区 ---
API_KEY = "269c7d6e-b884-41ca-8f58-***"
TARGET_TOKEN = "a3W4qutoEJA4232T2gwZUfgYJTetr96pU4SJMwppump"
MAX_PAGES = 5  # 扫描页数（每页100笔），增加此值可获取更久的历史


async def analyze_top_profit_wallets_deep(token_mint):
    base_url = f"https://api.helius.xyz/v0/addresses/{token_mint}/transactions?api-key={API_KEY}"
    last_signature = None
    pnl_ledger = {}
    page_count = 0

    async with httpx.AsyncClient() as client:
        print(f"🚀 开始深度扫描 Token: {token_mint}")
        print(f"正在回溯历史交易以计算盈亏...")

        while page_count < MAX_PAGES:
            request_url = base_url
            if last_signature:
                request_url += f"&before={last_signature}"

            try:
                response = await client.get(request_url, timeout=30)
                txs = response.json()

                if not txs or len(txs) == 0:
                    print("🏁 已到达该代币的历史开盘时刻。")
                    break

                for tx in txs:
                    # 获取 SOL 转移和 Token 转移记录
                    native_transfers = tx.get('nativeTransfers', [])
                    token_transfers = tx.get('tokenTransfers', [])

                    # 识别本笔交易涉及的所有钱包
                    involved_wallets = set()
                    for nt in native_transfers:
                        involved_wallets.add(nt['fromUserAccount'])
                        involved_wallets.add(nt['toUserAccount'])

                    for wallet in involved_wallets:
                        if wallet not in pnl_ledger:
                            pnl_ledger[wallet] = {'spent_sol': 0.0, 'received_sol': 0.0}

                        # 统计该钱包的 SOL 支出与收入
                        for nt in native_transfers:
                            if nt['fromUserAccount'] == wallet:
                                pnl_ledger[wallet]['spent_sol'] += nt['amount'] / 1e9
                            if nt['toUserAccount'] == wallet:
                                pnl_ledger[wallet]['received_sol'] += nt['amount'] / 1e9

                # 更新分页签名，准备抓取下一页
                last_signature = txs[-1]['signature']
                page_count += 1
                print(f"已处理第 {page_count} 页 ({len(txs)} 笔交易)...")

            except Exception as e:
                print(f"❌ 请求中断: {e}")
                break

        # --- 计算盈亏并排序 ---
        profit_list = []
        for wallet, data in pnl_ledger.items():
            # 净利润 = 卖出拿回的 SOL - 买入花掉的 SOL
            net_profit = data['received_sol'] - data['spent_sol']

            # 过滤逻辑：
            # 1. 过滤掉利润几乎为0的地址
            # 2. 过滤掉可能是官方池子的地址（流水极大，通常获利表现为负且数值巨大）
            if net_profit > 0.01:
                profit_list.append({
                    'address': wallet,
                    'profit': net_profit,
                    'spent': data['spent_sol'],
                    'received': data['received_sol']
                })

        # 根据净利润(profit)从大到小排序
        top_10_smart_money = sorted(profit_list, key=lambda x: x['profit'], reverse=True)[:10]

        # --- 打印结果 ---
        print("\n" + "🏆 SOL 获利排行榜 (Top 10 Smart Money)")
        print("=" * 90)
        print(f"{'排名':<5} {'钱包地址':<48} {'净利润(SOL)':<15} {'总收入/总支出'}")
        print("-" * 90)

        for i, item in enumerate(top_10_smart_money, 1):
            addr = item['address']
            profit_str = f"{item['profit']:>10.2f}"
            flow_str = f"{item['received']:>7.2f} / {item['spent']:<7.2f}"
            print(f"{i:<5} {addr:<48} {profit_str:<15} {flow_str}")
        print("=" * 90)
        print("💡 提示：高收入/极低支出的地址通常是开发者或早期内部地址。")


if __name__ == "__main__":
    # 替换为你想要分析的真实 Token Mint 地址
    # 比如：Pump.fun 上某个刚下榜的币
    asyncio.run(analyze_top_profit_wallets_deep(TARGET_TOKEN))