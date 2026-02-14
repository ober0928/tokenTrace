import asyncio
import socks
import pandas as pd
from telethon import TelegramClient
from datetime import datetime, timezone

# --- 1. 核心配置 ---
API_ID = 2040  # 替换为你的数字 ID
API_HASH = 'b18441a1ff607e10a989891a5462e627'  # 替换为你的字符串 Hash
# V2Ray 默认 SOCKS5 端口通常是 10808
PROXY = (socks.SOCKS5, '127.0.0.1', 7890)

# 爬取目标
target_chats = ['@imshards', '@trendisgoodcn']
keywords = ['61Wj56QgGyyB966T7YsMzEAKRLcMvJpDbPzjkrCZc4Bi', 'COPPERINU'] # 代币合约地址
START_DATE = datetime(2025, 1, 1, tzinfo=timezone.utc)  # 开始回溯的日期


async def scrape_telegram():
    """
    接入代理并全量爬取历史消息
    """
    # 接入 proxy 参数
    client = TelegramClient('session_meme_platform', API_ID, API_HASH, proxy=PROXY)

    async with client:
        print("✅ 代理连接成功，正在登录/检查会话...")

        all_messages = []

        for chat in TARGET_CHATS:
            print(f"🔍 正在爬取群组: {chat} ...")

            # 使用 iter_messages 进行全量搜索
            async for message in client.iter_messages(chat, search=KEYWORDS[0]):
                # 检查时间，如果消息早于代币发行时间则停止
                msg_date = message.date
                if msg_date < START_DATE:
                    break

                if message.text:
                    all_messages.append({
                        'time': msg_date,
                        'text': message.text,
                        'group': chat
                    })

            print(f"📊 从 {chat} 中获取了 {len(all_messages)} 条相关讨论")

        # 转换为 DataFrame 并处理时区
        if all_messages:
            df_tg = pd.DataFrame(all_messages)
            # 转换为北京时间 (UTC+8) 并移除时区信息以便保存 CSV
            df_tg['time'] = df_tg['time'].dt.with_timezone(timezone.utc).dt.tz_convert('Asia/Shanghai').dt.tz_localize(
                None)
            df_tg.to_csv('tg_discussions.csv', index=False)
            print("💾 讨论信息已保存至 tg_discussions.csv")
            return df_tg
        else:
            print("❌ 未搜索到相关讨论。")
            return None


def merge_with_price():
    """
    将爬到的讨论数据与之前抓取的 15min 价格数据对齐
    """
    try:
        # 加载数据
        df_price = pd.read_csv('token_price_15min.csv', parse_dates=['time'])
        df_tg = pd.read_csv('tg_discussions.csv', parse_dates=['time'])

        # 规整讨论时间到 15 分钟窗口
        df_tg['time_bin'] = df_tg['time'].dt.floor('15T')

        # 计算热度 (每个窗口的消息数)
        sentiment_counts = df_tg.groupby('time_bin').size().reset_index(name='mentions')

        # 合并
        final_df = pd.merge(df_price, sentiment_counts, left_on='time', right_on='time_bin', how='left')
        final_df['mentions'] = final_df['mentions'].fillna(0)

        final_df.to_csv('final_merged_data.csv', index=False)
        print("🔥 数据对齐完成！已生成 final_merged_data.csv")

    except FileNotFoundError:
        print("⚠️ 缺少必要文件，请确保价格数据和爬虫数据都已生成。")


async def main():
    # 1. 先执行爬虫逻辑
    await scrape_telegram()

    # 2. 爬虫结束后，执行数据对齐逻辑（对齐是同步操作，直接调即可）
    merge_with_price()


if __name__ == '__main__':
    # 使用 asyncio.run 替代 get_event_loop
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # 捕获手动停止 (Ctrl+C)
        pass