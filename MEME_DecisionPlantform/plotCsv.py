import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. 模拟/读取数据 (确保包含 time, open, high, low, close, volume)
df = pd.read_csv('history_15min_61Wj56.csv')
df['time'] = pd.to_datetime(df['time'])

# 2. 定义 GMGN 风格配色
COLOR_UP = '#26a69a' # 翡翠绿
COLOR_DOWN = '#ef5350' # 珊瑚红
BG_COLOR = '#131722'  # 深蓝色背景 (TradingView 经典色)
GRID_COLOR = '#363c4e' # 网格线颜色

# 3. 创建带子图的画布 (主图 + 底部成交量)
# vertical_spacing=0 表示主图和成交量无缝衔接
fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                    vertical_spacing=0.01,
                    row_heights=[0.8, 0.2])

# 4. 绘制 K 线 (Row 1)
fig.add_trace(go.Candlestick(
    x=df['time'],
    open=df['open'], high=df['high'],
    low=df['low'], close=df['close'],
    increasing_line_color=COLOR_UP,
    decreasing_line_color=COLOR_DOWN,
    increasing_fillcolor=COLOR_UP,
    decreasing_fillcolor=COLOR_DOWN,
    name='Price'
), row=1, col=1)

# 5. 绘制成交量 (Row 2)
# 根据涨跌设置成交量颜色
colors = [COLOR_UP if row['close'] >= row['open'] else COLOR_DOWN for _, row in df.iterrows()]

fig.add_trace(go.Bar(
    x=df['time'],
    y=df['volume'],
    marker_color=colors,
    opacity=0.8,
    name='Volume',
    showlegend=False
), row=2, col=1)

# 6. 布局深度优化
fig.update_layout(
    template='plotly_dark',
    plot_bgcolor=BG_COLOR,
    paper_bgcolor=BG_COLOR,
    margin=dict(l=10, r=50, t=30, b=10), # 压缩边距，留出右侧坐标空间
    xaxis_rangeslider_visible=False,      # 隐藏滑块
    hovermode='x unified',               # 悬停时显示整列数据
)

# 7. 坐标轴精修
# Y轴移到右侧，设置格式以防止科学计数法显示
fig.update_yaxes(
    side='right',
    gridcolor=GRID_COLOR,
    zeroline=False,
    tickformat='.8f', # 针对低价代币显示 8 位小数
    row=1, col=1
)

fig.update_yaxes(
    side='right',
    gridcolor=GRID_COLOR,
    showticklabels=False, # 隐藏成交量的数字
    row=2, col=1
)

fig.update_xaxes(
    gridcolor=GRID_COLOR,
    rangeslider_visible=False,
    type='date'
)

# 显示图表
fig.show()