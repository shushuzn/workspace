"""
Stock PRO UI Components v3.0
Reusable UI components for modern stock analysis dashboard
"""
import plotly.graph_objects as go
import plotly.express as px
from dash import html, dcc

# ============================================
# COLOR SYSTEM
# ============================================
COLORS = {
    # Primary
    'primary': '#6366F1',
    'primary_dark': '#4F46E5',
    'primary_light': '#818CF8',

    # Semantic
    'success': '#10B981',
    'warning': '#F59E0B',
    'danger': '#EF4444',

    # Neutral - Dark Theme
    'bg_dark': '#0F172A',
    'bg_card': '#1E293B',
    'bg_card_hover': '#334155',
    'text_primary': '#F8FAFC',
    'text_secondary': '#94A3B8',
    'text_muted': '#64748B',
    'border': '#334155',
}

# ============================================
# CHART COMPONENTS
# ============================================
def create_sparkline(data, title="", color=COLORS['primary'], height=60):
    """Create a minimal sparkline chart"""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=list(range(len(data))),
        y=data,
        mode='lines',
        line=dict(color=color, width=2),
        fill='tozeroy',
        fillcolor=f'rgba(99, 102, 241, 0.1)',
        hoverinfo='skip',
    ))

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        height=height,
        showlegend=False,
    )

    return fig

def create_gauge_chart(value, title="Score", max_val=100):
    """Create a modern gauge chart for scores"""
    color = COLORS['success'] if value >= 80 else COLORS['warning'] if value >= 60 else COLORS['danger']

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={'font': {'size': 36, 'color': COLORS['text_primary'], 'family': 'Arial Black'}},
        title={'text': title, 'font': {'size': 14, 'color': COLORS['text_secondary']}},
        gauge={
            'axis': {'range': [0, max_val], 'tickwidth': 0, 'showticklabels': False},
            'bar': {'color': color, 'thickness': 0.75},
            'bgcolor': COLORS['bg_card_hover'],
            'borderwidth': 0,
            'steps': [
                {'range': [0, 60], 'color': 'rgba(239, 68, 68, 0.2)'},
                {'range': [60, 80], 'color': 'rgba(245, 158, 11, 0.2)'},
                {'range': [80, 100], 'color': 'rgba(16, 185, 129, 0.2)'},
            ],
            'threshold': {
                'line': {'color': COLORS['text_muted'], 'width': 2},
                'thickness': 0.8,
                'value': value
            }
        }
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=40, b=20),
        height=200,
    )

    return fig

def create_bar_chart(categories, values, title="", orientation='h'):
    """Create a modern bar chart"""
    colors = [COLORS['success'] if v > 70 else COLORS['warning'] if v > 50 else COLORS['danger'] for v in values]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=categories if orientation == 'h' else None,
        x=values if orientation == 'h' else categories,
        orientation=orientation,
        marker=dict(
            color=colors,
            line=dict(color='rgba(0,0,0,0)', width=0),
            cornerRadius=4 if orientation == 'h' else 0,
        ),
        text=[f'{v:.0f}' for v in values],
        textposition='outside',
        textfont=dict(color=COLORS['text_secondary'], size=12),
    ))

    fig.update_layout(
        title=dict(text=title, font=dict(color=COLORS['text_primary'], size=16)),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=80, r=40, t=60, b=40),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            tickfont=dict(color=COLORS['text_secondary']),
            zeroline=False,
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(color=COLORS['text_secondary']),
            zeroline=False,
        ),
        showlegend=False,
        bargap=0.3,
    )

    return fig

