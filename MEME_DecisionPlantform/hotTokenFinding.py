import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from datetime import datetime, timedelta

# --- 配置区 ---
MONITOR_CHANNELS = ['gmgnsignalsol', 'SOL_Alpha_Calls', 'DexScreener_Trending','Crypto_Flash_News']  # 监控的频道列表
TARGET_THRESHOLD = 3  # 15分钟内讨论超过3次即预警
CHECK_INTERVAL = 10  # 每 5 分钟扫描一次


def extract_ca(text):
    """提取 Solana 合约地址 (Base58 格式)"""
    pattern = r'[1-9A-HJ-NP-Za-km-z]{32,44}'
    cas = re.findall(pattern, text)
    return cas[0] if cas else None


def get_tg_mentions(channel_name):
    """抓取单频道最近的消息并返回列表"""
    url = f"https://t.me/s/{channel_name}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message')

        results = []
        for msg in messages:
            text_div = msg.find('div', class_='tgme_widget_message_text')
            time_tag = msg.find('time', class_='time')
            if text_div and time_tag:
                text = text_div.get_text()
                ca = extract_ca(text)
                if ca:
                    results.append({
                        'ca': ca,
                        'time': pd.to_datetime(time_tag['datetime']).tz_localize(None),
                        'text': text[:50] + "..."
                    })
        return results
    except Exception as e:
        print(f"❌ 抓取 {channel_name} 失败: {e}")
        return []


def start_monitoring():
    print(f"🚀 启动实时热度监测仪... (阈值: {TARGET_THRESHOLD}次/15min)")

    while True:
        all_new_mentions = []
        now = datetime.utcnow()
        time_limit = now - timedelta(minutes=15)

        # 1. 抓取所有频道
        for channel in MONITOR_CHANNELS:
            mentions = get_tg_mentions(channel)
            # 过滤 15 分钟内的消息
            recent_mentions = [m for m in mentions if m['time'] > time_limit]
            all_new_mentions.extend(recent_mentions)
            time.sleep(1)  # 礼貌延时

        if not all_new_mentions:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 暂无新信号...")
        else:
            # 2. 统计每个 CA 出现的次数
            df = pd.DataFrame(all_new_mentions)
            stats = df['ca'].value_counts()

            for ca, count in stats.items():
                if count >= TARGET_THRESHOLD:
                    print("\n" + "!" * 40)
                    print(f"🔥 🔥 【高热度预警】 🔥 🔥")
                    print(f"合约地址: {ca}")
                    print(f"15min讨论次数: {count}")
                    print(f"X 搜索链接: https://twitter.com/search?q={ca}")
                    print(f"GMGN 链接: https://gmgn.ai/sol/token/{ca}")
                    print("!" * 40 + "\n")
                else:
                    print(f"🔍 发现潜在代币 {ca[:6]}... 讨论数: {count} (暂未触发预警)")

        # 3. 等待下一轮轮询
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    start_monitoring()