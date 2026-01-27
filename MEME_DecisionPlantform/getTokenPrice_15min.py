import requests
import pandas as pd
import time
from datetime import datetime


class Crypto15MinFetcher:
    def __init__(self):
        self.headers = {
            "Accept": "application/json;version=20230203",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.base_url = "https://api.geckoterminal.com/api/v2"

    def get_all_history_15min(self, network, token_ca):
        """
        抓取代币从发行至今的所有 15 分钟 K 线
        """
        # 1. 获取流动性最大的主池子
        pool_address = self._get_best_pool(network, token_ca)
        if not pool_address:
            return None

        all_data = []
        # 从当前时间戳开始往回找
        before_timestamp = int(time.time())

        print(f"🚀 开始全量抓取 15 分钟 K 线数据 (池子: {pool_address})...")

        while True:
            # 15分钟线对应：timeframe='minute', aggregate=15
            url = f"{self.base_url}/networks/{network}/pools/{pool_address}/ohlcv/minute"
            params = {
                "aggregate": 15,
                "before_timestamp": before_timestamp,
                "limit": 1000
            }

            try:
                response = requests.get(url, headers=self.headers, params=params)

                if response.status_code == 429:
                    print("⚠️ 频率过快，休息 10 秒...")
                    time.sleep(10)
                    continue

                if response.status_code != 200:
                    print(f"❌ 抓取中断，错误码: {response.status_code}")
                    break

                data = response.json().get('data', {}).get('attributes', {}).get('ohlcv_list', [])

                if not data:
                    print("🏁 已触达代币发行点，抓取完成。")
                    break

                all_data.extend(data)

                # 获取本批次最老的一个时间戳
                oldest_ts = data[-1][0]

                # 如果时间戳没有更新，说明没有更多数据了
                if oldest_ts >= before_timestamp:
                    break

                before_timestamp = oldest_ts
                print(f"📅 已同步至: {datetime.fromtimestamp(oldest_ts).strftime('%Y-%m-%d %H:%M')}")

                # 稍微停顿，防止被封
                time.sleep(1.2)

            except Exception as e:
                print(f"❌ 运行异常: {e}")
                break

        if not all_data:
            return None

        # 2. 转换为 DataFrame
        df = pd.DataFrame(all_data, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        df['time'] = pd.to_datetime(df['time'], unit='s')

        # 排序并去重
        df = df.sort_values('time').drop_duplicates('time').reset_index(drop=True)

        # 转换为北京时间
        df['time'] = df['time'] + pd.Timedelta(hours=8)

        return df

    def _get_best_pool(self, network, token_address):
        """查找主池子地址"""
        url = f"{self.base_url}/networks/{network}/tokens/{token_address}/pools"
        try:
            res = requests.get(url, headers=self.headers)
            if res.status_code == 200:
                data = res.json().get('data', [])
                if data:
                    # 按照 reserve_in_usd (流动性) 排序
                    best_pool = max(data, key=lambda x: float(x['attributes'].get('reserve_in_usd', 0) or 0))
                    return best_pool['attributes']['address']
        except:
            pass
        return None


# --- 使用示例 ---
if __name__ == "__main__":
    fetcher = Crypto15MinFetcher()

    # 以 Solana 链上的某个代币为例
    NETWORK = "solana"
    TOKEN_CA = "61Wj56QgGyyB966T7YsMzEAKRLcMvJpDbPzjkrCZc4Bi"  # 替换为你需要的 CA

    df_15m = fetcher.get_all_history_15min(NETWORK, TOKEN_CA)

    if df_15m is not None:
        print(f"\n📊 抓取结果汇总:")
        print(f"总行数: {len(df_15m)}")
        print(f"最早 K 线: {df_15m['time'].min()}")
        print(f"最晚 K 线: {df_15m['time'].max()}")
        print(df_15m.head())

        # 保存到本地
        df_15m.to_csv(f"history_15min_{TOKEN_CA[:6]}.csv", index=False)