def create_donut_chart(labels, values, title="", hole=0.6):
    """Create a modern donut chart"""
    colors = [COLORS['primary'], COLORS['success'], COLORS['warning'], COLORS['danger'], COLORS['primary_light']]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=hole,
        marker=dict(colors=colors, line=dict(color=COLORS['bg_card'], width=2)),
        textinfo='label+percent',
        textfont=dict(color=COLORS['text_primary'], size=12),
        hovertemplate='%{label}<br>%{value}<br>%{percent}<extra></extra>',
    ))

    fig.update_layout(
        title=dict(text=title, font=dict(color=COLORS['text_primary'], size=16)),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=60, b=20),
        showlegend=False,
        annotations=[dict(
            text=f'{sum(values)}',
            x=0.5, y=0.5,
            font=dict(size=24, color=COLORS['text_primary'], family='Arial Black'),
            showarrow=False,
        )],
    )

    return fig

def create_line_chart(dates, prices, symbol="", show_volume=False):
    """Create a modern stock price line chart"""
    fig = go.Figure()

    # Price line
    fig.add_trace(go.Scatter(
        x=dates,
        y=prices,
        mode='lines',
        name='Price',
        line=dict(color=COLORS['primary'], width=2),
        fill='tozeroy',
        fillcolor='rgba(99, 102, 241, 0.1)',
    ))

    # Add moving average
    if len(prices) >= 20:
        ma20 = [sum(prices[max(0, i -19):i +1]) /min(20, i +1) for i in range(len(prices))]
        fig.add_trace(go.Scatter(
            x=dates,
            y=ma20,
            mode='lines',
            name='MA20',
            line=dict(color=COLORS['warning'], width=1.5, dash='dash'),
        ))

    fig.update_layout(
        title=dict(text=f"{symbol} Price Chart", font=dict(color=COLORS['text_primary'], size=18)),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=60, r=40, t=60, b=40),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            tickfont=dict(color=COLORS['text_secondary']),
            zeroline=False,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.05)',
            tickfont=dict(color=COLORS['text_secondary']),
            tickprefix='$',
            zeroline=False,
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(color=COLORS['text_secondary']),
            bgcolor='rgba(0,0,0,0)',
        ),
        hovermode='x unified',
    )

    return fig

# ============================================
# UI COMPONENTS
# ============================================
def progress_bar(value, max_val=100, color=None, height=8, show_label=True):
    """Create a modern progress bar"""
    if color is None:
        color = COLORS['success'] if value >= 80 else COLORS['warning'] if value >= 60 else COLORS['danger']

    percentage = (value / max_val) * 100

    return html.Div([
        html.Div(style={
            'width': '100%',
            'height': f'{height}px',
            'background': COLORS['bg_card_hover'],
            'borderRadius': f'{height //2}px',
            'overflow': 'hidden',
        }, children=[
            html.Div(style={
                'width': f'{percentage}%',
                'height': '100%',
                'background': f'linear-gradient(90deg, {color}, {color}aa)',
                'borderRadius': f'{height //2}px',
                'transition': 'width 0.5s ease',
            })
        ]),
        html.Div(f"{value:.0f}/{max_val}", style={
            'fontSize': '11px',
            'color': COLORS['text_muted'],
            'marginTop': '4px',
            'textAlign': 'right',
        }) if show_label else None,
    ])

def badge(text, color=None, size="md"):
    """Create a modern badge"""
    if color is None:
        color = COLORS['primary']

    sizes = {
        "sm": {'padding': '2px 8px', 'fontSize': '11px'},
        "md": {'padding': '4px 12px', 'fontSize': '12px'},
        "lg": {'padding': '6px 16px', 'fontSize': '14px'},
    }

    return html.Span(text, style={
        'display': 'inline-block',
        'background': f'{color}22',
        'color': color,
        'borderRadius': '6px',
        'fontWeight': '600',
        'textTransform': 'uppercase',
        'letterSpacing': '0.5px',
        **sizes.get(size, sizes["md"]),
    })

