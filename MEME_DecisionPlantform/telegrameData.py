import asyncio
import pandas as pd
from telethon import TelegramClient
from datetime import datetime
import socks  # 必须导入

# 1. 配置你的 API 凭证
api_id = '2040'
api_hash = 'b18441a1ff607e10a989891a5462e627'
proxy = (socks.SOCKS5, '127.0.0.1', 7890)

# 2. 爬取配置
# 可以是群组的用户名 (如 @gmgnsignalsol) 或邀请链接
target_chats = ['@imshards', '@trendisgoodcn']
keywords = ['61Wj56QgGyyB966T7YsMzEAKRLcMvJpDbPzjkrCZc4Bi', 'COPPERINU']
start_date = datetime(2025, 1, 1)  # 代币发行日期


async def scrape_telegram():
    async with TelegramClient('session_name', api_id, api_hash) as client:
        all_messages = []

        for chat in target_chats:
            print(f"正在爬取群组: {chat}...")
            # iter_messages 支持搜索关键词和时间过滤
            async for message in client.iter_messages(chat, search=keywords[0]):
                # 如果消息早于发行日期，停止该群组爬取
                if message.date.replace(tzinfo=None) < start_date:
                    break

                all_messages.append({
                    'time': message.date,
                    'text': message.text,
                    'sender_id': message.sender_id,
                    'views': getattr(message, 'views', 0),
                    'group': chat
                })

        # 保存为 CSV
        df = pd.DataFrame(all_messages)
        # 统一转为北京时间
        df['time'] = df['time'].dt.tz_convert('Asia/Shanghai').dt.tz_localize(None)
        df.to_csv('tg_discussions.csv', index=False)
        print(f"✅ 爬取完成，共获得 {len(df)} 条相关讨论")


if __name__ == '__main__':
    asyncio.run(scrape_telegram())