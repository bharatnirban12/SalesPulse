import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import yaml
import requests

API_BASE_URL = "https://sales-pulse-api.onrender.com/api"

# ──────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────
st.set_page_config(
    page_title="SalesPulse • Smart Sales Forecasting Platform ",
    page_icon=" ",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# PREMIUM CSS — System design

st.markdown("""
<style>
    /* ─── Font Stack ─── */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@200;300;400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

    /* ─── Root Variables ─── */
    :root {
        --bg-primary:    #f8fafc;
        --bg-secondary:  #f1f5f9;
        --bg-card:       rgba(255, 255, 255, 0.85);
        --bg-glass:      rgba(240, 244, 250, 0.6);
        --accent-blue:   #3b82f6;
        --accent-violet: #8b5cf6;
        --accent-pink:   #ec4899;
        --accent-cyan:   #06b6d4;
        --accent-emerald:#10b981;
        --text-primary:  #0f172a;
        --text-secondary:#334155;
        --text-muted:    #64748b;
        --border-subtle: rgba(0, 0, 0, 0.07);
        --border-glow:   rgba(59, 130, 246, 0.25);
        --glow-blue:     0 0 40px rgba(59, 130, 246, 0.15);
        --glow-violet:   0 0 40px rgba(139, 92, 246, 0.15);
        --glow-pink:     0 0 40px rgba(236, 72, 153, 0.12);
        --radius-sm:     8px;
        --radius-md:     14px;
        --radius-lg:     20px;
        --radius-xl:     28px;
    }

    /* ─── Global Reset ─── */
    html, body, [class*="css"] {
        font-family: 'Inter', 'Outfit', sans-serif !important;
        background-color: var(--bg-primary) !important;
    }

    /* ─── Hide Streamlit Chrome ─── */
    [data-testid="collapsedControl"],
    #MainMenu, footer, header { display: none !important; }

    /* ─── Main Container ─── */
    .main .block-container {
        padding: 0 2rem 3rem 2rem !important;
        max-width: 1600px !important;
    }

    /* ─── Animated Background Grid ─── */
    .main {
        background:
            radial-gradient(ellipse 80% 50% at 50% -10%, rgba(59,130,246,0.12) 0%, transparent 60%),
            radial-gradient(ellipse 60% 40% at 90% 80%, rgba(139,92,246,0.08) 0%, transparent 50%),
            radial-gradient(ellipse 50% 60% at -5% 50%, rgba(6,182,212,0.06) 0%, transparent 50%),
            linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%) !important;
        min-height: 100vh;
    }

    /* ═══════════════════════════════════════
       ANIMATED HERO
    ═══════════════════════════════════════ */
    @keyframes gradientShift {
        0%   { background-position: 0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50%       { transform: translateY(-8px); }
    }
    @keyframes pulse-ring {
        0%   { box-shadow: 0 0 0 0 rgba(59,130,246,0.4); }
        70%  { box-shadow: 0 0 0 20px rgba(59,130,246,0); }
        100% { box-shadow: 0 0 0 0 rgba(59,130,246,0); }
    }
    @keyframes shimmer {
        0%   { background-position: -200% center; }
        100% { background-position: 200% center; }
    }
    @keyframes fadeSlideUp {
        0%   { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    @keyframes scanline {
        0%   { transform: translateY(-100%); opacity: 0; }
        10%  { opacity: 1; }
        90%  { opacity: 1; }
        100% { transform: translateY(400px); opacity: 0; }
    }
    @keyframes orb-float {
        0%, 100% { transform: translate(0, 0) scale(1); }
        33%       { transform: translate(30px, -20px) scale(1.05); }
        66%       { transform: translate(-20px, 15px) scale(0.97); }
    }

    .hero-wrapper {
        position: relative;
        overflow: hidden;
        background: linear-gradient(135deg,
            rgba(255, 255, 255, 0.95) 0%,
            rgba(248, 250, 252, 0.98) 40%,
            rgba(240, 244, 250, 0.95) 70%,
            rgba(255, 255, 255, 0.95) 100%
        );
        border: 1px solid rgba(59, 130, 246, 0.15);
        border-radius: var(--radius-xl);
        padding: 3rem 3.5rem 2.8rem;
        margin: 1.2rem 0 2rem;
        box-shadow:
            0 0 0 1px rgba(59, 130, 246, 0.05),
            0 4px 6px rgba(0,0,0,0.3),
            0 20px 60px rgba(0,0,0,0.5),
            inset 0 1px 0 rgba(255,255,255,0.04);
        animation: fadeSlideUp 0.7s ease both;
    }

    /* Orb decorations */
    .hero-orb-1, .hero-orb-2, .hero-orb-3 {
        position: absolute;
        border-radius: 50%;
        filter: blur(60px);
        pointer-events: none;
    }
    .hero-orb-1 {
        width: 350px; height: 350px;
        background: radial-gradient(circle, rgba(59,130,246,0.18) 0%, transparent 70%);
        top: -100px; right: -50px;
        animation: orb-float 8s ease-in-out infinite;
    }
    .hero-orb-2 {
        width: 250px; height: 250px;
        background: radial-gradient(circle, rgba(139,92,246,0.15) 0%, transparent 70%);
        bottom: -80px; left: 20%;
        animation: orb-float 11s ease-in-out infinite reverse;
    }
    .hero-orb-3 {
        width: 180px; height: 180px;
        background: radial-gradient(circle, rgba(6,182,212,0.12) 0%, transparent 70%);
        top: 10px; left: -40px;
        animation: orb-float 7s ease-in-out infinite 2s;
    }

    /* Scanline effect */
    .hero-scanline {
        position: absolute;
        left: 0; right: 0; top: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(59,130,246,0.4), transparent);
        animation: scanline 4s ease-in-out infinite 1s;
        pointer-events: none;
    }

    .hero-content { position: relative; z-index: 2; }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(59,130,246,0.1);
        border: 1px solid rgba(59,130,246,0.3);
        border-radius: 100px;
        padding: 6px 16px 6px 10px;
        font-size: 0.75rem;
        font-weight: 600;
        color: #60a5fa;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 1.2rem;
        font-family: 'JetBrains Mono', monospace;
    }
    .hero-badge .dot {
        width: 6px; height: 6px;
        background: #22c55e;
        border-radius: 50%;
        animation: pulse-ring 2s infinite;
        box-shadow: 0 0 6px #22c55e;
    }

    .hero-title {
        font-family: 'Outfit', sans-serif !important;
        font-size: 3.6rem !important;
        font-weight: 800 !important;
        line-height: 1.05 !important;
        letter-spacing: -2px !important;
        margin-bottom: 1rem !important;
    }
    .hero-title .gradient-text {
        background: linear-gradient(135deg, #0f172a 0%, #3b82f6 30%, #8b5cf6 60%, #0f172a 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 4s linear infinite;
    }
    .hero-title .accent-text {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .hero-subtitle {
        color: var(--text-secondary);
        font-size: 1.05rem;
        font-weight: 400;
        max-width: 560px;
        line-height: 1.7;
        margin-bottom: 2rem;
    }

    .hero-stats {
        display: flex;
        gap: 2.5rem;
        flex-wrap: wrap;
    }
    .hero-stat {
        display: flex;
        flex-direction: column;
        gap: 2px;
    }
    .hero-stat-value {
        font-family: 'Outfit', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
    }
    .hero-stat-label {
        font-size: 0.72rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-weight: 500;
    }

    .hero-divider {
        width: 1px;
        height: 40px;
        background: var(--border-subtle);
        align-self: center;
    }

    /* ═══════════════════════════════════════
       TABS
    ═══════════════════════════════════════ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(20px);
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        padding: 5px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        border-radius: 10px;
        font-weight: 500;
        font-size: 0.875rem;
        padding: 0 22px;
        background-color: transparent;
        border: 1px solid transparent;
        color: var(--text-secondary) !important;
        transition: all 0.2s ease;
        font-family: 'Inter', sans-serif;
        letter-spacing: 0.2px;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(59, 130, 246, 0.08) !important;
        color: #93c5fd !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(59,130,246,0.2), rgba(139,92,246,0.2)) !important;
        border: 1px solid rgba(99,130,246,0.35) !important;
        color: white !important;
        box-shadow: 0 2px 12px rgba(59,130,246,0.2), inset 0 1px 0 rgba(255,255,255,0.06) !important;
    }

    /* ═══════════════════════════════════════
       KPI CARDS
    ═══════════════════════════════════════ */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg,
            rgba(255, 255, 255, 0.8) 0%,
            rgba(248, 250, 252, 0.9) 100%
        ) !important;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(59, 130, 246, 0.12) !important;
        border-radius: var(--radius-lg) !important;
        padding: 1.5rem 1.6rem !important;
        position: relative;
        overflow: hidden;
        box-shadow:
            0 4px 24px rgba(0,0,0,0.3),
            inset 0 1px 0 rgba(255,255,255,0.04);
        transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease !important;
        animation: fadeSlideUp 0.5s ease both;
    }
    [data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(59,130,246,0.5), rgba(139,92,246,0.5), transparent);
        border-radius: 2px 2px 0 0;
    }
    [data-testid="stMetric"]::after {
        content: '';
        position: absolute;
        bottom: 0; right: 0;
        width: 80px; height: 80px;
        background: radial-gradient(circle, rgba(59,130,246,0.07) 0%, transparent 70%);
        border-radius: 50%;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-3px) !important;
        border-color: rgba(59,130,246,0.3) !important;
        box-shadow:
            0 12px 40px rgba(0,0,0,0.4),
            0 0 0 1px rgba(59,130,246,0.15),
            inset 0 1px 0 rgba(255,255,255,0.06) !important;
    }
    [data-testid="stMetric"] label {
        color: var(--text-muted) !important;
        font-weight: 600 !important;
        font-size: 0.7rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1.2px !important;
        font-family: 'Inter', sans-serif !important;
    }
    [data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
        font-family: 'Outfit', sans-serif !important;
        letter-spacing: -0.5px !important;
    }
    [data-testid="stMetricDelta"] {
        font-size: 0.78rem !important;
        font-weight: 500 !important;
    }

    /* ═══════════════════════════════════════
       GLASS CARDS
    ═══════════════════════════════════════ */
    .glass-card {
        background: linear-gradient(135deg,
            rgba(255, 255, 255, 0.7) 0%,
            rgba(248, 250, 252, 0.85) 100%
        );
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(59, 130, 246, 0.1);
        border-radius: var(--radius-lg);
        padding: 1.8rem;
        margin-bottom: 1.2rem;
        position: relative;
        overflow: hidden;
        box-shadow:
            0 4px 24px rgba(0,0,0,0.25),
            inset 0 1px 0 rgba(255,255,255,0.03);
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }
    .glass-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent);
    }
    .glass-card:hover {
        border-color: rgba(59, 130, 246, 0.2);
        box-shadow: 0 8px 40px rgba(0,0,0,0.3), var(--glow-blue);
    }

    /* ═══════════════════════════════════════
       SECTION HEADERS
    ═══════════════════════════════════════ */
    .section-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 2rem 0 1rem;
    }
    .section-header-line {
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, rgba(59,130,246,0.3), transparent);
    }
    .section-header-title {
        font-family: 'Outfit', sans-serif;
        font-size: 0.8rem;
        font-weight: 700;
        color: #60a5fa;
        text-transform: uppercase;
        letter-spacing: 2px;
        white-space: nowrap;
    }
    .section-header-icon {
        font-size: 1rem;
    }

    /* ═══════════════════════════════════════
       BUTTON
    ═══════════════════════════════════════ */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb, #6d28d9) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.3px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 20px rgba(37, 99, 235, 0.4) !important;
        font-family: 'Inter', sans-serif !important;
        position: relative;
        overflow: hidden;
    }
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 100%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        transition: left 0.4s ease;
    }
    .stButton > button:hover::before { left: 100%; }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(37, 99, 235, 0.6) !important;
    }

    /* ═══════════════════════════════════════
       DOWNLOAD BUTTON
    ═══════════════════════════════════════ */
    .stDownloadButton > button {
        background: rgba(16, 185, 129, 0.12) !important;
        border: 1px solid rgba(16,185,129,0.3) !important;
        color: #34d399 !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    .stDownloadButton > button:hover {
        background: rgba(16,185,129,0.22) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 20px rgba(16,185,129,0.2) !important;
    }

    /* ═══════════════════════════════════════
       SELECT BOXES & INPUTS
    ═══════════════════════════════════════ */
    [data-baseweb="select"] > div,
    [data-baseweb="input"] > div {
        background: rgba(255, 255, 255, 0.8) !important;
        border: 1px solid rgba(59,130,246,0.15) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }
    [data-baseweb="select"] > div:focus-within,
    [data-baseweb="input"] > div:focus-within {
        border-color: rgba(59,130,246,0.4) !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.1) !important;
    }

    /* ─── Slider ─── */
    [data-testid="stSlider"] > div > div > div {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important;
    }

    /* ─── Expander ─── */
    [data-testid="stExpander"] {
        border: 1px solid rgba(59, 130, 246, 0.12) !important;
        border-radius: var(--radius-md) !important;
        background: rgba(255, 255, 255, 0.5) !important;
        overflow: hidden;
    }
    .streamlit-expanderHeader {
        background: rgba(248, 250, 252, 0.6) !important;
        font-weight: 600 !important;
        color: var(--text-secondary) !important;
        font-size: 0.88rem !important;
        padding: 0.9rem 1.2rem !important;
    }
    .streamlit-expanderHeader:hover {
        background: rgba(59, 130, 246, 0.08) !important;
        color: var(--text-primary) !important;
    }

    /* ─── DataFrame ─── */
    [data-testid="stDataFrame"] {
        border-radius: var(--radius-md) !important;
        overflow: hidden;
        border: 1px solid rgba(59, 130, 246, 0.1) !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }

    /* ─── HR Divider ─── */
    hr {
        border: none !important;
        border-top: 1px solid rgba(148, 163, 184, 0.06) !important;
        margin: 2rem 0 !important;
    }

    /* ═══════════════════════════════════════
       MODEL BADGE
    ═══════════════════════════════════════ */
    .model-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 18px;
        border-radius: 100px;
        font-size: 0.82rem;
        font-weight: 600;
        letter-spacing: 0.3px;
        font-family: 'Inter', sans-serif;
        margin-top: 0.8rem;
        margin-bottom: 0.5rem;
    }

    /* ═══════════════════════════════════════
       STATUS BADGES
    ═══════════════════════════════════════ */
    .status-live {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(34, 197, 94, 0.1);
        border: 1px solid rgba(34, 197, 94, 0.3);
        border-radius: 100px;
        padding: 4px 12px;
        font-size: 0.72rem;
        font-weight: 700;
        color: #4ade80;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .status-live::before {
        content: '';
        display: inline-block;
        width: 6px; height: 6px;
        background: #22c55e;
        border-radius: 50%;
        box-shadow: 0 0 8px #22c55e;
        animation: pulse-ring 2s infinite;
    }

    /* ═══════════════════════════════════════
       CHART WRAPPER
    ═══════════════════════════════════════ */
    .chart-wrapper {
        background: linear-gradient(135deg,
            rgba(255, 255, 255, 0.6),
            rgba(240, 244, 250, 0.8)
        );
        border: 1px solid rgba(59, 130, 246, 0.08);
        border-radius: var(--radius-lg);
        padding: 0.5rem;
        overflow: hidden;
        box-shadow: 0 4px 24px rgba(0,0,0,0.2);
        transition: border-color 0.3s ease;
    }
    .chart-wrapper:hover {
        border-color: rgba(59, 130, 246, 0.18);
    }

    /* ═══════════════════════════════════════
       INFO / WARNING BOXES
    ═══════════════════════════════════════ */
    [data-testid="stAlert"] {
        border-radius: var(--radius-md) !important;
        border: 1px solid rgba(59,130,246,0.15) !important;
        background: rgba(59,130,246,0.05) !important;
    }

    /* ═══════════════════════════════════════
       ROUTING PIPELINE
    ═══════════════════════════════════════ */
    .pipeline-node {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 6px;
    }
    .pipeline-icon {
        font-size: 1.5rem;
    }
    .pipeline-label {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: var(--text-muted);
    }

    /* ═══════════════════════════════════════
       FOOTER
    ═══════════════════════════════════════ */
    .footer-wrap {
        border-top: 1px solid rgba(148,163,184,0.06);
        padding: 1.8rem 0 0.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 1rem;
        margin-top: 3rem;
    }
    .footer-brand {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        font-size: 1rem;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .footer-copy {
        font-size: 0.75rem;
        color: var(--text-muted);
    }

    /* Smooth fade for all elements */
    .element-container {
        animation: fadeSlideUp 0.4s ease both;
    }

    /* ─── Staggered metric animations ─── */
    .row-widget:nth-child(1) [data-testid="stMetric"] { animation-delay: 0.05s; }
    .row-widget:nth-child(2) [data-testid="stMetric"] { animation-delay: 0.1s; }
    .row-widget:nth-child(3) [data-testid="stMetric"] { animation-delay: 0.15s; }
    .row-widget:nth-child(4) [data-testid="stMetric"] { animation-delay: 0.2s; }
    .row-widget:nth-child(5) [data-testid="stMetric"] { animation-delay: 0.25s; }

    /* Multiselect tags */
    [data-baseweb="tag"] {
        background: rgba(59,130,246,0.2) !important;
        border: 1px solid rgba(59,130,246,0.4) !important;
        border-radius: 6px !important;
        color: #93c5fd !important;
    }

    /* Radio buttons */
    [data-testid="stRadio"] label {
        color: var(--text-secondary) !important;
        font-size: 0.88rem !important;
    }
    [data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {
        font-weight: 600 !important;
        color: var(--text-secondary) !important;
        font-size: 0.78rem !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    /* Label styling */
    label[data-testid="stWidgetLabel"] p {
        font-weight: 600 !important;
        font-size: 0.78rem !important;
        color: var(--text-muted) !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
</style>
""", unsafe_allow_html=True)


# DATA LOADING & CACHING
@st.cache_data(ttl=600)
def load_forecast_data():
    try:
        df = pd.read_csv(f"{API_BASE_URL}/data/forecast")
        df["date"] = pd.to_datetime(df["date"])
        return df
    except Exception as e:
        st.error(f"Error loading forecast data: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=600)
def load_training_data_sample():
    try:
        df = pd.read_csv(f"{API_BASE_URL}/data/training", nrows=50000, compression="zip")
        df["date"] = pd.to_datetime(df["date"])
        return df
    except Exception as e:
        st.error(f"Error loading training data: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=600)
def load_stores_data():
    try:
        return pd.read_csv(f"{API_BASE_URL}/data/stores")
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=600)
def load_config():
    try:
        res = requests.get(f"{API_BASE_URL}/config")
        if res.status_code == 200:
            return res.json()
        return {"sparse_categories": [], "sparse_threshold": 0.7}
    except Exception:
        return {"sparse_categories": [], "sparse_threshold": 0.7}


def get_unique_families(df):
    if "family" in df.columns:
        return sorted(df["family"].unique().tolist())
    return []


def get_unique_stores(df):
    if "store_nbr" in df.columns:
        return sorted(df["store_nbr"].unique().tolist())
    return []


# PLOTLY THEME — Premium Dark
PLOTLY_LAYOUT = dict(
    template="plotly_white",
    paper_bgcolor="rgba(255, 255, 255, 0)",
    plot_bgcolor="rgba(255, 255, 255, 0)",
    font=dict(family="Inter, Outfit, sans-serif", color="#334155", size=12),
    title_font=dict(size=15, color="#0f172a", family="Outfit, Inter, sans-serif"),
    margin=dict(l=40, r=30, t=50, b=40),
    hoverlabel=dict(
        bgcolor="rgba(255, 255, 255, 0.95)",
        font_size=13,
        font_family="Inter, sans-serif",
        bordercolor="rgba(59, 130, 246, 0.4)",
    ),
    legend=dict(
        bgcolor="rgba(255, 255, 255, 0.7)",
        bordercolor="rgba(59, 130, 246, 0.12)",
        borderwidth=1,
        font=dict(size=11, color="#334155"),
        itemclick="toggleothers",
    ),
)

COLOR_PALETTE = [
    "#3b82f6", "#8b5cf6", "#ec4899", "#f97316", "#10b981",
    "#06b6d4", "#eab308", "#ef4444", "#14b8a6", "#a855f7",
    "#f43f5e", "#0ea5e9", "#84cc16", "#d946ef",
]


# LOAD DATA
forecast_df    = load_forecast_data()
training_df    = load_training_data_sample()
stores_df      = load_stores_data()
config         = load_config()
sparse_cats    = set(config.get("sparse_categories", []))


# HERO HEADER
_total_preds = f"{len(forecast_df):,}"   if not forecast_df.empty else "—"
_n_stores    = f"{forecast_df['store_nbr'].nunique()}" if not forecast_df.empty else "—"
_n_fams      = f"{forecast_df['family'].nunique()}"    if not forecast_df.empty else "—"
_date_range  = ""
if not forecast_df.empty:
    mn = forecast_df["date"].min().strftime("%b %d")
    mx = forecast_df["date"].max().strftime("%b %d, %Y")
    _date_range = f"{mn} – {mx}"

st.markdown(f"""
<div class="hero-wrapper">
    <div class="hero-orb-1"></div>
    <div class="hero-orb-2"></div>
    <div class="hero-orb-3"></div>
    <div class="hero-scanline"></div>
    <div class="hero-content">
        <div class="hero-badge">
            <span class="dot"></span>
            Live Intelligence System &nbsp;·&nbsp; XGBoost + Sparse Router
        </div>
        <div class="hero-title">
            <span class="gradient-text">SalesPulse</span><br>
            <span class="gradient-text" style="font-size: 0.55em; font-weight: 300; letter-spacing: -0.5px;">
                Smart Sales Forecasting Platform
            </span>
        </div>
        <p class="hero-subtitle">
            AI-powered system for accurate sales prediction using advanced time-series models 
            and intelligent model selection for both high-frequency and sparse demand data.
        </p>
        <div class="hero-stats">
            <div class="hero-stat">
                <span class="hero-stat-value">{_total_preds}</span>
                <span class="hero-stat-label">Total Predictions</span>
            </div>
            <div class="hero-divider"></div>
            <div class="hero-stat">
                <span class="hero-stat-value">{_n_stores}</span>
                <span class="hero-stat-label">Active Stores</span>
            </div>
            <div class="hero-divider"></div>
            <div class="hero-stat">
                <span class="hero-stat-value">{_n_fams}</span>
                <span class="hero-stat-label">Product Families</span>
            </div>
            <div class="hero-divider"></div>
            <div class="hero-stat">
                <span class="hero-stat-value"></span>
                <span class="hero-stat-label"></span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# TOP-LEVEL TABS
tab_dash, tab_single, tab_batch, tab_explore, tab_model = st.tabs([
    "Overview",
    "Single Forecast",
    "Batch Analysis",
    "Data Explorer",
    "Model Hub",
])


# OVERVIEW / DASHBOARD
with tab_dash:

    if not forecast_df.empty:
        total_predictions = len(forecast_df)
        n_stores          = forecast_df["store_nbr"].nunique()
        n_families        = forecast_df["family"].nunique()
        n_days            = (forecast_df["date"].max() - forecast_df["date"].min()).days + 1
        avg_sales         = forecast_df["prediction"].mean()
        max_daily         = forecast_df.groupby("date")["prediction"].sum().max()

        # ── KPI Row ──
        st.markdown("""
        <div class="section-header">
            <span class="section-header-icon"></span>
            <span class="section-header-title">Key Performance Indicators</span>
            <div class="section-header-line"></div>
            <span class="status-live">Live</span>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Predictions",  f"{total_predictions:,}")
        c2.metric("Active Stores",       f"{n_stores}")
        c3.metric("Product Families",    f"{n_families}")
        c4.metric("Forecast Horizon",    f"{n_days} days")
        c5.metric("Peak Daily Volume",   f"{max_daily:,.0f}")

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Chart Tabs ──
        d1, d2, d3 = st.tabs(["Sales Trend", "Top Stores", "Top Families"])

        # ── Trend ──
        with d1:
            daily_total = forecast_df.groupby("date")["prediction"].sum().reset_index()
            daily_total.columns = ["Date", "Total Predicted Sales"]

            if len(daily_total) > 3:
                window = min(7, len(daily_total))
                daily_total["Trend"] = daily_total["Total Predicted Sales"].rolling(window=window, center=True).mean()

            fig = go.Figure()
            # Gradient fill
            fig.add_trace(go.Scatter(
                x=daily_total["Date"],
                y=daily_total["Total Predicted Sales"],
                mode="lines",
                name="Total Sales",
                line=dict(color="#3b82f6", width=2.5, shape="spline"),
                fill="tozeroy",
                fillcolor="rgba(59, 130, 246, 0.07)",
                hovertemplate="<b>%{x|%A, %b %d %Y}</b><br>Total Sales: <b>%{y:,.0f}</b><extra></extra>",
            ))
            if "Trend" in daily_total:
                fig.add_trace(go.Scatter(
                    x=daily_total["Date"],
                    y=daily_total["Trend"],
                    mode="lines",
                    name=f"{window}-Day Trend",
                    line=dict(color="#f97316", width=2, dash="dot"),
                    hovertemplate="<b>%{x|%b %d}</b><br>Trend: %{y:,.0f}<extra></extra>",
                ))
            fig.update_layout(
                **PLOTLY_LAYOUT,
                title="Aggregate Forecasted Sales Over Time",
                xaxis_title="Date", yaxis_title="Total Predicted Sales",
                height=430,
            )
            st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Top Stores ──
        with d2:
            store_sales = (
                forecast_df.groupby("store_nbr")["prediction"]
                .sum().sort_values(ascending=False).head(10).reset_index()
            )
            store_sales.columns = ["Store", "Total Sales"]
            store_sales["Store"] = store_sales["Store"].astype(str)
            store_sales["rank"] = range(1, len(store_sales) + 1)

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=store_sales["Store"], y=store_sales["Total Sales"],
                marker=dict(
                    color=store_sales["Total Sales"],
                    colorscale=[[0, "#1e3a5f"], [0.4, "#3b82f6"], [0.8, "#8b5cf6"], [1, "#ec4899"]],
                    line=dict(color="rgba(255,255,255,0.05)", width=1),
                ),
                text=[f"#{r}" for r in store_sales["rank"]],
                textposition="inside",
                textfont=dict(color="rgba(255,255,255,0.7)", size=11, family="Outfit"),
                hovertemplate="<b>Store %{x}</b><br>Total Forecast: <b>%{y:,.0f}</b><extra></extra>",
            ))
            fig.update_layout(
                **PLOTLY_LAYOUT,
                title="Top 10 Stores by Forecasted Revenue",
                xaxis_title="Store Number", yaxis_title="Total Predicted Sales",
                height=430, showlegend=False,
            )
            st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Top Families ──
        with d3:
            family_sales = (
                forecast_df.groupby("family")["prediction"]
                .sum().sort_values(ascending=True).tail(10).reset_index()
            )
            family_sales.columns = ["Family", "Total Sales"]

            bar_colors = ["#8b5cf6" if f in sparse_cats else "#3b82f6" for f in family_sales["Family"]]
            model_labels = ["Sparse" if f in sparse_cats else "Dense" for f in family_sales["Family"]]

            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=family_sales["Family"], x=family_sales["Total Sales"],
                orientation="h",
                marker=dict(
                    color=bar_colors,
                    line=dict(color="rgba(255,255,255,0.04)", width=1),
                ),
                text=model_labels,
                textposition="inside",
                textfont=dict(size=10, color="rgba(255,255,255,0.7)", family="Inter"),
                hovertemplate="<b>%{y}</b><br>Total: <b>%{x:,.0f}</b><extra></extra>",
            ))
            fig.update_layout(
                **PLOTLY_LAYOUT,
                title="Top 10 Product Families  —  Blue: Dense · Purple: Sparse",
                xaxis_title="Total Predicted Sales",
                height=430, showlegend=False,
            )
            st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Heatmap ──
        st.markdown("""
        <div class="section-header">
            <span class="section-header-icon"></span>
            <span class="section-header-title">Sales Intensity Heatmap</span>
            <div class="section-header-line"></div>
        </div>
        """, unsafe_allow_html=True)

        top_families = (
            forecast_df.groupby("family")["prediction"]
            .sum().sort_values(ascending=False).head(14).index.tolist()
        )
        heatmap_df = forecast_df[forecast_df["family"].isin(top_families)]
        pivot = heatmap_df.pivot_table(values="prediction", index="family", columns="date", aggfunc="sum")

        fig_heat = go.Figure(data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns.strftime("%b %d"),
            y=pivot.index,
            colorscale=[
                [0.0,  "#f8fafc"],
                [0.15, "#e2e8f0"],
                [0.35, "#cbd5e1"],
                [0.6,  "#3b82f6"],
                [0.8,  "#8b5cf6"],
                [1.0,  "#ec4899"],
            ],
            hovertemplate="<b>%{y}</b><br>%{x}<br>Sales: <b>%{z:,.0f}</b><extra></extra>",
            colorbar=dict(
                title=dict(text="Sales", font=dict(color="#94a3b8", size=12)),
                tickfont=dict(color="#64748b"),
                len=0.85,
                thickness=14,
                bgcolor="rgba(0,0,0,0)",
            ),
            xgap=1, ygap=1,
        ))
        fig_heat.update_layout(
            **PLOTLY_LAYOUT,
            title="",
            height=460,
            xaxis_title="Date",
        )
        fig_heat.update_xaxes(tickangle=-35)
        st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
        st.plotly_chart(fig_heat, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding: 3rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;"></div>
            <p style="color: #94a3b8; font-size: 1rem; font-weight: 500;">
                No forecast data found. Please run the precompute pipeline first.
            </p>
        </div>
        """, unsafe_allow_html=True)


# SINGLE FORECAST
with tab_single:

    if not forecast_df.empty:
        families = get_unique_families(forecast_df)
        stores   = get_unique_stores(forecast_df)

        # Controls Row
        st.markdown("""
        <div class="section-header">
            <span class="section-header-icon"></span>
            <span class="section-header-title">Forecast Configuration</span>
            <div class="section-header-line"></div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            selected_stores_input = st.multiselect("Store Numbers", stores, default=[stores[0]], key="sf_stores")
            all_stores = st.checkbox("All Stores", value=False, key="sf_all_stores")
            if all_stores:
                selected_stores = stores
            else:
                selected_stores = selected_stores_input
        with col2:
            selected_family = st.selectbox("Product Family", families, key="sf_family")
        with col3:
            weeks = st.slider(" (weeks)", min_value=1, max_value=4, value=2, key="sf_weeks")

        # Model badge
        model_type  = "Sparse" if selected_family in sparse_cats else "Dense"
        model_color = "#8b5cf6" if model_type == "Sparse" else "#3b82f6"
        model_desc  = "Classifier → Regressor Pipeline" if model_type == "Sparse" else "XGBoost Regressor"
        model_icon  = "" if model_type == "Sparse" else ""

        st.markdown(f"""
        <span class="model-badge" style="
            background: {model_color}15;
            border: 1px solid {model_color}35;
            color: {model_color};">
            {model_icon} &nbsp; {model_type} Model &nbsp;·&nbsp; {model_desc}
        </span>
        """, unsafe_allow_html=True)

        # Filter
        if not selected_stores:
            filtered = pd.DataFrame()
            store_label = "None"
        else:
            store_label = "All Stores" if all_stores else (f"Store {selected_stores[0]}" if len(selected_stores)==1 else f"{len(selected_stores)} Stores")
            days = weeks * 7
            valid_dates = sorted(forecast_df["date"].unique())[:days]
            filtered = forecast_df[
                (forecast_df["store_nbr"].isin(selected_stores)) &
                (forecast_df["family"] == selected_family) &
                (forecast_df["date"].isin(valid_dates))
            ]
            if not filtered.empty:
                filtered = filtered.groupby("date")["prediction"].sum().reset_index()

        if not filtered.empty:

            # KPI Row
            st.markdown("""
            <div class="section-header" style="margin-top: 1.5rem;">
                <span class="section-header-icon"></span>
                <span class="section-header-title">Forecast Metrics</span>
                <div class="section-header-line"></div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Avg Daily Sales", f"{filtered['prediction'].mean():,.1f}")
            c2.metric("Peak Sales",      f"{filtered['prediction'].max():,.1f}")
            c3.metric("Minimum Sales",   f"{filtered['prediction'].min():,.1f}")
            c4.metric("Total Forecast",  f"{filtered['prediction'].sum():,.0f}")

            st.markdown("<br>", unsafe_allow_html=True)

            # Forecast chart
            plot_df = filtered.copy()
            plot_df["lower_bound"] = np.maximum(0, plot_df["prediction"] * 0.82)
            plot_df["upper_bound"] = plot_df["prediction"] * 1.18

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=pd.concat([plot_df["date"], plot_df["date"][::-1]]),
                y=pd.concat([plot_df["upper_bound"], plot_df["lower_bound"][::-1]]),
                fill="toself",
                fillcolor=f"rgba({int(model_color[1:3],16)}, {int(model_color[3:5],16)}, {int(model_color[5:7],16)}, 0.07)",
                line=dict(color="rgba(0,0,0,0)"),
                name="80% Confidence Band",
                hoverinfo="skip",
            ))
            fig.add_trace(go.Scatter(
                x=plot_df["date"], y=plot_df["prediction"],
                mode="lines+markers",
                name="Forecast",
                line=dict(color=model_color, width=3, shape="spline"),
                marker=dict(size=8, color=model_color,
                            line=dict(width=2.5, color="#020817"),
                            symbol="circle"),
                hovertemplate=(
                    "<b>%{x|%A, %b %d}</b><br>"
                    f"{store_label} · {selected_family}<br>"
                    "Prediction: <b>%{y:,.1f}</b><extra></extra>"
                ),
            ))
            fig.update_layout(
                **PLOTLY_LAYOUT,
                title=f"{store_label}  —  {selected_family}  ·  {weeks}-Week Horizon",
                xaxis_title="Date", yaxis_title="Predicted Sales",
                height=440,
            )
            st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Two-column: DoW pattern + DataTable
            col_a, col_b = st.columns(2)

            with col_a:
                st.markdown("""
                <div class="section-header">
                    <span class="section-header-icon"></span>
                    <span class="section-header-title">Day-of-Week Pattern</span>
                    <div class="section-header-line"></div>
                </div>
                """, unsafe_allow_html=True)
                dow         = plot_df.copy()
                dow["day_name"] = dow["date"].dt.day_name()
                dow_order   = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
                dow_colors  = [model_color]*5 + ["#f97316","#f97316"]
                dow_avg     = dow.groupby("day_name")["prediction"].mean().reindex(dow_order).reset_index()
                dow_avg.columns = ["Day","Avg Sales"]

                fig_dow = go.Figure()
                fig_dow.add_trace(go.Bar(
                    x=dow_avg["Day"], y=dow_avg["Avg Sales"],
                    marker=dict(
                        color=dow_colors,
                        line=dict(color="rgba(255,255,255,0.04)", width=1),
                    ),
                    hovertemplate="<b>%{x}</b><br>Avg: <b>%{y:,.1f}</b><extra></extra>",
                ))
                fig_dow.update_layout(
                    **PLOTLY_LAYOUT, height=350, showlegend=False,
                    title="", xaxis_title="", yaxis_title="Avg Predicted Sales",
                )
                st.plotly_chart(fig_dow, use_container_width=True)

            with col_b:
                st.markdown("""
                <div class="section-header">
                    <span class="section-header-icon"></span>
                    <span class="section-header-title">Forecast Data Table</span>
                    <div class="section-header-line"></div>
                </div>
                """, unsafe_allow_html=True)
                display_df = plot_df[["date","prediction","lower_bound","upper_bound"]].copy()
                display_df.columns = ["Date","Prediction","Lower (80%)","Upper (80%)"]
                display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d")
                display_df = display_df.round(2)
                st.dataframe(display_df, use_container_width=True, height=350, hide_index=True)

        else:
            if not selected_stores:
                msg = f"Please select at least one store."
            else:
                msg = f"No forecast data for <strong style='color:#60a5fa;'>{store_label}</strong>, Family <strong style='color:#60a5fa;'>'{selected_family}'</strong>."

            st.markdown(f"""
            <div class="glass-card" style="text-align: center; padding: 2.5rem;">
                <div style="font-size: 2.5rem; margin-bottom: 1rem;"></div>
                <p style="color: #94a3b8; font-size: 0.95rem;">
                    {msg}
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No forecast data found.")


# BATCH FORECAST / ANALYSIS
with tab_batch:

    if not forecast_df.empty:
        families = get_unique_families(forecast_df)

        st.markdown("""
        <div class="section-header">
            <span class="section-header-icon"></span>
            <span class="section-header-title">Batch Configuration</span>
            <div class="section-header-line"></div>
        </div>
        """, unsafe_allow_html=True)

        col_sel, col_wk, col_agg = st.columns([3, 1, 1])
        with col_sel:
            selected_families = st.multiselect(
                "Product Families",
                options=families,
                default=[],
                placeholder="Click to browse or type to search families...",
                key="bf_families",
            )
        with col_wk:
            weeks    = st.slider("Weeks", 1, 4, 2, key="bf_weeks")
        with col_agg:
            agg_mode = st.radio("View Mode", ["By Family", "By Store", "Summary"], key="bf_agg")

        if selected_families:
            days  = weeks * 7
            start = forecast_df["date"].min()
            end   = start + pd.Timedelta(days=days - 1)

            batch = forecast_df[
                (forecast_df["family"].isin(selected_families)) &
                (forecast_df["date"] >= start) &
                (forecast_df["date"] <= end)
            ]

            if not batch.empty:
                # Batch KPIs
                b_total  = batch["prediction"].sum()
                b_avg    = batch["prediction"].mean()
                b_stores = batch["store_nbr"].nunique()
                b_days   = batch["date"].nunique()

                bc1, bc2, bc3, bc4 = st.columns(4)
                bc1.metric("Batch Total",    f"{b_total:,.0f}")
                bc2.metric("Avg per Record", f"{b_avg:,.1f}")
                bc3.metric("Stores Covered", f"{b_stores}")
                bc4.metric("Days",           f"{b_days}")

                st.markdown("<br>", unsafe_allow_html=True)

                # Main chart
                if agg_mode == "By Family":
                    agg = batch.groupby(["date","family"])["prediction"].sum().reset_index()
                    fig = go.Figure()
                    for i, fam in enumerate(selected_families):
                        fd = agg[agg["family"] == fam]
                        fig.add_trace(go.Scatter(
                            x=fd["date"], y=fd["prediction"],
                            mode="lines", name=fam,
                            line=dict(color=COLOR_PALETTE[i % len(COLOR_PALETTE)], width=2.5, shape="spline"),
                            hovertemplate=f"<b>%{{x|%b %d}}</b><br>{fam}<br>Sales: <b>%{{y:,.0f}}</b><extra></extra>",
                        ))
                    fig.update_layout(
                        **PLOTLY_LAYOUT,
                        title="Daily Sales by Product Family",
                        xaxis_title="Date", yaxis_title="Total Sales (All Stores)",
                        height=480,
                    )

                elif agg_mode == "By Store":
                    store_agg  = batch.groupby(["date","store_nbr"])["prediction"].sum().reset_index()
                    top_stores = (
                        store_agg.groupby("store_nbr")["prediction"]
                        .sum().sort_values(ascending=False).head(8).index.tolist()
                    )
                    store_agg = store_agg[store_agg["store_nbr"].isin(top_stores)]
                    fig = go.Figure()
                    for i, s in enumerate(top_stores):
                        sd = store_agg[store_agg["store_nbr"] == s]
                        fig.add_trace(go.Scatter(
                            x=sd["date"], y=sd["prediction"],
                            mode="lines", name=f"Store {s}",
                            line=dict(color=COLOR_PALETTE[i % len(COLOR_PALETTE)], width=2.5, shape="spline"),
                            hovertemplate=f"<b>%{{x|%b %d}}</b><br>Store {s}<br>Sales: <b>%{{y:,.0f}}</b><extra></extra>",
                        ))
                    fig.update_layout(
                        **PLOTLY_LAYOUT,
                        title="Top 8 Stores — Daily Forecasted Sales",
                        xaxis_title="Date", yaxis_title="Sales",
                        height=480,
                    )

                else:
                    summary = batch.groupby("date")["prediction"].sum().reset_index()
                    summary.columns = ["Date","Total Sales"]
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=summary["Date"], y=summary["Total Sales"],
                        mode="lines+markers", name="Total",
                        line=dict(color="#3b82f6", width=3, shape="spline"),
                        marker=dict(size=7, color="#3b82f6", line=dict(width=2, color="#020817")),
                        fill="tozeroy", fillcolor="rgba(59,130,246,0.07)",
                        hovertemplate="<b>%{x|%b %d}</b><br>Total: <b>%{y:,.0f}</b><extra></extra>",
                    ))
                    fig.update_layout(
                        **PLOTLY_LAYOUT,
                        title="Aggregate Sales — All Selected Families",
                        xaxis_title="Date", yaxis_title="Total Sales",
                        height=480,
                    )

                st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

                # Distribution
                st.markdown("""
                <div class="section-header">
                    <span class="section-header-icon"></span>
                    <span class="section-header-title">Prediction Distribution Analysis</span>
                    <div class="section-header-line"></div>
                </div>
                """, unsafe_allow_html=True)

                col_a, col_b = st.columns(2)
                with col_a:
                    fig_hist = go.Figure()
                    fig_hist.add_trace(go.Histogram(
                        x=batch["prediction"], nbinsx=50,
                        marker=dict(
                            color="rgba(59,130,246,0.7)",
                            line=dict(color="#1e3a5f", width=0.5),
                        ),
                        hovertemplate="Sales: %{x:,.0f}<br>Count: <b>%{y}</b><extra></extra>",
                    ))
                    fig_hist.update_layout(
                        **PLOTLY_LAYOUT, title="Prediction Distribution",
                        xaxis_title="Predicted Sales", yaxis_title="Frequency",
                        height=360, showlegend=False,
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)

                with col_b:
                    fig_box = go.Figure()
                    for i, fam in enumerate(selected_families[:6]):
                        fd = batch[batch["family"] == fam]["prediction"]
                        fig_box.add_trace(go.Box(
                            y=fd, name=fam[:15],
                            marker_color=COLOR_PALETTE[i % len(COLOR_PALETTE)],
                            boxmean="sd",
                            line=dict(width=2),
                        ))
                    fig_box.update_layout(
                        **PLOTLY_LAYOUT, title="Sales Distribution by Family",
                        yaxis_title="Predicted Sales", height=360, showlegend=False,
                    )
                    st.plotly_chart(fig_box, use_container_width=True)

                # Raw Data Expander
                with st.expander("View Raw Forecast Data", expanded=False):
                    show_df = batch.copy()
                    show_df["date"] = show_df["date"].dt.strftime("%Y-%m-%d")
                    show_df = show_df.round(2)
                    st.dataframe(show_df, use_container_width=True, height=400, hide_index=True)
                    col_dl1, col_dl2 = st.columns([1,5])
                    with col_dl1:
                        csv = show_df.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            "⬇  Download CSV",
                            csv, "forecast_export.csv", "text/csv",
                            key="batch_dl_btn",
                        )

            else:
                st.info("No data matches the current selection.")
        else:
            st.markdown("""
            <div class="glass-card" style="text-align: center; padding: 3rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📦</div>
                <p style="color: #94a3b8; font-size: 0.95rem; font-weight: 500;">
                    Select one or more product families above to begin batch analysis.
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No forecast data found.")


# DATA EXPLORER
with tab_explore:

    if not training_df.empty:
        ex1, ex2, ex3 = st.tabs(["Historical Sales", "Feature Analysis", "Store Metadata"])

        with ex1:
            families = get_unique_families(training_df)
            stores   = get_unique_stores(training_df)

            st.markdown("""
            <div class="section-header">
                <span class="section-header-icon"></span>
                <span class="section-header-title">Filter Historical Data</span>
                <div class="section-header-line"></div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                sel_fam   = st.selectbox("Product Family", families, key="ex_fam")
            with col2:
                sel_store = st.selectbox("Store Number", stores, key="ex_store")

            hist = training_df[
                (training_df["store_nbr"] == sel_store) &
                (training_df["family"]    == sel_fam)
            ].sort_values("date")

            if not hist.empty and "sales" in hist.columns:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=hist["date"], y=hist["sales"],
                    mode="lines", name="Actual Sales",
                    line=dict(color="#10b981", width=2, shape="spline"),
                    fill="tozeroy",
                    fillcolor="rgba(16,185,129,0.05)",
                    hovertemplate="<b>%{x|%b %d, %Y}</b><br>Sales: <b>%{y:,.1f}</b><extra></extra>",
                ))
                if "roliing_mean_7" in hist.columns:
                    fig.add_trace(go.Scatter(
                        x=hist["date"], y=hist["roliing_mean_7"],
                        mode="lines", name="7-Day Rolling Mean",
                        line=dict(color="#f97316", width=2, dash="dash"),
                    ))
                fig.update_layout(
                    **PLOTLY_LAYOUT,
                    title=f"Historical Sales — Store {sel_store}, {sel_fam}",
                    xaxis_title="Date", yaxis_title="Sales", height=430,
                )
                st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

                # Feature correlations
                lag_cols = [c for c in hist.columns if "lag" in c.lower() or "rolling" in c.lower()]
                if lag_cols:
                    st.markdown("""
                    <div class="section-header">
                        <span class="section-header-icon">🔗</span>
                        <span class="section-header-title">Feature Correlations with Sales</span>
                        <div class="section-header-line"></div>
                    </div>
                    """, unsafe_allow_html=True)
                    corr_data = (
                        hist[["sales"] + lag_cols].corr()["sales"].drop("sales").sort_values(ascending=True)
                    )
                    fig_corr = go.Figure()
                    fig_corr.add_trace(go.Bar(
                        y=corr_data.index, x=corr_data.values, orientation="h",
                        marker=dict(
                            color=corr_data.values,
                            colorscale=[[0,"#ef4444"],[0.5,"#334155"],[1,"#10b981"]],
                            line=dict(color="rgba(255,255,255,0.04)", width=1),
                        ),
                        hovertemplate="<b>%{y}</b><br>Correlation: <b>%{x:.4f}</b><extra></extra>",
                    ))
                    fig_corr.update_layout(
                        **PLOTLY_LAYOUT,
                        title="Lag & Rolling Feature Correlations with Sales",
                        xaxis_title="Pearson Correlation", height=400, showlegend=False,
                    )
                    st.plotly_chart(fig_corr, use_container_width=True)
            else:
                st.info("No historical data matches the selection.")

        with ex2:
            st.markdown("""
            <div class="section-header">
                <span class="section-header-icon"></span>
                <span class="section-header-title">Feature Distributions</span>
                <div class="section-header-line"></div>
            </div>
            """, unsafe_allow_html=True)

            numeric_cols = training_df.select_dtypes(include=[np.number]).columns.tolist()
            numeric_cols = [c for c in numeric_cols if c not in ["store_nbr","id"]]

            if numeric_cols:
                selected_feat = st.selectbox("Select Feature to Analyze", numeric_cols, key="ex_feat")
                col_a, col_b  = st.columns([3, 2])
                with col_a:
                    fig_dist = go.Figure()
                    fig_dist.add_trace(go.Histogram(
                        x=training_df[selected_feat].dropna(), nbinsx=60,
                        marker=dict(
                            color="rgba(59,130,246,0.7)",
                            line=dict(color="#1e3a5f", width=0.5),
                        ),
                    ))
                    fig_dist.update_layout(
                        **PLOTLY_LAYOUT,
                        title=f"Distribution · {selected_feat}",
                        xaxis_title=selected_feat, yaxis_title="Count",
                        height=380, showlegend=False,
                    )
                    st.plotly_chart(fig_dist, use_container_width=True)

                with col_b:
                    stats    = training_df[selected_feat].describe()
                    stats_df = pd.DataFrame({"Statistic": stats.index, "Value": stats.values.round(4)})
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.dataframe(stats_df, use_container_width=True, hide_index=True, height=350)

        with ex3:
            if not stores_df.empty:
                st.markdown("""
                <div class="section-header">
                    <span class="section-header-icon"></span>
                    <span class="section-header-title">Store Registry</span>
                    <div class="section-header-line"></div>
                </div>
                """, unsafe_allow_html=True)
                st.dataframe(stores_df, use_container_width=True, hide_index=True)

                if "city" in stores_df.columns:
                    city_counts = stores_df["city"].value_counts().reset_index()
                    city_counts.columns = ["City","Stores"]
                    fig_city = go.Figure()
                    fig_city.add_trace(go.Bar(
                        x=city_counts["City"], y=city_counts["Stores"],
                        marker=dict(
                            color=city_counts["Stores"],
                            colorscale=[[0,"#1e3a5f"],[0.5,"#3b82f6"],[1,"#8b5cf6"]],
                            line=dict(color="rgba(255,255,255,0.04)", width=1),
                        ),
                        hovertemplate="<b>%{x}</b><br>Stores: <b>%{y}</b><extra></extra>",
                    ))
                    fig_city.update_layout(
                        **PLOTLY_LAYOUT,
                        title="Store Count by City",
                        xaxis_title="City", yaxis_title="Number of Stores",
                        height=380, showlegend=False,
                    )
                    fig_city.update_xaxes(tickangle=-35)
                    st.plotly_chart(fig_city, use_container_width=True)
            else:
                st.info("Store metadata not available.")
    else:
        st.warning("Training data not available.")


