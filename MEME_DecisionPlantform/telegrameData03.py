import requests
from bs4 import BeautifulSoup
import pandas as pd
import time


def scrape_tg_no_api(channel_name, pages=5):
    base_url = f"https://t.me/s/{channel_name}"
    all_data = []
    current_url = base_url

    # 模拟真实浏览器，防止被拦截
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }

    print(f"🚀 正在连接频道预览页: {channel_name}...")

    for i in range(pages):
        try:
            response = requests.get(current_url, headers=headers, timeout=15)
            if response.status_code != 200:
                print(f"⚠️ 无法访问页面，状态码: {response.status_code}")
                break

            soup = BeautifulSoup(response.text, 'html.parser')

            # 这里的选择器是关键：Telegram 网页版的消息容器
            messages = soup.find_all('div', class_='tgme_widget_message')

            if not messages:
                print(f"📭 第 {i + 1} 页未发现有效消息。可能到达了尽头或被拦截。")
                # 打印一部分 HTML 看看是不是出了验证码 (手动检查用)
                # print(response.text[:500])
                break

            for msg in messages:
                # 提取文本
                text_div = msg.find('div', class_='tgme_widget_message_text')
                text = text_div.get_text(separator=" ", strip=True) if text_div else None

                # 提取时间 (重点检查这里)
                time_tag = msg.find('time', class_='time')
                if time_tag and 'datetime' in time_tag.attrs:
                    dt_str = time_tag['datetime']
                    dt = pd.to_datetime(dt_str).tz_convert('Asia/Shanghai').tz_localize(None)
                else:
                    continue

                if text:
                    all_data.append({'time': dt, 'text': text})

            # 寻找“显示更早消息”的链接
            more_btn = soup.find('a', class_='tme_messages_more', href=True)
            if more_btn and "/s/" in more_btn['href']:
                current_url = "https://t.me" + more_btn['href']
                print(f"📅 成功抓取一批消息，正在回溯... (当前数据量: {len(all_data)})")
                time.sleep(2)  # 稍微增加延时，模拟人类操作
            else:
                break

        except Exception as e:
            print(f"❌ 循环抓取时发生错误: {e}")
            break

    # --- 修复 KeyError 的核心逻辑 ---
    if not all_data:
        print("🛑 最终未抓取到任何数据，请检查频道 ID 是否正确，或在浏览器中尝试访问该链接。")
        return None

    df = pd.DataFrame(all_data)

    # 确保列确实存在
    if 'time' in df.columns:
        df = df.drop_duplicates().sort_values('time').reset_index(drop=True)
        df.to_csv('tg_discussions_no_api.csv', index=False)
        print(f"✅ 抓取完成！保存了 {len(df)} 条讨论。")
        return df
    else:
        print("❌ 数据结构异常：找不到 'time' 列。")
        return None


if __name__ == "__main__":
    # 尝试抓取 imshards
    scrape_tg_no_api('imshards', pages=5)