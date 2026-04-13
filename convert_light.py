import os
import re

filepath = "streamlit_app.py"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace CSS variables
replacements = {
    "--bg-primary:    #020817;": "--bg-primary:    #f8fafc;",
    "--bg-secondary:  #0a1628;": "--bg-secondary:  #f1f5f9;",
    "--bg-card:       rgba(10, 22, 40, 0.85);": "--bg-card:       rgba(255, 255, 255, 0.85);",
    "--bg-glass:      rgba(15, 28, 55, 0.6);": "--bg-glass:      rgba(255, 255, 255, 0.6);",
    "--text-primary:  #f1f5f9;": "--text-primary:  #0f172a;",
    "--text-secondary:#94a3b8;": "--text-secondary:#475569;",
    "--text-muted:    #475569;": "--text-muted:    #64748b;",
    "rgba(148, 163, 184, 0.07);": "rgba(0, 0, 0, 0.07);", # border-subtle
    
    # Grid Background
    "linear-gradient(180deg, #020817 0%, #030d1f 100%) !important;": "linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%) !important;",
    
    # Hero wrapper
    "rgba(2, 8, 23, 0.95) 0%": "rgba(255, 255, 255, 0.95) 0%",
    "rgba(10, 22, 40, 0.98) 40%": "rgba(248, 250, 252, 0.98) 40%",
    "rgba(15, 28, 65, 0.95) 70%": "rgba(241, 245, 249, 0.95) 70%",
    "rgba(2, 8, 23, 0.95) 100%": "rgba(255, 255, 255, 0.95) 100%",
    
    # Hero title gradient text
    "linear-gradient(135deg, #f8fafc 0%, #93c5fd 30%, #c4b5fd 60%, #f8fafc 100%)": "linear-gradient(135deg, #0f172a 0%, #3b82f6 30%, #8b5cf6 60%, #0f172a 100%)",

    # Tabs Background
    "rgba(10, 22, 40, 0.7)": "rgba(255, 255, 255, 0.7)",

    # stMetric Background
    "rgba(15, 28, 55, 0.8) 0%": "rgba(255, 255, 255, 0.8) 0%",
    "rgba(8, 16, 35, 0.9) 100%": "rgba(248, 250, 252, 0.9) 100%",

    # Glass Card Background
    "rgba(15, 28, 55, 0.7) 0%": "rgba(255, 255, 255, 0.7) 0%",
    "rgba(8, 16, 35, 0.85) 100%": "rgba(248, 250, 252, 0.85) 100%",

    # Input and Select background
    "rgba(10, 22, 40, 0.8)": "rgba(255, 255, 255, 0.8)",

    # Expander
    "background: rgba(10, 22, 40, 0.5) !important;": "background: rgba(255, 255, 255, 0.5) !important;",
    "background: rgba(15, 28, 55, 0.6) !important;": "background: rgba(248, 250, 252, 0.6) !important;",

    # Chart Wrapper
    "rgba(10, 22, 40, 0.6)": "rgba(255, 255, 255, 0.6)",
    "rgba(5, 12, 25, 0.8)": "rgba(248, 250, 252, 0.8)",

    # PLOTLY_LAYOUT
    'template="plotly_dark"': 'template="plotly_white"',
    'paper_bgcolor="rgba(0, 0, 0, 0)"': 'paper_bgcolor="rgba(255, 255, 255, 0)"',
    'plot_bgcolor="rgba(0, 0, 0, 0)"': 'plot_bgcolor="rgba(255, 255, 255, 0)"',
    'color="#94a3b8"': 'color="#475569"',
    'color="#e2e8f0"': 'color="#0f172a"',
    'gridcolor="rgba(148, 163, 184, 0.05)"': 'gridcolor="rgba(0, 0, 0, 0.05)"',
    'zerolinecolor="rgba(148, 163, 184, 0.08)"': 'zerolinecolor="rgba(0, 0, 0, 0.08)"',
    'linecolor="rgba(148, 163, 184, 0.08)"': 'linecolor="rgba(0, 0, 0, 0.08)"',
    'bgcolor="rgba(10, 22, 40, 0.95)"': 'bgcolor="rgba(255, 255, 255, 0.95)"',
    'bgcolor="rgba(5, 12, 25, 0.7)"': 'bgcolor="rgba(255, 255, 255, 0.7)"',
}

for k, v in replacements.items():
    content = content.replace(k, v)

# Heatmap
content = content.replace('[0.0,  "#020817"]', '[0.0,  "#f8fafc"]')
content = content.replace('[0.15, "#0f172a"]', '[0.15, "#e2e8f0"]')
content = content.replace('[0.35, "#1e3a5f"]', '[0.35, "#cbd5e1"]')

# Colors inside dicts (specifically for line/border in Plotly objects)
content = re.sub(r'color="rgba\(255,255,255,\s*0\.7\)"', 'color="rgba(0,0,0,0.7)"', content)
content = re.sub(r'color="rgba\(255,255,255,\s*0\.04\)"', 'color="rgba(0,0,0,0.04)"', content)
content = re.sub(r'color="rgba\(255,255,255,\s*0\.05\)"', 'color="rgba(0,0,0,0.05)"', content)
content = re.sub(r'color="rgba\(255,255,255,\s*0\.06\)"', 'color="rgba(0,0,0,0.06)"', content)
content = re.sub(r'color="#020817"', 'color="#f8fafc"', content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("done")
