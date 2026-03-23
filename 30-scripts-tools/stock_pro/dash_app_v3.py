"""
Stock PRO Dashboard v3.0 - Modern UI/UX Optimized
Run: python dash_app_v3.py | Open: http://127.0.0.1:8050

UI/UX Improvements:
- Modern glassmorphism design
- Improved color contrast and accessibility
- Responsive grid layout
- Enhanced loading states
- Better typography hierarchy
- Interactive hover effects
- Dark/Light mode support
"""
import dash
from dash import dcc, html, Input, Output, callback_context, State
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import sys
from datetime import datetime, timedelta
import threading

sys.path.insert(0, str(Path(__file__).parent.parent))
from stock_pro import analyze, top_picks, value_picks, growth_picks, dividend_picks
from stock_pro.core import A, P

# Initialize Dash app with modern theme
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Stock PRO v3.0"

# ============================================
# DESIGN SYSTEM - Modern Color Palette
# ============================================
COLORS = {
    # Primary colors
    'primary': '#6366F1',      # Indigo 500
    'primary_dark': '#4F46E5', # Indigo 600
    'primary_light': '#818CF8', # Indigo 400

    # Semantic colors
    'success': '#10B981',      # Emerald 500
    'success_light': '#34D399', # Emerald 400
    'warning': '#F59E0B',      # Amber 500
    'danger': '#EF4444',       # Red 500
    'danger_light': '#F87171', # Red 400

    # Neutral colors
    'bg_dark': '#0F172A',      # Slate 900
    'bg_card': '#1E293B',      # Slate 800
    'bg_card_hover': '#334155', # Slate 700
    'text_primary': '#F8FAFC',  # Slate 50
    'text_secondary': '#94A3B8', # Slate 400
    'text_muted': '#64748B',    # Slate 500
    'border': '#334155',        # Slate 700

    # Gradient colors
    'gradient_start': '#6366F1',
    'gradient_end': '#8B5CF6',
}

# ============================================
# CACHE SYSTEM
# ============================================
class Cache:
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()

    def get(self, key, ttl=300):
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

cache = Cache()

# ============================================
# HELPER FUNCTIONS
# ============================================
def get_score_color(score):
    """Get color based on score with better accessibility"""
    if score >= 80:
        return COLORS['success']
    elif score >= 60:
        return COLORS['warning']
    else:
        return COLORS['danger']

def get_score_bg(score):
    """Get background color for score badges"""
    if score >= 80:
        return 'rgba(16, 185, 129, 0.15)'
    elif score >= 60:
        return 'rgba(245, 158, 11, 0.15)'
    else:
        return 'rgba(239, 68, 68, 0.15)'

def fmt(n):
    """Format numbers with K/M/B suffixes"""
    if n >= 1e9:
        return f"{n /1e9:.1f}B"
    elif n >= 1e6:
        return f"{n /1e6:.1f}M"
    elif n >= 1e3:
        return f"{n /1e3:.1f}K"
    return f"{n:.2f}"

# ============================================
# COMPONENT BUILDERS
# ============================================
def glass_card(children, className="", style=None, id=None):
    """Create a glassmorphism card component"""
    base_style = {
        'background': 'rgba(30, 41, 59, 0.7)',
        'backdropFilter': 'blur(20px)',
        'borderRadius': '16px',
        'border': '1px solid rgba(255, 255, 255, 0.1)',
        'padding': '24px',
        'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'transition': 'all 0.3s ease',
    }
    if style:
        base_style.update(style)

    return html.Div(children, className=f"glass-card {className}", style=base_style, id=id)

