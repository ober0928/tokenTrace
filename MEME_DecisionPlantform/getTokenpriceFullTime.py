import requests
import pandas as pd
import time
from datetime import datetime


class CryptoFullHistoryFetcher:
    def __init__(self):
        self.headers = {
            "Accept": "application/json;version=20230203",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.base_url = "https://api.geckoterminal.com/api/v2"

    def get_all_ohlcv(self, network, token_ca, timeframe='day', aggregate=1):
        """
        获取代币从上线至今的所有历史数据
        timeframe 可选: 'minute', 'hour', 'day'
        """
        # 1. 先找到主池子地址
        pool_address = self._get_best_pool(network, token_ca)
        if not pool_address:
            return None

        all_data = []
        # 使用当前时间戳作为初始回溯点
        before_timestamp = int(time.time())

        print(f"🚀 开始抓取全量数据 ({timeframe})...")

        while True:
            url = f"{self.base_url}/networks/{network}/pools/{pool_address}/ohlcv/{timeframe}"
            params = {
                "aggregate": aggregate,
                "before_timestamp": before_timestamp,
                "limit": 1000  # 每次拉取最大值
            }

            try:
                response = requests.get(url, headers=self.headers, params=params)

                # 频率限制处理 (Rate Limit)
                if response.status_code == 429:
                    print("⚠️ 触发频率限制，冷却 10 秒...")
                    time.sleep(10)
                    continue

                if response.status_code != 200:
                    print(f"❌ 抓取中断，状态码: {response.status_code}")
                    break

                data = response.json().get('data', {}).get('attributes', {}).get('ohlcv_list', [])

                if not data:
                    print("🏁 已到达数据源头，抓取完成。")
                    break

                all_data.extend(data)

                # 获取这批数据中最老的一根 K 线的时间戳
                # data 格式通常是 [timestamp, open, high, low, close, volume]
                oldest_ts = data[-1][0]

                # 更新 before_timestamp 准备下一次循环
                if oldest_ts < before_timestamp:
                    before_timestamp = oldest_ts
                    print(f"📅 已抓取至: {datetime.fromtimestamp(oldest_ts).strftime('%Y-%m-%d %H:%M')}")
                else:
                    # 避免死循环
                    break

                # 适当延时，保护 API
                time.sleep(1.5)

            except Exception as e:
                print(f"❌ 运行异常: {e}")
                break

        # 转换为 DataFrame
        if not all_data:
            return None

        df = pd.DataFrame(all_data, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        df['time'] = pd.to_datetime(df['time'], unit='s')

        # 去重并按时间排序
        df = df.drop_duplicates(subset=['time']).sort_values('time').reset_index(drop=True)
        return df

    def _get_best_pool(self, network, token_address):
        """私有方法：查找流动性最大的池子"""
        url = f"{self.base_url}/networks/{network}/tokens/{token_address}/pools"
        res = requests.get(url, headers=self.headers)
        if res.status_code == 200:
            data = res.json().get('data', [])
            if data:
                # 按流动性排序取第一
                best_pool = max(data, key=lambda x: float(x['attributes'].get('reserve_in_usd', 0) or 0))
                return best_pool['attributes']['address']
        return None


# --- 运行示例 ---
if __name__ == "__main__":
    fetcher = CryptoFullHistoryFetcher()

    # 示例：抓取 Solana 上的某个代币 (例如 JUP)
    # 如果要看“发行至今”，建议 timeframe 用 'hour' 或 'day'，否则数据量极大
    df_full = fetcher.get_all_ohlcv("solana", "61Wj56QgGyyB966T7YsMzEAKRLcMvJpDbPzjkrCZc4Bi", timeframe='hour')

    if df_full is not None:
        print(f"\n✅ 抓取成功！总计 {len(df_full)} 行数据。")
        print(f"📅 起始时间: {df_full['time'].min()}")
        print(f"📅 结束时间: {df_full['time'].max()}")
        print(df_full.head())

        # 保存到本地 CSV
        df_full.to_csv("token_full_history.csv", index=False)