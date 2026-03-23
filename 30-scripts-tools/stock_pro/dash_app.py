"""
Stock PRO Dashboard v2.2 - Enhanced UI with Performance Optimizations
Run: python dash_app.py | Open: http://127.0.0.1:8050
"""
import dash
from dash import dcc, html, Input, Output, callback_context
import plotly.graph_objects as go
from pathlib import Path
import sys
from datetime import datetime, timedelta
import threading

sys.path.insert(0, str(Path(__file__).parent.parent))
from stock_pro import analyze, top_picks, value_picks, growth_picks, dividend_picks
from stock_pro.core import A, P

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Stock PRO v2.2"

# Cache system
class Cache:
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()

    def get(self, key, ttl=300):  # 5 minutes default
        with self.lock:
            if key in self.data:
                data, timestamp = self.data[key]
                if datetime.now() - timestamp < timedelta(seconds=ttl):
                    return data
                else:
                    del self.data[key]
            return None

    def set(self, key, value):
        with self.lock:
            self.data[key] = (value, datetime.now())

    def clear(self):
        with self.lock:
            self.data.clear()

cache = Cache()

# Theme colors
light_theme = {
    'bg': '#f8fafc', 'card': 'rgba(255,255,255,0.9)', 'border': 'rgba(0,0,0,0.1)',
    'text': '#1e293b', 'muted': '#64748b', 'primary': '#6366f1', 'bull': '#10b981',
    'bear': '#ef4444', 'amber': '#f59e0b', 'purple': '#8b5cf6', 'cyan': '#06b6d4'
}

dark_theme = {
    'bg': '#0f0f23', 'card': 'rgba(30,30,60,0.85)', 'border': 'rgba(255,255,255,0.08)',
    'text': '#e0e0e0', 'muted': '#8b8b9a', 'primary': '#6366f1', 'bull': '#10b981',
    'bear': '#ef4444', 'amber': '#f59e0b', 'purple': '#8b5cf6', 'cyan': '#06b6d4'
}

# Default theme
C = dark_theme

# Sidebar styles
SIDEBAR_BASE = {'padding': '16px 24px', 'color': C['muted'], 'cursor': 'pointer',
                'fontSize': '14px', 'fontWeight': '500', 'borderLeft': '4px solid transparent',
                'transition': 'all 0.2s ease', 'borderRadius': '0 12px 12px 0', 'margin': '4px 0'}
SIDEBAR_HOVER = {'background': 'rgba(99,102,241,0.1)', 'color': C['text']}
SIDEBAR_ACTIVE = {'background': 'linear-gradient(90deg, rgba(99,102,241,0.25), rgba(99,102,241,0.05))',
                  'color': C['primary'], 'borderLeft': f'4px solid {C["primary"]}'}

def fmt(n, d=2):
    if n is None: return "N/A"
    try: return f"{n:,.{d}f}"
    except: return str(n)

def sc(s):
    return '#059669' if s>=80 else '#10b981' if s>=70 else '#f59e0b' if s>=50 else '#f97316' if s>=30 else '#ef4444'

def sl(s):
    return "STRONG BUY" if s>=80 else "BUY" if s>=70 else "HOLD" if s>=50 else "SELL" if s>=30 else "STRONG SELL"

# Card with hover effect
def glass(content, style=None, hover=True, className=None):
    base = {'background': C['card'], 'backdropFilter': 'blur(20px)', 'borderRadius': '20px',
            'border': f'1px solid {C["border"]}', 'padding': '24px', 'marginBottom': '20px',
            'boxShadow': '0 8px 32px rgba(0,0,0,0.3)', 'transition': 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            'position': 'relative', 'overflow': 'hidden'}
    # Add subtle gradient overlay
    overlay = html.Div(style={'position': 'absolute', 'top': 0, 'left': 0, 'right': 0, 'bottom': 0,
                              'background': 'linear-gradient(135deg, rgba(99,102,241,0.05), rgba(139,92,246,0.05))',
                              'pointerEvents': 'none'})
    if style: base.update(style)
    if hover:
        base['_hover'] = {
            'transform': 'translateY(-4px) scale(1.02)',
            'boxShadow': '0 12px 40px rgba(99,102,241,0.3)',
            'borderColor': 'rgba(99,102,241,0.3)'
        }
    return html.Div([overlay] + content, style=base, className=className)