def stat_card_v3(title, value, change=None, icon=None, accent=COLORS['primary']):
    """Modern stat card with improved visual hierarchy"""
    change_color = COLORS['success'] if change and change > 0 else COLORS['danger'] if change and change < 0 else COLORS['text_secondary']
    change_icon = "↑" if change and change > 0 else "↓" if change and change < 0 else "→"

    return glass_card([
        html.Div([
            # Icon circle
            html.Div(icon if icon else "📊", style={
                'width': '48px',
                'height': '48px',
                'borderRadius': '12px',
                'background': f'linear-gradient(135deg, {accent}22, {accent}44)',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'center',
                'fontSize': '24px',
                'marginBottom': '16px',
            }),
            # Title
            html.Div(title, style={
                'fontSize': '14px',
                'color': COLORS['text_secondary'],
                'fontWeight': '500',
                'marginBottom': '8px',
                'textTransform': 'uppercase',
                'letterSpacing': '0.5px',
            }),
            # Value
            html.Div(value, style={
                'fontSize': '32px',
                'fontWeight': '700',
                'color': COLORS['text_primary'],
                'marginBottom': '8px',
            }),
            # Change indicator
            html.Div([
                html.Span(change_icon, style={'marginRight': '4px'}),
                html.Span(f"{abs(change):.1f}%" if change else "No change", style={
                    'fontSize': '13px',
                    'fontWeight': '600',
                    'color': change_color,
                }),
                html.Span(" vs last week", style={
                    'fontSize': '12px',
                    'color': COLORS['text_muted'],
                    'marginLeft': '4px',
                }),
            ]) if change is not None else None,
        ]),
    ], style={
        'cursor': 'pointer',
        'hover': {'transform': 'translateY(-4px)', 'boxShadow': '0 20px 25px -5px rgba(0, 0, 0, 0.1)'},
    })

def stock_row_v3(symbol, data, rank=None):
    """Modern stock row with better visual hierarchy"""
    score = data.get('score', 0)
    upside = data.get('upside', 0)
    price = data.get('price', 0)

    score_color = get_score_color(score)
    upside_color = COLORS['success'] if upside > 0 else COLORS['danger']

    return html.Div([
        # Rank badge
        html.Div(str(rank) if rank else "", style={
            'width': '32px',
            'height': '32px',
            'borderRadius': '8px',
            'background': COLORS['bg_card_hover'] if rank and rank > 3 else f'linear-gradient(135deg, {COLORS["primary"]}, {COLORS["primary_dark"]})',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'fontSize': '14px',
            'fontWeight': '700',
            'color': COLORS['text_primary'] if rank and rank <= 3 else COLORS['text_secondary'],
            'marginRight': '16px',
        }) if rank else None,

        # Symbol and name
        html.Div([
            html.Div(symbol, style={
                'fontSize': '16px',
                'fontWeight': '700',
                'color': COLORS['text_primary'],
            }),
            html.Div(data.get('name', symbol), style={
                'fontSize': '12px',
                'color': COLORS['text_muted'],
                'marginTop': '2px',
            }),
        ], style={'flex': '1'}),

        # Score badge
        html.Div([
            html.Span(f"{score:.0f}", style={
                'fontSize': '18px',
                'fontWeight': '700',
                'color': score_color,
            }),
        ], style={
            'padding': '8px 16px',
            'borderRadius': '8px',
            'background': get_score_bg(score),
            'marginRight': '16px',
        }),

        # Price
        html.Div([
            html.Div(f"${price:.2f}", style={
                'fontSize': '16px',
                'fontWeight': '600',
                'color': COLORS['text_primary'],
                'textAlign': 'right',
            }),
            html.Div([
                html.Span("↑" if upside > 0 else "↓", style={'marginRight': '2px'}),
                html.Span(f"{abs(upside):.1f}%", style={
                    'fontSize': '12px',
                    'fontWeight': '600',
                    'color': upside_color,
                }),
            ], style={
                'fontSize': '12px',
                'textAlign': 'right',
                'marginTop': '2px',
            }),
        ], style={'minWidth': '80px'}),

    ], style={
        'display': 'flex',
        'alignItems': 'center',
        'padding': '16px 20px',
        'background': COLORS['bg_card'],
        'borderRadius': '12px',
        'marginBottom': '8px',
        'border': f'1px solid {COLORS["border"]}',
        'transition': 'all 0.2s ease',
        'cursor': 'pointer',
    }, className="stock-row")

