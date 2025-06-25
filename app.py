from dash import Dash, html, dcc, Output, Input
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from helper import random_sector_data, fetch_latest_row, stock_data, dates, price_range_labels

app = Dash()

app.layout = html.Div(
    style={'backgroundColor': '#181c23', 'height': '100vh', 'padding': '0', 'fontFamily': '微软雅黑,Arial'},
    children=[
        # 顶部导航栏
        html.Div([
            html.Span("Level-2 深度分析云端版", style={'color': '#ff3c00', 'fontWeight': 'bold', 'fontSize': '22px', 'marginRight': '30px'}),
            html.Span("自选股[6]", style={'color': '#fff', 'marginRight': '30px'}),
            html.Span("涨幅排行[60]", style={'color': '#fff', 'marginRight': '30px'}),
            html.Span("资讯", style={'color': '#fff', 'marginRight': '30px'}),
            html.Span("DDE全景图", style={'color': '#fff', 'marginRight': '30px'}),
            html.Span("快捷热榜[80]", style={'color': '#fff'}),
            html.Span("个人中心", style={'float': 'right', 'color': '#fff', 'marginLeft': 'auto'})
        ], style={'backgroundColor': '#23262e', 'padding': '10px 30px', 'display': 'flex', 'alignItems': 'center'}),
        # 2x2 网格主体
        html.Div([
            # 第一行
            html.Div([
                html.Div([
                    html.H4("自选股", style={'color': '#fff', 'marginBottom': '10px'}),
                    dcc.Dropdown(
                        id='stock-list',
                        options=[{'label': name, 'value': name} for name in stock_data.keys()],
                        value='上证指数',
                        style={'height': '30px', 'width': '100%', 'marginBottom': '20px'}
                    ),
                    html.Div(id='stock-list-table', style={'color': '#fff', 'fontSize': '15px'})
                ], style={'backgroundColor': '#23262e', 'borderRadius': '8px', 'padding': '20px', 'margin': '10px', 'width': 'calc(50% - 40px)', 'height': 'calc(50vh - 60px)'}),
                html.Div([
                    dcc.Graph(id='stock-graph', config={'displayModeBar': False})
                ], style={'backgroundColor': '#23262e', 'borderRadius': '8px', 'padding': '20px', 'margin': '10px', 'width': 'calc(50% - 40px)', 'height': 'calc(50vh - 60px)'})
            ], style={'display': 'flex', 'width': '100%', 'height': '50%'}),
            # 第二行
            html.Div([
                html.Div([
                    dcc.Graph(id='treemap', config={'displayModeBar': False}),
                    dcc.Interval(id='interval-treemap', interval=3*1000, n_intervals=0)
                ], style={'backgroundColor': '#23262e', 'borderRadius': '8px', 'padding': '20px', 'margin': '10px', 'width': 'calc(50% - 40px)', 'height': 'calc(50vh - 60px)'}),
                html.Div([
                    html.Div(id='summary-box', style={'display': 'flex', 'justifyContent': 'center', 'gap': '40px', 'fontSize': '18px', 'color': 'white', 'marginBottom': '10px'}),
                    dcc.Graph(id='bar-chart', config={'displayModeBar': False}),
                    dcc.Interval(id='interval-bar', interval=3*1000, n_intervals=0)
                ], style={'backgroundColor': '#23262e', 'borderRadius': '8px', 'padding': '20px', 'margin': '10px', 'width': 'calc(50% - 40px)', 'height': 'calc(50vh - 60px)'})
            ], style={'display': 'flex', 'width': '100%', 'height': '50%'})
        ], style={'width': '100%', 'height': 'calc(100vh - 60px)'})
    ]
)


# ========== 指数走势回调 ==========
@app.callback(
    Output('stock-graph', 'figure'),
    Input('stock-list', 'value')
)
def update_graph(selected_stock):
    y = stock_data[selected_stock]
    fig = go.Figure(
        go.Scatter(x=dates, y=y, mode='lines+markers', line=dict(color='deepskyblue'))
    )
    fig.update_layout(
        title=f"{selected_stock} 价格走势",
        plot_bgcolor='#23262e',
        paper_bgcolor='#23262e',
        font_color='white',
        xaxis_title='日期',
        yaxis_title='价格',
        margin=dict(l=30, r=10, t=40, b=30),
        height=300
    )
    return fig

# ========== 板块热力图回调 ==========
@app.callback(
    Output('treemap', 'figure'),
    Input('interval-treemap', 'n_intervals')
)
def update_treemap(n):
    df = random_sector_data()
    fig = px.treemap(
        df,
        path=['root', '板块'],
        values='市值',
        color='涨跌幅',
        color_continuous_scale=[(0, "#b7e6d9"), (0.5, "#fff"), (1, "#f8d7da")],
        color_continuous_midpoint=0,
        custom_data=['涨跌幅_str'],
    )
    fig.update_traces(
        texttemplate='<b>%{label}</b><br>%{customdata[0]}%',
        textfont_size=16,
        textfont_color='black',
        hovertemplate='<b>%{label}</b><br>涨跌幅: %{customdata[0]}%<br>市值: %{value}<extra></extra>',
        marker_line_color='rgba(0,0,0,0)',
        marker_line_width=0,
        root_color='white'
    )
    fig.update_layout(
        margin=dict(t=40, l=10, r=10, b=10),
        plot_bgcolor='white',
        paper_bgcolor='white',
        coloraxis_colorbar=dict(
            title="涨跌幅(%)",
            tickvals=[-3, -2, -1, 0, 1, 2, 3],
            lenmode="pixels", len=200
        ),
        height=300
    )
    return fig

# ========== 涨跌分布回调 ==========
@app.callback(
    [Output('bar-chart', 'figure'),
     Output('summary-box', 'children')],
    Input('interval-bar', 'n_intervals')
)
def update_bar_chart(n):
    df = fetch_latest_row()
    if df is None or df.empty:
        return go.Figure(), ""
    row = df.iloc[0]
    shanghai_time = pd.to_datetime(row['TIMESTAMP']) + pd.Timedelta(hours=8)
    shanghai_time_str = shanghai_time.strftime('%Y-%m-%d %H:%M:%S')
    y = [
        row['price_range_0'], row['price_range_1'], row['price_range_2'],
        row['price_range_3'], row['price_range_4'], row['price_range_5'],
        row['price_range_6'], row['price_range_7'], row['price_range_8']
    ]
    up_count = int(sum([row['price_range_5'], row['price_range_6'], row['price_range_7'], row['price_range_8']]))
    down_count = int(sum([row['price_range_0'], row['price_range_1'], row['price_range_2'], row['price_range_3']]))
    up_limit = int(row['num_upper_limit'])
    down_limit = int(row['num_lower_limit'])

    summary = [
        html.Span(f"上涨: {up_count}", style={'color': 'red', 'marginRight': '20px'}),
        html.Span(f"涨停: {up_limit}", style={'color': 'red', 'marginRight': '40px'}),
        html.Span(f"下跌: {down_count}", style={'color': 'lime', 'marginRight': '20px'}),
        html.Span(f"跌停: {down_limit}", style={'color': 'lime'})
    ]

    fig = go.Figure(
        data=go.Bar(x=price_range_labels, y=y, marker_color='deepskyblue')
    )
    fig.update_layout(
        title=f"时间: {shanghai_time_str}",
        xaxis_title='涨跌幅区间',
        yaxis_title='股票数量',
        plot_bgcolor='#23262e',
        paper_bgcolor='#23262e',
        font_color='white',
        height=300
    )
    return fig, summary

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8052)