# Enhanced Stat Card
def stat_card(title, val, chg=None, icon=None, acc=None):
    chg_str, chg_clr = "", C['muted']
    if chg is not None:
        chg_str = f"{'↑' if chg>=0 else '↓'} {abs(chg):.1f}%"
        chg_clr = C['bull'] if chg>=0 else C['bear']
    top = {'borderTop': f'4px solid {acc}'} if acc else {}
    return glass([
        html.Div([html.Span(icon, style={'fontSize':'28px'}) if icon else html.Div()],
                 style={'marginBottom':'12px'}),
        html.Div(title, style={'fontSize':'11px','color':C['muted'],'textTransform':'uppercase',
                               'letterSpacing':'1px','marginBottom':'8px'}),
        html.Div(val, style={'fontSize':'32px','fontWeight':'800','background':f'linear-gradient(135deg, {C["text"]}, #fff)',
                            '-webkit-background-clip':'text','-webkit-text-fill-color':'transparent'}),
        html.Div(chg_str, style={'fontSize':'13px','marginTop':'8px','color':chg_clr,'fontWeight':'600'}) if chg is not None else html.Div(),
    ], {**top, 'textAlign':'left', 'padding':'28px'})

# Enhanced Stock Card
def stock_card(sym):
    try:
        # Check cache first
        cache_key = f"stock_{sym}"
        data = cache.get(cache_key)
        if not data:
            # Set loading state in cache
            cache.set(cache_key, 'loading')
            # Fetch data
            data = analyze(sym)
            # Format market cap
            mkt = data.get('marketCap', 0)
            if mkt > 1e12:
                data['marketCap'] = f"${mkt /1e12:.1f}T"
            elif mkt > 1e9:
                data['marketCap'] = f"${mkt /1e9:.1f}B"
            else:
                data['marketCap'] = f"${mkt /1e6:.0f}M" if mkt > 0 else "N/A"
            # Store in cache
            cache.set(cache_key, data)

        # If data is still loading (async case)
        if data == 'loading':
            return glass([
                html.Div('Loading...', style={'textAlign':'center','padding':'40px','color':C['muted']}),
                html.Div([
                    html.Div(style={'width':'40px','height':'40px','border':'3px solid rgba(99,102,241,0.3)','borderTop':'3px solid #6366f1','borderRadius':'50%','animation':'spin 1s linear infinite','margin':'10px auto'})
                ], style={'display':'flex','justifyContent':'center'})
            ])

        # Check for errors in data
        if not data or 'error' in data:
            return glass([
                html.Div('❌ Error', style={'textAlign':'center','padding':'40px','color':C['bear'],'fontSize':'18px','fontWeight':'700'}),
                html.Div(f"Failed to load {sym}", style={'textAlign':'center','color':C['muted'],'marginTop':'8px'}),
                html.Div(data.get('error', 'Unknown error'), style={'textAlign':'center','color':C['muted'],'fontSize':'12px','marginTop':'4px'})
            ])

        return glass([
            # Header Row
            html.Div([
                html.Div([
                    html.Div(sym, style={'fontSize':'22px','fontWeight':'800','letterSpacing':'0.5px','marginBottom':'4px'}),
                    html.Div(data.get('recommend', data.get('rating', 'N/A')), style={'fontSize':'11px','color':sc(data.get('score', 50)),'fontWeight':'700',
                                    'letterSpacing':'1px','textTransform':'uppercase'}),
                ]),
                html.Div([
                    html.Div(f"${fmt(data.get('price', 0))}", style={'fontSize':'26px','fontWeight':'800','textAlign':'right'}),
                    html.Div(f"{data.get('upside', 0):+.1f}% upside", style={'fontSize':'12px','color':C['bull'] if data.get('upside', 0)>10 else C['amber'] if data.get('upside', 0)>0 else C['bear'],'fontWeight':'600','textAlign':'right'}),
                ])
            ], style={'display':'flex','justifyContent':'space-between','alignItems':'flex-start','marginBottom':'20px'}),

            # Score Section
            html.Div([
                html.Div([html.Div(sl(data.get('score', 50)), style={'fontSize':'9px','fontWeight':'700','color':'white','letterSpacing':'1px'}),
                          html.Div(f"{data.get('score', 50)}/100", style={'fontSize':'11px','color':C['muted'],'marginLeft':'auto'})],
                         style={'display':'flex','justifyContent':'space-between','marginBottom':'8px'}),
                html.Div([
                    html.Div('', style={'height':'10px','borderRadius':'5px',
                                'background':f'linear-gradient(90deg, {sc(data.get('score', 50))} {data.get('score', 50)}%, rgba(255,255,255,0.15) {data.get('score', 50)}%)'}),
                ], style={'background':'rgba(0,0,0,0.3)','borderRadius':'5px'}),
            ], style={'marginBottom':'20px'}),

            # Key Metrics - 2x2 Grid
            html.Div([
                html.Div([html.Div('P/E', style={'fontSize':'10px','color':C['muted'],'marginBottom':'4px'}),
                          html.Div(fmt(data.get('pe', 0)), style={'fontSize':'16px','fontWeight':'700'})],
                         style={'padding':'14px','background':'rgba(0,0,0,0.2)','borderRadius':'12px','textAlign':'center'}),
                html.Div([html.Div('EPS', style={'fontSize':'10px','color':C['muted'],'marginBottom':'4px'}),
                          html.Div(f"${fmt(data.get('eps', 0))}", style={'fontSize':'16px','fontWeight':'700'})],
                         style={'padding':'14px','background':'rgba(0,0,0,0.2)','borderRadius':'12px','textAlign':'center'}),
                html.Div([html.Div('Target', style={'fontSize':'10px','color':C['muted'],'marginBottom':'4px'}),
                          html.Div(f"${fmt(data.get('target', 0))}", style={'fontSize':'16px','fontWeight':'700'})],
                         style={'padding':'14px','background':'rgba(0,0,0,0.2)','borderRadius':'12px','textAlign':'center'}),
                html.Div([html.Div('Market Cap', style={'fontSize':'10px','color':C['muted'],'marginBottom':'4px'}),
                          html.Div(data.get('marketCap', 'N/A'), style={'fontSize':'16px','fontWeight':'700'})],
                         style={'padding':'14px','background':'rgba(0,0,0,0.2)','borderRadius':'12px','textAlign':'center'}),
            ], style={'display':'grid','gridTemplateColumns':'repeat(2, 1fr)','gap':'12px','marginBottom':'20px'}),

            # Action Button
            html.Div([html.Button('View Full Analysis', n_clicks=0,
                       style={'width':'100%',
                              'background':f'linear-gradient(135deg, {C["primary"]}, {C["purple"]})',
                              'border':'none','color':'white','padding':'14px','borderRadius':'12px',
                              'cursor':'pointer','fontSize':'14px','fontWeight':'600',
                              'boxShadow':'0 4px 15px rgba(99,102,241,0.3)',
                              'transition':'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                              'position':'relative',
                              'overflow':'hidden',
                              # Hover effects
                              '_hover': {
                                  'transform': 'translateY(-2px)',
                                  'boxShadow': '0 6px 20px rgba(99,102,241,0.4)'
                              },
                              '_active': {
                                  'transform': 'translateY(0)'
                              }})]),
        ])
    except Exception as e:
        # Clear cache on error
        cache.set(f"stock_{sym}", None)
        return glass([
            html.Div('❌ Error', style={'textAlign':'center','padding':'40px','color':C['bear'],'fontSize':'18px','fontWeight':'700'}),
            html.Div(f"Failed to load {sym}", style={'textAlign':'center','color':C['muted'],'marginTop':'8px'}),
            html.Div(f"{str(e)[:50]}...", style={'textAlign':'center','color':C['muted'],'fontSize':'12px','marginTop':'4px'})
        ])