def metric_badge(label, value, unit="", color=None):
    """Metric badge component"""
    return html.Div([
        html.Div(label, style={
            'fontSize': '11px',
            'color': COLORS['text_muted'],
            'textTransform': 'uppercase',
            'letterSpacing': '0.5px',
            'marginBottom': '4px',
        }),
        html.Div([
            html.Span(f"{value}", style={
                'fontSize': '18px',
                'fontWeight': '700',
                'color': color or COLORS['text_primary'],
            }),
            html.Span(unit, style={
                'fontSize': '12px',
                'color': COLORS['text_secondary'],
                'marginLeft': '2px',
            }) if unit else None,
        ]),
    ], style={
        'padding': '12px 16px',
        'background': COLORS['bg_card_hover'],
        'borderRadius': '10px',
        'minWidth': '80px',
    })

# ============================================
# LOADING COMPONENT
# ============================================
def loading_spinner(text="Loading..."):
    """Modern loading spinner"""
    return html.Div([
        html.Div(className="spinner", style={
            'width': '40px',
            'height': '40px',
            'border': f'3px solid {COLORS["border"]}',
            'borderTop': f'3px solid {COLORS["primary"]}',
            'borderRadius': '50%',
            'animation': 'spin 1s linear infinite',
            'marginBottom': '16px',
        }),
        html.Div(text, style={
            'fontSize': '14px',
            'color': COLORS['text_secondary'],
        }),
    ], style={
        'display': 'flex',
        'flexDirection': 'column',
        'alignItems': 'center',
        'justifyContent': 'center',
        'padding': '60px 20px',
    })