# MODEL HUB
with tab_model:

    st.markdown("""
    <div class="section-header">
        <span class="section-header-icon"></span>
        <span class="section-header-title">Model Architecture</span>
        <div class="section-header-line"></div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="glass-card" style="border-left: 3px solid #3b82f6; border-top-left-radius: 0; border-bottom-left-radius: 0;">
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:1.2rem;">
                <div style="background: rgba(59,130,246,0.15); border-radius:10px; padding:10px 14px; font-size:1.4rem;"></div>
                <div>
                    <div style="font-family:'Outfit',sans-serif; font-size:1.1rem; font-weight:700; color:#2563eb;">Dense Model</div>
                    <div style="font-size:0.75rem; color:#64748b; font-weight:500; text-transform:uppercase; letter-spacing:0.8px; margin-top:2px;">High-Frequency Demand</div>
                </div>
            </div>
            <table style="width:100%; border-collapse:collapse;">
                <tr style="border-bottom: 1px solid rgba(59,130,246,0.07);">
                    <td style="padding:10px 0; color:#64748b; font-size:0.83rem; font-weight:500;">Algorithm</td>
                    <td style="padding:10px 0; text-align:right; color:#0f172a; font-size:0.85rem; font-weight:600; font-family:'JetBrains Mono',monospace;">XGBoost Regressor</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(59,130,246,0.07);">
                    <td style="padding:10px 0; color:#64748b; font-size:0.83rem; font-weight:500;">Target Transform</td>
                    <td style="padding:10px 0; text-align:right; color:#0f172a; font-size:0.85rem; font-weight:600; font-family:'JetBrains Mono',monospace;">log1p(sales)</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(59,130,246,0.07);">
                    <td style="padding:10px 0; color:#64748b; font-size:0.83rem; font-weight:500;">Post-Processing</td>
                    <td style="padding:10px 0; text-align:right; color:#0f172a; font-size:0.85rem; font-weight:600; font-family:'JetBrains Mono',monospace;">expm1(pred)</td>
                </tr>
                <tr>
                    <td style="padding:10px 0 0; color:#64748b; font-size:0.83rem; font-weight:500;">Use Case</td>
                    <td style="padding:10px 0 0; text-align:right; color:#0f172a; font-size:0.85rem; font-weight:600;">High-frequency families</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="glass-card" style="border-left: 3px solid #8b5cf6; border-top-left-radius: 0; border-bottom-left-radius: 0;">
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:1.2rem;">
                <div style="background: rgba(139,92,246,0.15); border-radius:10px; padding:10px 14px; font-size:1.4rem;"></div>
                <div>
                    <div style="font-family:'Outfit',sans-serif; font-size:1.1rem; font-weight:700; color:#7c3aed;">Sparse Model</div>
                    <div style="font-size:0.75rem; color:#64748b; font-weight:500; text-transform:uppercase; letter-spacing:0.8px; margin-top:2px;">Low-Frequency / Intermittent Demand</div>
                </div>
            </div>
            <table style="width:100%; border-collapse:collapse;">
                <tr style="border-bottom: 1px solid rgba(139,92,246,0.07);">
                    <td style="padding:10px 0; color:#64748b; font-size:0.83rem; font-weight:500;">Stage 1</td>
                    <td style="padding:10px 0; text-align:right; color:#0f172a; font-size:0.85rem; font-weight:600;">Binary Classifier (zero/nonzero)</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(139,92,246,0.07);">
                    <td style="padding:10px 0; color:#64748b; font-size:0.83rem; font-weight:500;">Stage 2</td>
                    <td style="padding:10px 0; text-align:right; color:#0f172a; font-size:0.85rem; font-weight:600; font-family:'JetBrains Mono',monospace;">XGBoost Regressor</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(139,92,246,0.07);">
                    <td style="padding:10px 0; color:#64748b; font-size:0.83rem; font-weight:500;">Target Transform</td>
                    <td style="padding:10px 0; text-align:right; color:#0f172a; font-size:0.85rem; font-weight:600; font-family:'JetBrains Mono',monospace;">log1p(sales)</td>
                </tr>
                <tr>
                    <td style="padding:10px 0 0; color:#64748b; font-size:0.83rem; font-weight:500;">Use Case</td>
                    <td style="padding:10px 0 0; text-align:right; color:#0f172a; font-size:0.85rem; font-weight:600;">Sparse / intermittent demand</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    # ── Routing Pipeline ──
    st.markdown("""
<div class="glass-card" style="padding: 1.5rem 1rem; overflow-x: auto;">
    <div style="display:flex; align-items:center; justify-content:center; gap:8px; min-width: max-content; padding: 0.5rem;">
        <!-- INPUT -->
        <div style="text-align:center;">
            <div style="background:rgba(6,182,212,0.18); border:1px solid rgba(6,182,212,0.4);border-radius:14px; padding:12px 18px;">
                <div style="font-size:1.4rem;"></div>
                <div style="font-weight:700; color:#0891b2; font-size:0.88rem;">Input Features</div>
                <div style="font-size:0.7rem; color:#1e293b;">Time + Lag + Rolling</div>
            </div>
        </div>
        <div style="font-size:1.3rem; color:#475569;">➜</div>
        <!-- ROUTER -->
        <div style="text-align:center;">
            <div style="background:rgba(234,179,8,0.18); border:1px solid rgba(234,179,8,0.4);border-radius:14px; padding:12px 18px;">
                <div style="font-size:1.4rem;"></div>
                <div style="font-weight:700; color:#d97706; font-size:0.88rem;">ModelRouter</div>
                <div style="font-size:0.7rem; color:#1e293b;">family → sparse_cats</div>
            </div>
        </div>
        <div style="font-size:1.3rem; color:#475569;">➜</div>
        <!-- MODELS -->
        <div style="display:flex; flex-direction:column; gap:8px;">
            <div style="background:rgba(59,130,246,0.18); border:1px solid rgba(59,130,246,0.4);border-radius:12px; padding:10px 16px; font-size:0.82rem; color:#2563eb; font-weight:700;">
                 Dense → XGBoost → expm1
            </div>
            <div style="background:rgba(139,92,246,0.18); border:1px solid rgba(139,92,246,0.4);border-radius:12px; padding:10px 16px; font-size:0.82rem; color:#7c3aed; font-weight:700;">
                 Sparse → Classify → Regress → expm1
            </div>
        </div>
        <div style="font-size:1.3rem; color:#475569;">➜</div>
        <!-- OUTPUT -->
        <div style="text-align:center;">
            <div style="background:rgba(16,185,129,0.18); border:1px solid rgba(16,185,129,0.4);border-radius:14px; padding:12px 18px;">
                <div style="font-size:1.4rem;"></div>
                <div style="font-weight:700; color:#059669; font-size:0.88rem;">Final Prediction</div>
                <div style="font-size:0.7rem; color:#1e293b;">Sales Forecast</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    # ── Sparse Categories ──
    st.markdown("""
    <div class="section-header">
        <span class="section-header-icon"></span>
        <span class="section-header-title">Sparse Model Categories</span>
        <div class="section-header-line"></div>
    </div>
    """, unsafe_allow_html=True)

    threshold = config.get("sparse_threshold", 0.7)
    tags_html = "".join([
        f"""<span style="
            display:inline-block;
            background:rgba(139,92,246,0.12);
            border:1px solid rgba(139,92,246,0.25);
            border-radius:8px;
            padding:6px 14px;
            color:#c4b5fd;
            font-weight:600;
            font-size:0.82rem;
            font-family:'Inter',sans-serif;
            margin: 4px;
            transition: all 0.2s ease;
        ">{cat}</span>"""
        for cat in sparse_cats
    ]) if sparse_cats else "<span style='color:#64748b; font-size:0.9rem;'>No sparse categories configured.</span>"

    st.markdown(f"""
    <div class="glass-card">
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:14px;">
            <span style="color:#f97316; font-weight:700; font-family:'Outfit',sans-serif; font-size:1.1rem;">&gt;{threshold*100:.0f}%</span>
            <span style="color:#94a3b8; font-size:0.88rem;">zero-sales days threshold — families above this are routed to the sparse pipeline</span>
        </div>
        <div style="display:flex; flex-wrap:wrap; gap:4px;">
            {tags_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Feature Pipeline ──
    st.markdown("""
    <div class="section-header">
        <span class="section-header-icon"></span>
        <span class="section-header-title">Feature Engineering Pipeline</span>
        <div class="section-header-line"></div>
    </div>
    """, unsafe_allow_html=True)

    features_info = pd.DataFrame({
        "Group":       ["Time","Time","Time","Time","Time","Lag","Lag","Lag","Lag","Rolling","Rolling","Rolling","Rolling"],
        "Feature":     ["day_of_week","day_of_month","week_of_year","time_index","is_weekend",
                        "dales_lag_1","dales_lag_7","dales_lag_14","dales_lag_28",
                        "roliing_mean_7","rolling_std_7","rolling_mean_14","rolling_mean_30"],
        "Description": [
            "Day of week (0=Mon → 6=Sun)","Day of month (1–31)","ISO week of year",
            "Days since dataset start","Binary weekend flag (Sat/Sun = 1)",
            "Sales 1 day ago","Sales 7 days ago","Sales 14 days ago","Sales 28 days ago",
            "7-day rolling mean","7-day rolling std deviation","14-day rolling mean","30-day rolling mean",
        ],
    })
    st.dataframe(features_info, use_container_width=True, hide_index=True, height=480)

    # ── Model Artifacts ──
    st.markdown("""
    <div class="section-header">
        <span class="section-header-icon"></span>
        <span class="section-header-title">Model Artifacts</span>
        <div class="section-header-line"></div>
    </div>
    """, unsafe_allow_html=True)

    model_files = []
    try:
        res = requests.get(f"{API_BASE_URL}/models")
        if res.status_code == 200:
            model_files = res.json()
    except:
        pass
        
    if model_files:
        st.dataframe(pd.DataFrame(model_files), use_container_width=True, hide_index=True)
    else:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:2rem;">
            <p style="color:#64748b; font-size:0.88rem; margin:0;">No model artifacts found in <code style="color:#60a5fa;">models/</code> directory.</p>
        </div>
        """, unsafe_allow_html=True)


# FOOTER
st.markdown("""
<div class="footer-wrap">
    <div>
        <span class="footer-brand">SalesPulse</span>
        <span style="color:#334155; margin: 0 10px;">·</span>
        <span class="footer-copy">Sales Forecasting Platform</span>
    </div>
    <div class="footer-copy" style="display:flex; align-items:center; gap:16px;">
        <span>Built with Streamlit + Plotly</span>
    </div>
</div>
""", unsafe_allow_html=True)
