# tokenTrace
    
# 开发目标：
利用Python作为技术栈，制作一个token追踪平台。
分析token的走势，并解析该token获利较大的钱包地址。
对获利较大钱包地址进行追踪，分析其交易行为，嗅探下一个可能爆发的token
（变更）
一边做一边学习

#day01
开宗明义

技术路线：

    交互库: 
solana-py (基础交互), solders (高性能数据序列化), anchorpy (处理 Anchor 框架合约)。

    实时数据源:
RPC 节点: 自建或使用 Helius, QuickNode, Alchemy (推荐 Helius，对代币解析支持最好)。
WebSocket: 用于订阅 logsSubscribe 或 accountSubscribe 捕获实时交易。

    数据库:
TimeScaleDB (基于 PostgreSQL): 存储 Token 价格走势（K线数据）。
ClickHouse: 存储海量交易流水，用于离线分析钱包获利。

分析库: Pandas, NumPy (计算 PnL, Win Rate), Scikit-learn (交易行为聚类)。

    核心功能模块设计
1. Token 走势分析
在 Solana 上，代币价格通常由 Raydium 或 Pump.fun 的流动性池决定。
实现方法: 通过 RPC 订阅 programSubscribe 监听 Raydium 的 AMM 路由。
逻辑: 监控 SOL 与目标 Token 的账户余额变化，利用 $x \times y = k$ 公式反向计算实时价格。
2. 获利钱包（Smart Money）挖掘
步骤:
1）获取大户列表: 使用 getTokenLargestAccounts 获取持仓前 20 的地址。
2）溯源分析: 追踪这些地址的买入成本。
通过 getSignaturesForAddress 抓取该地址所有与该 Token 相关的交易，计算 (卖出总额 + 当前持仓价值) - 买入总额。
3）多指标筛选: 过滤掉项目方地址、做市商地址（根据交易频次和关联账户判断），筛选出高胜率、高盈亏比的散户地址。
3. 钱包行为嗅探与预警
新币监听: 当多个“聪明钱”地址在极短时间内（例如 1 分钟内）同时买入某一个新创建的 Token 地址（Mint Address）时，触发高强度预警。
仓位变动: 监控其 SOL 余额波动及代币授权（Approve）行为。

今日开发目标：通过 API 获取特定 Token 的获利最高钱包列表
存在问题：调用api只能返回前100条交易信息，虽然可以通过回溯（程序3.0）查找更多交易信息。
但是某一Token交易量过大，很难从始到终发掘盈利最大的钱包地址。为此更改开发线路

# 开发目标变更；
利用GMGN找到某个热门Token的最大获利钱包（可以由始到终查找并实时更新）
将钱包地址存入数据库，可以保存钱包地址，同时查询钱包的交易情况（包括目前持有代币、最近盈亏情况）整个界面由web展示
数据库会保存上一次查询的信息，有一个刷新按钮。点击后可以更新信息，数据库内容同步更新。

模块 A：Token 深度分析器
逻辑：当用户输入 Token 地址，后端首先检查数据库。
新币：启动异步任务，从 Helius 抓取 50-100 页数据，计算 PnL 排行并存入数据库。
旧币：直接读取数据库，并同时在后台发起一个增量抓取请求

模块 B：钱包详情透视
逻辑：点击某个钱包地址后，前端发起请求。
数据聚合：
调用 getAssetsByOwner 获取其目前持有的所有代币。
调用分析逻辑，展示其在当前 Token 上的买入点位图（如果在前端引入 Chart.js）。

模块 C：同步与刷新机制
逻辑：
点击“刷新”按钮。
前端发送当前显示的最新 Signature 给后端。
后端请求 Helius，加入 until 参数（只抓取该 Signature 之后的交易）。
计算新的 PnL，更新数据库。
前端局部刷新表格数据，高亮显示利润变动的行。

数据库表结构设计；
A. wallets (钱包主表)
``
CREATE TABLE wallets (
    address VARCHAR(44) PRIMARY KEY,       -- Solana 钱包地址 (Ed25519)
    label VARCHAR(50),                     -- 标签：如 "Dev", "Smart Money", "Sniper"
    last_updated TIMESTAMP DEFAULT NOW(),  -- 最后一次更新的时间
    tags TEXT[]                            -- 预留标签数组
);
``
B. tokens (代币信息表)
``
CREATE TABLE tokens (
    mint_address VARCHAR(44) PRIMARY KEY,  -- 代币的 Mint 地址
    symbol VARCHAR(20),                    -- 代币符号
    decimals INT DEFAULT 6,                -- 精度（Solana 常用 6 或 9）
    created_at TIMESTAMP                   -- 该代币在链上创建的时间
);
``
C. token_pnl_stats (盈亏统计表 - 核心)
``
CREATE TABLE token_pnl_stats (
    wallet_address VARCHAR(44) REFERENCES wallets(address),
    token_mint VARCHAR(44) REFERENCES tokens(mint_address),
    
    -- 核心统计指标
    total_bought_sol DECIMAL(20, 9) DEFAULT 0,  -- 累计花费的 SOL
    total_sold_sol DECIMAL(20, 9) DEFAULT 0,    -- 累计卖出换回的 SOL
    total_token_amount DECIMAL(30, 0) DEFAULT 0, -- 累计买入的代币原始数量
    
    -- 增量更新同步位
    last_signature TEXT,                   -- 上次抓取到的最后一笔交易签名
    
    PRIMARY KEY (wallet_address, token_mint)
);
``