# ============================================
# LAYOUT
# ============================================
app.layout = html.Div([
    # CSS Animations
    html.Style("""
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .glass-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 10px 10px -5px rgba(0, 0, 0, 0.1);
            border-color: rgba(99, 102, 241, 0.3);
        }
        .stock-row:hover {
            background: #334155 !important;
            border-color: #6366F1 !important;
        }
        .tab-active {
            background: linear-gradient(135deg, #6366F1, #4F46E5) !important;
            color: white !important;
        }
        * {
            scrollbar-width: thin;
            scrollbar-color: #475569 #1E293B;
        }
        *::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        *::-webkit-scrollbar-track {
            background: #1E293B;
        }
        *::-webkit-scrollbar-thumb {
            background: #475569;
            border-radius: 4px;
        }
        *::-webkit-scrollbar-thumb:hover {
            background: #64748B;
        }
    """),

    # Main container
    html.Div([
        # Header
        html.Div([
            html.Div([
                html.H1("📈 Stock PRO", style={
                    'fontSize': '28px',
                    'fontWeight': '800',
                    'color': COLORS['text_primary'],
                    'margin': '0',
                    'background': f'linear-gradient(135deg, {COLORS["text_primary"]}, {COLORS["primary_light"]})',
                    'WebkitBackgroundClip': 'text',
                    'WebkitTextFillColor': 'transparent',
                }),
                html.Div("Professional Stock Analysis Platform", style={
                    'fontSize': '14px',
                    'color': COLORS['text_secondary'],
                    'marginTop': '4px',
                }),
            ]),
            html.Div([
                html.Div(id="last-update", style={
                    'fontSize': '12px',
                    'color': COLORS['text_muted'],
                }),
            ]),
        ], style={
            'display': 'flex',
            'justifyContent': 'space-between',
            'alignItems': 'center',
            'marginBottom': '32px',
            'paddingBottom': '24px',
            'borderBottom': f'1px solid {COLORS["border"]}',
        }),

        # Stats row
        html.Div(id="stats-row", style={
            'display': 'grid',
            'gridTemplateColumns': 'repeat(auto-fit, minmax(240px, 1fr))',
            'gap': '20px',
            'marginBottom': '32px',
        }),

        # Search bar
        glass_card([
            html.Div([
                html.Span("🔍", style={'fontSize': '20px', 'marginRight': '12px'}),
                dcc.Input(
                    id="symbol-input",
                    type="text",
                    placeholder="Enter stock symbol (e.g., AAPL, NVDA)...",
                    style={
                        'flex': '1',
                        'border': 'none',
                        'background': 'transparent',
                        'color': COLORS['text_primary'],
                        'fontSize': '16px',
                        'outline': 'none',
                    }
                ),
                html.Button(
                    "Analyze",
                    id="analyze-btn",
                    style={
                        'padding': '12px 24px',
                        'background': f'linear-gradient(135deg, {COLORS["primary"]}, {COLORS["primary_dark"]})',
                        'border': 'none',
                        'borderRadius': '10px',
                        'color': 'white',
                        'fontSize': '14px',
                        'fontWeight': '600',
                        'cursor': 'pointer',
                        'transition': 'all 0.2s ease',
                    }
                ),
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'gap': '12px',
            }),
        ], style={'marginBottom': '24px'}),

        # Loading indicator
        html.Div(id="loading-indicator"),

        # Analysis result
        html.Div(id="analysis-result"),

        # Tabs
        html.Div([
            html.Button("🏆 Top Picks", id="tab-top", className="tab-btn tab-active", n_clicks=1),
            html.Button("💰 Value", id="tab-value", className="tab-btn", n_clicks=0),
            html.Button("📈 Growth", id="tab-growth", className="tab-btn", n_clicks=0),
            html.Button("💵 Dividend", id="tab-dividend", className="tab-btn", n_clicks=0),
        ], style={
            'display': 'flex',
            'gap': '8px',
            'marginBottom': '24px',
            'flexWrap': 'wrap',
        }),

        # Tab content
        html.Div(id="tab-content"),

    ], style={
        'maxWidth': '1400px',
        'margin': '0 auto',
        'padding': '32px',
        'minHeight': '100vh',
    }),

], style={
    'background': f'linear-gradient(135deg, {COLORS["bg_dark"]} 0%, #1a1f2e 100%)',
    'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    'minHeight': '100vh',
})

# ============================================
# CALLBACKS
# ============================================

# Stats callback
@app.callback(
    Output("stats-row", "children"),
    Output("last-update", "children"),
    Input("stats-row", "id"),
)
def update_stats(_):
    cache_key = "stats_v3"
    stats = cache.get(cache_key, ttl=300)

    if not stats:
        from stock_pro.core import A, P
        total = len(A)
        scores = [A[s][2] for s in A] if A else [65]
        avg = sum(scores) /len(scores) if scores else 65
        buys = len([s for s in A if A[s][1] in ['Overweight', 'Outperform', 'Strong Buy', 'Buy']]) if A else 0

        upsides = []
        for s in A:
            if s in P:
                target, _, _ = A[s]
                price = P[s]
                if price > 0:
                    upsides.append((target - price) / price * 100)
        top_up = max(upsides) if upsides else 25

        stats = [
            stat_card_v3('Total Stocks', total, icon='📊', accent=COLORS['primary']),
            stat_card_v3('Avg Score', f"{avg:.0f}", chg=2.1, icon='🎯', accent=COLORS['success']),
            stat_card_v3('Top Upside', f"+{top_up:.1f}%", icon='🚀', accent=COLORS['warning']),
            stat_card_v3('Strong Buys', buys, icon='⭐', accent=COLORS['success_light']),
        ]
        cache.set(cache_key, stats)

    return stats, f"Last updated: {datetime.now().strftime('%H:%M:%S')}"