def price_chart(sym, time_range='3mo'):
    import json, urllib.request
    closes = []
    volumes = []
    highs = []
    lows = []
    opens = []
    try:
        # Check cache first
        cache_key = f"chart_{sym}_{time_range}"
        chart_data = cache.get(cache_key, ttl=600)  # 10 minutes for chart data
        if not chart_data:
            # Set loading state
            cache.set(cache_key, 'loading')
            # Fetch data from API
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range={time_range}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                result = data["chart"]["result"][0]
                quote = result["indicators"]["quote"][0]
                chart_data = {
                    'closes': quote.get("close", []),
                    'volumes': quote.get("volume", []),
                    'highs': quote.get("high", []),
                    'lows': quote.get("low", []),
                    'opens': quote.get("open", [])
                }
                cache.set(cache_key, chart_data)

        # If data is still loading
        if chart_data == 'loading':
            return glass([
                html.Div('Loading chart...', style={'textAlign':'center','padding':'60px','color':C['muted'],'fontSize':'16px'}),
                html.Div([
                    html.Div(style={'width':'50px','height':'50px','border':'4px solid rgba(99,102,241,0.3)','borderTop':'4px solid #6366f1','borderRadius':'50%','animation':'spin 1s linear infinite','margin':'15px auto'})
                ], style={'display':'flex','justifyContent':'center'})
            ])

        # Extract data from cache or API response
        closes = chart_data.get('closes', [])
        volumes = chart_data.get('volumes', [])
        highs = chart_data.get('highs', [])
        lows = chart_data.get('lows', [])
        opens = chart_data.get('opens', [])
    except Exception as e:
        # Clear cache on error
        cache.set(f"chart_{sym}_{time_range}", None)
        return glass([
            html.Div('❌ Error', style={'textAlign':'center','padding':'60px','color':C['bear'],'fontSize':'18px','fontWeight':'700'}),
            html.Div(f"Failed to load chart for {sym}", style={'textAlign':'center','color':C['muted'],'marginTop':'8px'}),
            html.Div(f"{str(e)[:60]}...", style={'textAlign':'center','color':C['muted'],'fontSize':'12px','marginTop':'4px'})
        ])

    if not closes:
        return glass([
            html.Div('📊 No Data', style={'textAlign':'center','padding':'60px','color':C['muted'],'fontSize':'18px','fontWeight':'700'}),
            html.Div(f"No chart data available for {sym}", style={'textAlign':'center','color':C['muted'],'marginTop':'8px'})
        ])

    n = min(90, len(closes))
    closes = closes[-n:]
    volumes = volumes[-n:] if volumes else [0] *n
    highs = highs[-n:] if highs else closes
    lows = lows[-n:] if lows else closes
    opens = opens[-n:] if opens else closes

    # Moving averages
    ma20 = [sum(closes[max(0,i -19):i +1]) /min(i +1,20) for i in range(n)]
    ma50 = [sum(closes[max(0,i -49):i +1]) /min(i +1,50) for i in range(n)]

    # RSI calculation
    def calculate_rsi(prices, period=14):
        deltas = [prices[i] - prices[i -1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        rsi = []
        if avg_loss == 0:
            rsi.append(100)
        else:
            rs = avg_gain / avg_loss
            rsi.append(100 - (100 / (1 + rs)))
        for i in range(period, len(deltas)):
            delta = deltas[i]
            gain = delta if delta > 0 else 0
            loss = -delta if delta < 0 else 0
            avg_gain = (avg_gain * (period - 1) + gain) / period
            avg_loss = (avg_loss * (period - 1) + loss) / period
            if avg_loss == 0:
                rsi.append(100)
            else:
                rs = avg_gain / avg_loss
                rsi.append(100 - (100 / (1 + rs)))
        # Pad with None for the first period
        rsi = [None] * (period) + rsi
        return rsi[-n:]

    rsi = calculate_rsi(closes)

    # Price change
    price_change = closes[-1] - closes[0] if len(closes) > 1 else 0
    pct_change = (price_change / closes[0] * 100) if closes[0] > 0 else 0
    change_clr = C['bull'] if pct_change >= 0 else C['bear']

    # Main price chart
    price_fig = go.Figure()
    # Candlestick
    price_fig.add_trace(go.Candlestick(x=list(range(n)), open=opens, high=highs, low=lows, close=closes,
                                  name='Price', increasing_line_color=C['bull'], decreasing_line_color=C['bear'],
                                  increasing_fillcolor=C['bull'], decreasing_fillcolor=C['bear'],
                                  whiskerwidth=0.8))
    # MA20
    price_fig.add_trace(go.Scatter(x=list(range(n)), y=ma20, mode='lines', name='MA20',
                             line=dict(color=C['amber'], width=2.5)))
    # MA50
    price_fig.add_trace(go.Scatter(x=list(range(n)), y=ma50, mode='lines', name='MA50',
                             line=dict(color=C['cyan'], width=2.5)))

    # Price annotation
    price_fig.add_annotation(x=n -1, y=closes[-1], text=f"${fmt(closes[-1])}",
                      showarrow=False, font=dict(size=16, color=C['text'], family="Arial Black"),
                      yshift=20)

    price_fig.update_layout({
        'plot_bgcolor':'#0f0f23', 'paper_bgcolor':'#0f0f23', 'font':{'color':C['text'], 'size':12},
        'xaxis':{'showgrid':False, 'zeroline':False, 'tickfont':{'color':C['muted'], 'size':10}, 'showticklabels':True},
        'yaxis':{'showgrid':True, 'gridcolor':'rgba(255,255,255,0.03)', 'zeroline':False, 'tickfont':{'color':C['muted']}},
        'legend':{'orientation':'h', 'y':1.12, 'x':0.5, 'xanchor':'center', 'font':{'color':C['text'], 'size':11},
                 'bgcolor':'rgba(0,0,0,0)', 'borderwidth':0},
        'margin':{'l':50, 'r':50, 't':30, 'b':30}, 'height':400, 'hovermode':'x unified',
        'showlegend':True,
    })
    price_fig.update_xaxes(showspikes=True, spikecolor=C['muted'], spikethickness=1, spikemode='across')
    price_fig.update_yaxes(showspikes=True, spikecolor=C['muted'], spikethickness=1, spikemode='across')

    # Volume chart
    volume_fig = go.Figure()
    volume_fig.add_trace(go.Bar(x=list(range(n)), y=volumes, name='Volume',
                               marker_color=[C['bull'] if closes[i] >= closes[i -1] else C['bear'] for i in range(n)],
                               opacity=0.7))
    volume_fig.update_layout({
        'plot_bgcolor':'#0f0f23', 'paper_bgcolor':'#0f0f23', 'font':{'color':C['text'], 'size':12},
        'xaxis':{'showgrid':False, 'zeroline':False, 'tickfont':{'color':C['muted'], 'size':10}, 'showticklabels':True},
        'yaxis':{'showgrid':True, 'gridcolor':'rgba(255,255,255,0.03)', 'zeroline':False, 'tickfont':{'color':C['muted']}},
        'legend':{'orientation':'h', 'y':1.1, 'x':0.5, 'xanchor':'center', 'font':{'color':C['text'], 'size':11},
                 'bgcolor':'rgba(0,0,0,0)', 'borderwidth':0},
        'margin':{'l':50, 'r':50, 't':20, 'b':30}, 'height':200,
        'showlegend':False,
    })

    # RSI chart
    rsi_fig = go.Figure()
    rsi_fig.add_trace(go.Scatter(x=list(range(n)), y=rsi, mode='lines', name='RSI',
                                line=dict(color=C['purple'], width=2.5)))
    # RSI thresholds
    rsi_fig.add_shape(type="line", x0=0, y0=70, x1=n -1, y1=70, line=dict(color=C['bear'], width=1, dash="dash"))
    rsi_fig.add_shape(type="line", x0=0, y0=30, x1=n -1, y1=30, line=dict(color=C['bull'], width=1, dash="dash"))
    rsi_fig.update_layout({
        'plot_bgcolor':'#0f0f23', 'paper_bgcolor':'#0f0f23', 'font':{'color':C['text'], 'size':12},
        'xaxis':{'showgrid':False, 'zeroline':False, 'tickfont':{'color':C['muted'], 'size':10}, 'showticklabels':True},
        'yaxis':{'showgrid':True, 'gridcolor':'rgba(255,255,255,0.03)', 'zeroline':False, 'tickfont':{'color':C['muted']}, 'range':[0, 100]},
        'legend':{'orientation':'h', 'y':1.1, 'x':0.5, 'xanchor':'center', 'font':{'color':C['text'], 'size':11},
                 'bgcolor':'rgba(0,0,0,0)', 'borderwidth':0},
        'margin':{'l':50, 'r':50, 't':20, 'b':30}, 'height':200,
        'showlegend':True,
    })

    return html.Div([
        html.Div([
            html.Div([html.Div(f"${fmt(closes[-1])}", style={'fontSize':'32px','fontWeight':'800'}),
                     html.Div([f"{'+' if pct_change >= 0 else ''}{pct_change:.2f}%",
                              f"({'↑' if pct_change >= 0 else '↓'} ${abs(price_change):.2f})"],
                             style={'fontSize':'14px','color':change_clr,'fontWeight':'600','marginTop':'4px'})],
                    style={'textAlign':'center'}),
        ], style={'padding':'20px','background':'rgba(0,0,0,0.2)','borderRadius':'16px','marginBottom':'20px'}),
        dcc.Graph(figure=price_fig, config={'displayModeBar':True, 'responsive':True, 'displaylogo':False}),
        html.Div(style={'height':'20px'}),
        dcc.Graph(figure=volume_fig, config={'displayModeBar':False, 'responsive':True, 'displaylogo':False}),
        html.Div(style={'height':'20px'}),
        dcc.Graph(figure=rsi_fig, config={'displayModeBar':False, 'responsive':True, 'displaylogo':False}),
    ])

def get_stats():
    # Check cache first
    cache_key = "stats"
    stats = cache.get(cache_key, ttl=300)  # 5 minutes for stats
    if not stats:
        from stock_pro.core import A, P
        total = len(A)
        scores = [A[s][2] for s in A]
        avg = sum(scores) /len(scores) if scores else 65
        buys = len([s for s in A if A[s][1] in ['Overweight', 'Outperform', 'Strong Buy', 'Buy']])
        upsides = []
        for s in A:
            if s in P:
                target, _, _ = A[s]
                price = P[s]
                if price > 0: upsides.append((target - price) / price * 100)
        top_up = max(upsides) if upsides else 25

        stats = [
            stat_card('Total Stocks', total, icon='📈', acc=C['primary']),
            stat_card('Avg Score', f"{avg:.0f}", chg=2.1, icon='🎯', acc=C['purple']),
            stat_card('Top Upside', f"+{top_up:.1f}%", icon='🚀', acc=C['bull']),
            stat_card('Strong Buys', buys, icon='⭐', acc=C['amber']),
        ]
        cache.set(cache_key, stats)
    return stats

# ============================================================
# Layout
# ============================================================
DEFAULT_SYMS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'AMD', 'INTC', 'NFLX', 'CRM', 'ORCL']

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Interval(id='refresh', interval=30000, n_intervals=0),
    dcc.Store(id='active-nav', data='dashboard'),
    # Custom CSS using inline style approach
    html.Div(id='custom-css', style={'display': 'none'}),
    # Responsive CSS
    html.Div([
        html.Div(style={'display': 'none'}, children=[
            html.Script('''
                var style = document.createElement('style');
                style.textContent = `
                    @media (max-width: 768px) {
                        .sidebar {
                            width: 100% !important;
                            height: auto !important;
                            position: relative !important;
                            border-right: none !important;
                            border-bottom: 1px solid rgba(255,255,255,0.08) !important;
                            padding-bottom: 20px !important;
                        }
                        .main-content {
                            margin-left: 0 !important;
                            padding: 20px !important;
                        }
                        .stats-row {
                            grid-template-columns: repeat(2, 1fr) !important;
                            gap: 16px !important;
                        }
                        .stock-grid {
                            grid-template-columns: 1fr !important;
                            gap: 16px !important;
                        }
                        .header {
                            flex-direction: column !important;
                            align-items: flex-start !important;
                            gap: 16px !important;
                        }
                        .chart-controls {
                            flex-direction: column !important;
                            align-items: stretch !important;
                            gap: 12px !important;
                        }
                        .chart-controls > * {
                            width: 100% !important;
                        }
                        .chart-section {
                            padding: 20px !important;
                        }
                        h1 {
                            font-size: 24px !important;
                        }
                        .stat-card {
                            padding: 20px !important;
                        }
                        .stock-card {
                            padding: 20px !important;
                        }
                    }
                    
                    @media (max-width: 480px) {
                        .stats-row {
                            grid-template-columns: 1fr !important;
                        }
                        .main-content {
                            padding: 16px !important;
                        }
                        h1 {
                            font-size: 20px !important;
                        }
                        .chart-section {
                            padding: 16px !important;
                        }
                    }
                    
                    /* Loading animation */
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                `;
                document.head.appendChild(style);
            ''')
        ])
    ]),

    # Sidebar
    html.Div([
        # Logo
        html.Div([
            html.Span("📈", style={'fontSize':'32px','marginRight':'14px'}),
            html.Div([
                html.Div("Stock PRO", style={'fontSize':'22px','fontWeight':'800',
                    'background':'linear-gradient(135deg, #6366f1, #8b5cf6, #06b6d4)',
                    '-webkit-background-clip':'text','-webkit-text-fill-color':'transparent',
                    'background-clip':'text'}),
                html.Div("v2.1 Enhanced", style={'fontSize':'11px','color':'#8b8b9a','marginTop':'2px'}),
            ])
        ], style={'padding':'15px 24px 30px','borderBottom':'1px solid rgba(255,255,255,0.08)'}),

        # Nav Items
        html.Div([
            html.Div([html.Span('📊', style={'marginRight':'12px'}), 'Dashboard'],
                    id='nav-dashboard', n_clicks=0, style=SIDEBAR_ACTIVE, className='sidebar-item nav-btn'),
            html.Div([html.Span('🔍', style={'marginRight':'12px'}), 'Search'],
                    id='nav-search', n_clicks=0, style={**SIDEBAR_BASE, **SIDEBAR_HOVER}, className='sidebar-item nav-btn'),
            html.Div([html.Span('⭐', style={'marginRight':'12px'}), 'Top Picks'],
                    id='nav-picks', n_clicks=0, style={**SIDEBAR_BASE, **SIDEBAR_HOVER}, className='sidebar-item nav-btn'),
            html.Div([html.Span('💎', style={'marginRight':'12px'}), 'Value Stocks'],
                    id='nav-value', n_clicks=0, style={**SIDEBAR_BASE, **SIDEBAR_HOVER}, className='sidebar-item nav-btn'),
            html.Div([html.Span('🚀', style={'marginRight':'12px'}), 'Growth Stocks'],
                    id='nav-growth', n_clicks=0, style={**SIDEBAR_BASE, **SIDEBAR_HOVER}, className='sidebar-item nav-btn'),
            html.Div([html.Span('💰', style={'marginRight':'12px'}), 'Dividend'],
                    id='nav-dividend', n_clicks=0, style={**SIDEBAR_BASE, **SIDEBAR_HOVER}, className='sidebar-item nav-btn'),
        ], style={'marginTop':'20px'}),

        # Market Status
        html.Div([
            html.Div('Market Status', style={'fontSize':'11px','color':'#8b8b9a','marginBottom':'10px','letterSpacing':'1px','textTransform':'uppercase'}),
            html.Div([html.Div('●', style={'color':'#10b981','fontSize':'10px','marginRight':'8px'}), 'US Market Open'],
                    style={'fontSize':'13px','color':'#e0e0e0','display':'flex','alignItems':'center'}),
        ], style={'padding':'20px 24px','borderTop':'1px solid rgba(255,255,255,0.08)','marginTop':'auto'}),

        # Last Update
        html.Div(id='last-update', children='Last: --',
                style={'padding':'16px 24px','color':'#8b8b9a','fontSize':'12px',
                      'borderTop':'1px solid rgba(255,255,255,0.08)'}),
    ], className='sidebar', style={'position':'fixed','left':'0','top':'0','height':'100vh','width':'280px',
              'background':'rgba(15,15,35,0.98)','backdropFilter':'blur(20px)',
              'borderRight':'1px solid rgba(255,255,255,0.08)','zIndex':'1000',
              'display':'flex','flexDirection':'column','overflowY':'auto'}),

    # Main Content
    html.Div([
        # Header
        html.Div([
            html.Div([
                html.H1(id='page-title', children='📊 Dashboard',
                       style={'fontSize':'32px','fontWeight':'800','margin':'0 0 8px 0',
                             'background':'linear-gradient(135deg, #e0e0e0, #fff)','-webkit-background-clip':'text','-webkit-text-fill-color':'transparent'}),
                html.Div(id='page-subtitle', children='Real-time market analysis powered by AI',
                        style={'color':'#8b8b9a','fontSize':'14px'})
            ]),
            # Quick Search and Theme Toggle
            html.Div([
                dcc.Input(id='quick-search', type='text', placeholder='Symbol (e.g. AAPL)...',
                         style={'padding':'12px 18px','borderRadius':'12px','border':'1px solid rgba(255,255,255,0.1)',
                                'background':'rgba(30,30,60,0.85)','color':'#e0e0e0','fontSize':'14px',
                                'width':'220px','outline':'none'}),
                html.Button('🌙', id='theme-toggle', n_clicks=0,
                           style={'padding':'12px','borderRadius':'12px','border':'1px solid rgba(255,255,255,0.1)',
                                  'background':'rgba(30,30,60,0.85)','color':'#e0e0e0','cursor':'pointer',
                                  'fontSize':'16px','transition':'all 0.3s ease'}),
            ], style={'display':'flex','gap':'12px','alignItems':'center'}),
        ], className='header', style={'display':'flex','justifyContent':'space-between','alignItems':'center','marginBottom':'32px'}),

        # Stats Row
        html.Div(id='stats-row', children=get_stats(), className='stats-row',
                style={'display':'grid','gridTemplateColumns':'repeat(4, 1fr)','gap':'24px','marginBottom':'32px'}),

        # Section Title
        html.Div([
            html.Div(id='section-title', children='Featured Stocks',
                    style={'fontSize':'18px','fontWeight':'700','color':'#e0e0e0'}),
            html.Div(id='stock-count', children='12 stocks',
                    style={'fontSize':'13px','color':'#8b8b9a','marginLeft':'12px'}),
        ], style={'display':'flex','alignItems':'center','marginBottom':'20px'}),

        # Stock Grid
        html.Div(id='stock-grid', children=[stock_card(s) for s in DEFAULT_SYMS], className='stock-grid',
                style={'display':'grid','gridTemplateColumns':'repeat(auto-fill, minmax(320px, 1fr))','gap':'24px'}),

        # Chart Section
        html.Div([
            html.H2('📊 Price Analysis', style={'fontSize':'20px','fontWeight':'700','marginBottom':'20px'}),
            html.Div([dcc.Dropdown(id='chart-sym', value='AAPL', clearable=False,
                        options=[{'label':s,'value':s} for s in DEFAULT_SYMS],
                        style={'width':'200px','color':'#0f0f23'}),
                      dcc.Dropdown(id='chart-range', value='3mo', clearable=False,
                        options=[
                            {'label':'1 Week', 'value':'1wk'},
                            {'label':'1 Month', 'value':'1mo'},
                            {'label':'3 Months', 'value':'3mo'},
                            {'label':'6 Months', 'value':'6mo'},
                            {'label':'1 Year', 'value':'1y'},
                            {'label':'5 Years', 'value':'5y'}
                        ],
                        style={'width':'150px','color':'#0f0f23'}),
                      html.Button([html.Span('🔄', style={'marginRight':'8px'}), 'Refresh'],
                                 id='refresh-chart', n_clicks=0,
                                 style={'background':'linear-gradient(135deg, #6366f1, #8b5cf6)',
                                        'border':'none','color':'white','padding':'10px 20px',
                                        'borderRadius':'10px','cursor':'pointer','fontWeight':'600','marginLeft':'auto'})],
                     className='chart-controls', style={'display':'flex','alignItems':'center','gap':'16px','marginBottom':'24px'}),
            html.Div(id='chart-container', children=price_chart('AAPL', '3mo')),
        ], className='chart-section', style={'marginTop':'40px','padding':'28px','background':'rgba(30,30,60,0.5)',
                 'borderRadius':'24px','border':'1px solid rgba(255,255,255,0.08)'}),
    ], className='main-content', style={'marginLeft':'300px','padding':'40px 50px','minHeight':'100vh',
              'background':'linear-gradient(135deg, #0f0f23 0%, #16162a 50%, #1a1a2e 100%)'}),
], style={'background':'#0f0f23','minHeight':'100vh',
          'fontFamily':"Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",'color':'#e0e0e0'})