def tooltip(text, children, position="top"):
    """Create a tooltip wrapper"""
    positions = {
        "top": {'bottom': '100%', 'left': '50%', 'transform': 'translateX(-50%)', 'marginBottom': '8px'},
        "bottom": {'top': '100%', 'left': '50%', 'transform': 'translateX(-50%)', 'marginTop': '8px'},
        "left": {'right': '100%', 'top': '50%', 'transform': 'translateY(-50%)', 'marginRight': '8px'},
        "right": {'left': '100%', 'top': '50%', 'transform': 'translateY(-50%)', 'marginLeft': '8px'},
    }

    return html.Div([
        children,
        html.Div(text, style={
            'position': 'absolute',
            'background': COLORS['bg_card_hover'],
            'color': COLORS['text_primary'],
            'padding': '8px 12px',
            'borderRadius': '6px',
            'fontSize': '12px',
            'whiteSpace': 'nowrap',
            'zIndex': '1000',
            'opacity': '0',
            'visibility': 'hidden',
            'transition': 'all 0.2s ease',
            'boxShadow': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
            **positions.get(position, positions["top"]),
        }, className="tooltip-content"),
    ], style={
        'position': 'relative',
        'display': 'inline-block',
    }, className="tooltip-wrapper")

def alert(message, type_="info", dismissible=True):
    """Create an alert component"""
    colors = {
        "info": COLORS['primary'],
        "success": COLORS['success'],
        "warning": COLORS['warning'],
        "error": COLORS['danger'],
    }

    icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
    }

    color = colors.get(type_, COLORS['primary'])

    return html.Div([
        html.Span(icons.get(type_, "ℹ️"), style={'marginRight': '12px', 'fontSize': '18px'}),
        html.Span(message, style={'flex': '1'}),
        html.Button("×", style={
            'background': 'none',
            'border': 'none',
            'color': COLORS['text_secondary'],
            'fontSize': '20px',
            'cursor': 'pointer',
            'padding': '0',
            'marginLeft': '12px',
        }) if dismissible else None,
    ], style={
        'display': 'flex',
        'alignItems': 'center',
        'padding': '16px 20px',
        'background': f'{color}15',
        'border': f'1px solid {color}33',
        'borderRadius': '10px',
        'color': color,
        'fontSize': '14px',
    })

def skeleton_loader(height=100, count=1):
    """Create skeleton loading placeholder"""
    items = []
    for i in range(count):
        items.append(html.Div(style={
            'width': '100%',
            'height': f'{height}px',
            'background': f'linear-gradient(90deg, {COLORS["bg_card"]} 25%, {COLORS["bg_card_hover"]} 50%, {COLORS["bg_card"]} 75%)',
            'backgroundSize': '200% 100%',
            'animation': 'shimmer 1.5s infinite',
            'borderRadius': '8px',
            'marginBottom': '12px',
        }))

    return html.Div(items, style={
        'width': '100%',
    })

# ============================================
# ANIMATION CSS
# ============================================
ANIMATION_CSS = """
@keyframes shimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateX(-20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

.tooltip-wrapper:hover .tooltip-content {
    opacity: 1 !important;
    visibility: visible !important;
}

.animate-fadeInUp {
    animation: fadeInUp 0.4s ease forwards;
}

.animate-slideIn {
    animation: slideIn 0.3s ease forwards;
}
"""

# ============================================
# UTILITY FUNCTIONS
# ============================================
def format_number(n, decimals=2):
    """Format large numbers with K/M/B suffixes"""
    if n is None:
        return "N/A"
    if abs(n) >= 1e12:
        return f"${n /1e12:.{decimals}f}T"
    elif abs(n) >= 1e9:
        return f"${n /1e9:.{decimals}f}B"
    elif abs(n) >= 1e6:
        return f"${n /1e6:.{decimals}f}M"
    elif abs(n) >= 1e3:
        return f"${n /1e3:.{decimals}f}K"
    return f"${n:.{decimals}f}"

def format_percentage(n, decimals=1, signed=True):
    """Format percentage with sign"""
    if n is None:
        return "N/A"
    sign = "+" if signed and n > 0 else ""
    return f"{sign}{n:.{decimals}f}%"

def get_trend_indicator(current, previous):
    """Get trend indicator based on current vs previous value"""
    if current > previous:
        return "↑", COLORS['success']
    elif current < previous:
        return "↓", COLORS['danger']
    return "→", COLORS['text_muted']