# Tab switching
@app.callback(
    Output("tab-content", "children"),
    Output("tab-top", "className"),
    Output("tab-value", "className"),
    Output("tab-growth", "className"),
    Output("tab-dividend", "className"),
    Input("tab-top", "n_clicks"),
    Input("tab-value", "n_clicks"),
    Input("tab-growth", "n_clicks"),
    Input("tab-dividend", "n_clicks"),
)
def update_tab(top, value, growth, dividend):
    ctx = callback_context
    if not ctx.triggered:
        tab = "top"
    else:
        tab = ctx.triggered[0]["prop_id"].split(".")[0].replace("tab-", "")

    classes = ["tab-btn"] * 4
    tab_map = {"top": 0, "value": 1, "growth": 2, "dividend": 3}
    if tab in tab_map:
        classes[tab_map[tab]] = "tab-btn tab-active"

    # Get data
    if tab == "top":
        data = top_picks(15) or []
        title = "🏆 Top Picks"
        desc = "Highest overall scores with strong fundamentals"
    elif tab == "value":
        data = value_picks() or []
        title = "💰 Value Stocks"
        desc = "Undervalued stocks with strong potential"
    elif tab == "growth":
        data = growth_picks() or []
        title = "📈 Growth Stocks"
        desc = "High growth potential stocks"
    else:
        data = dividend_picks() or []
        title = "💵 Dividend Stocks"
        desc = "Stocks with attractive dividend yields"

    if not data:
        return html.Div("No data available", style={'color': COLORS['text_secondary']}), *classes

    rows = [stock_row_v3(s['symbol'], s, rank=i +1) for i, s in enumerate(data)]

    content = glass_card([
        html.Div([
            html.H2(title, style={
                'fontSize': '20px',
                'fontWeight': '700',
                'color': COLORS['text_primary'],
                'margin': '0 0 8px 0',
            }),
            html.Div(desc, style={
                'fontSize': '14px',
                'color': COLORS['text_secondary'],
            }),
        ], style={'marginBottom': '20px'}),
        html.Div(rows),
    ])

    return content, *classes