# ============================================================
# Callbacks
# ============================================================
@app.callback([Output('stock-grid','children'), Output('stats-row','children'),
               Output('last-update','children'), Output('stock-count','children')],
              [Input('refresh','n_intervals'), Input('nav-picks','n_clicks'),
               Input('nav-value','n_clicks'), Input('nav-growth','n_clicks'), Input('nav-dividend','n_clicks')])
def update_stocks(n_int, *args):
    ctx = callback_context
    trigger = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'refresh'

    default_syms = DEFAULT_SYMS
    stocks = default_syms

    if trigger == 'nav-picks':
        stocks = top_picks(limit=12) or default_syms
    elif trigger == 'nav-value':
        stocks = value_picks(limit=12) or default_syms
    elif trigger == 'nav-growth':
        stocks = growth_picks(limit=12) or default_syms
    elif trigger == 'nav-dividend':
        stocks = dividend_picks(limit=12) or default_syms

    return [stock_card(s) for s in stocks[:12]], get_stats(), f"Updated: {datetime.now().strftime('%H:%M:%S')}", f"{len(stocks[:12])} stocks"

@app.callback(Output('chart-container','children'), [Input('chart-sym','value'), Input('chart-range','value'), Input('refresh-chart','n_clicks')])
def update_chart(sym, time_range, n):
    return price_chart(sym, time_range)

