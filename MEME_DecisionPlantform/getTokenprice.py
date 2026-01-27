import requests
import pandas as pd
import time


class CryptoDataFetcher:
    def __init__(self):
        # 2026年 GeckoTerminal API 的标准请求头
        self.headers = {
            "Accept": "application/json;version=20230203",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.base_url = "https://api.geckoterminal.com/api/v2"

    def get_best_pool(self, network, token_address):
        """步骤 1: 查找代币流动性最大的池子"""
        url = f"{self.base_url}/networks/{network}/tokens/{token_address}/pools"

        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 429:
                print("⚠️ 请求过快，正在触发频率限制，请等待一分钟...")
                return None

            data = response.json().get('data', [])
            if not data:
                print(f"❌ 未找到该代币的池子，请确认 CA: {token_address}")
                return None

            # 按流动性（reserve_in_usd）排序
            best_pool = max(data, key=lambda x: float(x['attributes'].get('reserve_in_usd', 0) or 0))
            attr = best_pool['attributes']

            print(f"✅ 找到主池: {attr['name']}")
            print(
                f"   流动性: ${float(attr['reserve_in_usd']):,.2f} | 24h交易量: ${float(attr['volume_usd']['h24']):,.2f}")

            return best_pool['attributes']['address']

        except Exception as e:
            print(f"❌ 查找池子出错: {e}")
            return None

    def get_ohlcv(self, network, pool_address, timeframe='minute', aggregate=1):
        """步骤 2: 抓取指定池子的 OHLCV 数据"""
        url = f"{self.base_url}/networks/{network}/pools/{pool_address}/ohlcv/{timeframe}"
        params = {"aggregate": aggregate, "limit": 100}

        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code != 200:
                print(f"❌ 抓取 K 线失败: {response.status_code}")
                return None

            ohlcv_data = response.json()['data']['attributes']['ohlcv_list']
            df = pd.DataFrame(ohlcv_data, columns=['time', 'open', 'high', 'low', 'close', 'volume'])

            # 转换时间戳为北京时间 (UTC+8)
            df['time'] = pd.to_datetime(df['time'], unit='s') + pd.Timedelta(hours=8)
            return df

        except Exception as e:
            print(f"❌ 解析数据出错: {e}")
            return None


# --- 使用示例 ---
if __name__ == "__main__":
    fetcher = CryptoDataFetcher()

    # 以 Solana 链上的某个代币为例 (请替换为你感兴趣的 CA)
    # 示例 CA: JUP (Solana)
    NETWORK = "solana"
    TOKEN_CA = "61Wj56QgGyyB966T7YsMzEAKRLcMvJpDbPzjkrCZc4Bi"

    print(f"🔍 正在分析代币: {TOKEN_CA}...")

    # 1. 自动定位主池子
    main_pool_addr = fetcher.get_best_pool(NETWORK, TOKEN_CA)

    if main_pool_addr:
        # 2. 抓取 1 分钟级 K 线
        df = fetcher.get_ohlcv(NETWORK, main_pool_addr, timeframe='minute', aggregate=1)

        if df is not None:
            print("\n📊 最近 5 条 K 线数据 (北京时间):")
            print(df.head())