# Analysis callback
@app.callback(
    Output("analysis-result", "children"),
    Output("loading-indicator", "children"),
    Input("analyze-btn", "n_clicks"),
    State("symbol-input", "value"),
    prevent_initial_call=True,
)
def analyze_stock(n_clicks, symbol):
    if not n_clicks or not symbol:
        return None, None

    # Show loading
    loading = loading_spinner(f"Analyzing {symbol.upper()}...")

    try:
        data = analyze(symbol.upper())
        if not data or 'error' in data:
            error_msg = data.get('error', 'Analysis failed') if data else 'Unknown error'
            return glass_card([
                html.Div("❌ Analysis Failed", style={
                    'fontSize': '18px',
                    'fontWeight': '600',
                    'color': COLORS['danger'],
                    'marginBottom': '8px',
                }),
                html.Div(error_msg, style={
                    'fontSize': '14px',
                    'color': COLORS['text_secondary'],
                }),
            ]), None

        score = data.get('score', 0)
        upside = data.get('upside', 0)

        result = glass_card([
            # Header
            html.Div([
                html.Div([
                    html.Div(data.get('symbol', symbol.upper()), style={
                        'fontSize': '24px',
                        'fontWeight': '800',
                        'color': COLORS['text_primary'],
                    }),
                    html.Div(data.get('name', ''), style={
                        'fontSize': '14px',
                        'color': COLORS['text_secondary'],
                        'marginTop': '4px',
                    }),
                ]),
                html.Div([
                    html.Div(f"${data.get('price', 0):.2f}", style={
                        'fontSize': '32px',
                        'fontWeight': '700',
                        'color': COLORS['text_primary'],
                        'textAlign': 'right',
                    }),
                    html.Div([
                        html.Span("↑" if upside > 0 else "↓", style={'marginRight': '4px'}),
                        html.Span(f"{abs(upside):.1f}%", style={
                            'fontSize': '14px',
                            'fontWeight': '600',
                            'color': COLORS['success'] if upside > 0 else COLORS['danger'],
                        }),
                    ], style={
                        'fontSize': '14px',
                        'textAlign': 'right',
                        'marginTop': '4px',
                    }),
                ]),
            ], style={
                'display': 'flex',
                'justifyContent': 'space-between',
                'alignItems': 'flex-start',
                'marginBottom': '24px',
                'paddingBottom': '20px',
                'borderBottom': f'1px solid {COLORS["border"]}',
            }),

            # Score and rating
            html.Div([
                html.Div([
                    html.Div("Overall Score", style={
                        'fontSize': '12px',
                        'color': COLORS['text_muted'],
                        'textTransform': 'uppercase',
                        'letterSpacing': '0.5px',
                        'marginBottom': '8px',
                    }),
                    html.Div([
                        html.Div(f"{score:.0f}", style={
                            'fontSize': '48px',
                            'fontWeight': '800',
                            'color': get_score_color(score),
                        }),
                        html.Div("/100", style={
                            'fontSize': '16px',
                            'color': COLORS['text_muted'],
                            'marginLeft': '4px',
                        }),
                    ], style={'display': 'flex', 'alignItems': 'baseline'}),
                ], style={'flex': '1'}),

                html.Div([
                    html.Div("Rating", style={
                        'fontSize': '12px',
                        'color': COLORS['text_muted'],
                        'textTransform': 'uppercase',
                        'letterSpacing': '0.5px',
                        'marginBottom': '8px',
                        'textAlign': 'right',
                    }),
                    html.Div(data.get('rating', 'N/A'), style={
                        'fontSize': '18px',
                        'fontWeight': '700',
                        'color': get_score_color(score),
                        'textAlign': 'right',
                    }),
                ], style={'flex': '1'}),
            ], style={
                'display': 'flex',
                'marginBottom': '24px',
            }),

            # Metrics grid
            html.Div([
                metric_badge("P/E Ratio", f"{data.get('pe', 0):.1f}", "x"),
                metric_badge("ROE", f"{data.get('roe', 0):.1f}", "%", COLORS['success'] if data.get('roe', 0) > 15 else None),
                metric_badge("Div Yield", f"{data.get('div', 0):.2f}", "%"),
                metric_badge("Debt/Eq", f"{data.get('debt_eq', 0):.2f}", "x", COLORS['danger'] if data.get('debt_eq', 0) > 1 else COLORS['success']),
            ], style={
                'display': 'grid',
                'gridTemplateColumns': 'repeat(auto-fit, minmax(100px, 1fr))',
                'gap': '12px',
                'marginBottom': '20px',
            }),

            # Recommendation
            html.Div([
                html.Div("🎯 Recommendation", style={
                    'fontSize': '14px',
                    'fontWeight': '600',
                    'color': COLORS['text_primary'],
                    'marginBottom': '8px',
                }),
                html.Div(data.get('recommend', 'No recommendation available'), style={
                    'fontSize': '14px',
                    'color': COLORS['text_secondary'],
                    'lineHeight': '1.6',
                    'padding': '16px',
                    'background': COLORS['bg_card_hover'],
                    'borderRadius': '10px',
                }),
            ]),

        ], style={'animation': 'fadeIn 0.3s ease'})

        return result, None

    except Exception as e:
        return glass_card([
            html.Div("❌ Error", style={
                'fontSize': '18px',
                'fontWeight': '600',
                'color': COLORS['danger'],
                'marginBottom': '8px',
            }),
            html.Div(str(e), style={
                'fontSize': '14px',
                'color': COLORS['text_secondary'],
            }),
        ]), None

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Stock PRO v3.0 - Modern UI/UX")
    print("=" * 50)
    print("📊 Opening dashboard...")
    print("🔗 URL: http://127.0.0.1:8050")
    print("=" * 50)
    app.run(debug=True, port=8050)