@app.callback([Output('page-title','children'), Output('page-subtitle','children'), Output('section-title','children')],
              [Input('nav-dashboard','n_clicks'), Input('nav-search','n_clicks'),
               Input('nav-picks','n_clicks'), Input('nav-value','n_clicks'),
               Input('nav-growth','n_clicks'), Input('nav-dividend','n_clicks')])
def update_nav(*args):
    ctx = callback_context
    trigger = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'nav-dashboard'
    views = {
        'nav-dashboard': ('📊 Dashboard', 'Real-time market analysis powered by AI', 'Featured Stocks'),
        'nav-search': ('🔍 Search', 'Find and analyze any stock', 'Search Results'),
        'nav-picks': ('⭐ Top Picks', 'Best opportunities by AI score', 'Top Rated Stocks'),
        'nav-value': ('💎 Value', 'Undervalued stocks with strong fundamentals', 'Value Opportunities'),
        'nav-growth': ('🚀 Growth', 'High growth potential stocks', 'Growth Stocks'),
        'nav-dividend': ('💰 Dividend', 'Income-generating stocks', 'Dividend Stocks'),
    }
    return views.get(trigger, views['nav-dashboard'])

# Theme toggle callback
@app.callback(
    [Output('theme-toggle', 'children'),
     Output('theme-toggle', 'style'),
     Output('main-content', 'style')],
    [Input('theme-toggle', 'n_clicks')]
)
def toggle_theme(n_clicks):
    global C
    if n_clicks % 2 == 1:
        # Switch to light theme
        C = light_theme
        return '🌙', {
            'padding':'12px','borderRadius':'12px','border':'1px solid rgba(0,0,0,0.1)',
            'background':'rgba(255,255,255,0.9)','color':'#1e293b','cursor':'pointer',
            'fontSize':'16px','transition':'all 0.3s ease'
        }, {
            'marginLeft':'300px','padding':'40px 50px','minHeight':'100vh',
            'background':'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #cbd5e1 100%)'
        }
    else:
        # Switch to dark theme
        C = dark_theme
        return '☀️', {
            'padding':'12px','borderRadius':'12px','border':'1px solid rgba(255,255,255,0.1)',
            'background':'rgba(30,30,60,0.85)','color':'#e0e0e0','cursor':'pointer',
            'fontSize':'16px','transition':'all 0.3s ease'
        }, {
            'marginLeft':'300px','padding':'40px 50px','minHeight':'100vh',
            'background':'linear-gradient(135deg, #0f0f23 0%, #16162a 50%, #1a1a2e 100%)'
        }

# ============================================================
# Run
# ============================================================
if __name__ == '__main__':
    print("=" *50)
    print("  Stock PRO Dashboard v2.1")
    print("  Open: http://127.0.0.1:8050")
    print("=" *50)
    app.run(debug=False, port=8050, threaded=True)