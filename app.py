"""
Dashboard Simulasi Verifikasi Pembayaran Digital
=================================================
Menggunakan Discrete Event Simulation (DES) & Monte Carlo

Fitur:
- Home: Penjelasan model simulasi
- Dataset: Lihat & kelola dataset transaksi
- Simulation: Jalankan simulasi dengan parameter kustom + real-time view
- Analytics: Visualisasi dan grafik hasil simulasi
- About Model: Penjelasan entitas, state, event, dan persamaan
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import time
import os
from pathlib import Path

from simulation.des import DESSimulation, get_server_state_at_time
from simulation.monte_carlo import MonteCarloSimulation

# ======================== PAGE CONFIG ========================
st.set_page_config(
    page_title="Simulasi Verifikasi Pembayaran Digital",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================== CUSTOM CSS ========================
st.markdown("""
<style>
    /* Main background & font */
    .stApp {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown li,
    [data-testid="stSidebar"] .stMarkdown label {
        color: #e0e0e0 !important;
    }
    
    /* KPI Card styling */
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 24px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        margin-bottom: 16px;
    }
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.5);
    }
    .kpi-card h3 {
        margin: 0;
        font-size: 14px;
        font-weight: 500;
        opacity: 0.85;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .kpi-card h1 {
        margin: 8px 0 0 0;
        font-size: 36px;
        font-weight: 700;
    }
    
    .kpi-card-blue {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        box-shadow: 0 8px 32px rgba(79, 172, 254, 0.3);
    }
    .kpi-card-green {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        box-shadow: 0 8px 32px rgba(67, 233, 123, 0.3);
        color: #1a1a2e;
    }
    .kpi-card-green h3 { color: #1a1a2e !important; }
    .kpi-card-orange {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        box-shadow: 0 8px 32px rgba(250, 112, 154, 0.3);
        color: #1a1a2e;
    }
    .kpi-card-orange h3 { color: #1a1a2e !important; }
    .kpi-card-red {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        box-shadow: 0 8px 32px rgba(240, 147, 251, 0.3);
    }

    /* Server status boxes */
    .server-box {
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        text-align: center;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.3s ease;
    }
    .server-busy {
        background: linear-gradient(135deg, #f5576c 0%, #ff6b6b 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(245, 87, 108, 0.4);
        animation: pulse-busy 2s infinite;
    }
    .server-idle {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        color: #1a1a2e;
        box-shadow: 0 4px 15px rgba(67, 233, 123, 0.3);
    }
    
    @keyframes pulse-busy {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.85; }
    }
    
    /* Queue item */
    .queue-item {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        border-radius: 8px;
        padding: 8px 16px;
        margin: 4px;
        display: inline-block;
        font-weight: 600;
        color: #1a1a2e;
        font-size: 13px;
    }
    
    /* Section headers */
    .section-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 28px;
        font-weight: 800;
        margin-bottom: 4px;
    }
    
    /* Hero banner */
    .hero-banner {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        border-radius: 20px;
        padding: 40px;
        color: white;
        text-align: center;
        margin-bottom: 32px;
        box-shadow: 0 12px 40px rgba(15, 12, 41, 0.4);
    }
    .hero-banner h1 {
        font-size: 32px;
        font-weight: 800;
        margin-bottom: 8px;
        background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .hero-banner p {
        font-size: 16px;
        opacity: 0.8;
        margin: 4px 0;
    }
    
    /* Model info card */
    .model-card {
        background: rgba(102, 126, 234, 0.08);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 16px;
        padding: 24px;
        margin: 12px 0;
    }
    
    /* Equation block */
    .equation-block {
        background: linear-gradient(135deg, #f8f9ff 0%, #eef0ff 100%);
        border-left: 4px solid #667eea;
        border-radius: 0 12px 12px 0;
        padding: 20px 24px;
        margin: 16px 0;
        font-size: 15px;
    }
    
    /* Progress bar enhancement */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    /* Metric container */
    [data-testid="stMetric"] {
        background: rgba(102, 126, 234, 0.06);
        border-radius: 12px;
        padding: 12px 16px;
        border: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 20px;
    }
    
    /* Divider */
    .gradient-divider {
        height: 3px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        border-radius: 3px;
        margin: 24px 0;
    }
</style>
""", unsafe_allow_html=True)


# ======================== DATA LOADING ========================
DATA_DIR = Path("data")

@st.cache_data
def load_dataset(scenario_key):
    """Load dataset dari file JSON"""
    filepath = DATA_DIR / f"{scenario_key}_dataset.json"
    if filepath.exists():
        with open(filepath, 'r') as f:
            return json.load(f)
    return None

@st.cache_data
def load_all_datasets():
    """Load semua dataset yang tersedia"""
    scenario_keys = ['sepi', 'normal', 'padat', 'sangat_padat']
    datasets = {}
    for key in scenario_keys:
        data = load_dataset(key)
        if data:
            datasets[key] = data
    return datasets

def json_to_dataframe(json_data):
    """Convert JSON dataset ke DataFrame untuk simulasi"""
    transactions = json_data['transactions']
    df = pd.DataFrame([{
        'Transaction_ID': tx['transaction_id'],
        'Interarrival_Time': tx['interarrival_time'],
        'Verification_Time': tx['verification_time']
    } for tx in transactions])
    return df

SCENARIO_LABELS = {
    'sepi': '🟢 Sepi (Low Traffic)',
    'normal': '🔵 Normal (Medium Traffic)',
    'padat': '🟠 Padat (High Traffic)',
    'sangat_padat': '🔴 Sangat Padat (Very High Traffic)'
}

SCENARIO_COLORS = {
    'sepi': '#43e97b',
    'normal': '#4facfe',
    'padat': '#fa709a',
    'sangat_padat': '#f5576c'
}


# ======================== SIDEBAR ========================
with st.sidebar:
    st.markdown("## 💳 Dashboard Simulasi")
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    page = st.radio(
        "Navigasi",
        ["🏠 Home", "📊 Dataset", "🚀 Simulation", "📈 Analytics", "📐 About Model"],
        label_visibility="collapsed"
    )
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center; opacity:0.6; font-size:12px; color:#ccc;">
        <p>PDSD Final Project</p>
        <p>DES + Monte Carlo</p>
        <p style="margin-top:8px;">© 2026</p>
    </div>
    """, unsafe_allow_html=True)


# ======================== HOME PAGE ========================
if page == "🏠 Home":
    st.markdown("""
    <div class="hero-banner">
        <h1>💳 Simulasi Verifikasi Pembayaran Digital</h1>
        <p>Discrete Event Simulation (DES) + Monte Carlo Simulation</p>
        <p style="margin-top:16px; font-size:14px;">Menganalisis Pengaruh Kepadatan Transaksi terhadap Kinerja Server Verifikasi</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="model-card">
            <h3>🔬 Model Simulasi</h3>
            <ul>
                <li><strong>Discrete Event Simulation (DES)</strong><br>
                    Mensimulasikan proses verifikasi transaksi dengan event-driven approach</li>
                <li><strong>Monte Carlo Simulation</strong><br>
                    Menjalankan DES berulang kali (1000x) dengan randomized verification time untuk menangkap ketidakpastian</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="model-card">
            <h3>🖥️ Konfigurasi Server</h3>
            <ul>
                <li><strong>4 Server Verifikasi</strong> (paralel, identik)</li>
                <li>Strategi: <strong>Earliest Available Server</strong></li>
                <li>Scheduling: <strong>First-Come-First-Served</strong> (FCFS)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="model-card">
            <h3>📋 4 Skenario Simulasi</h3>
            <table style="width:100%; border-collapse:collapse; margin-top:12px;">
                <tr style="border-bottom:1px solid rgba(102,126,234,0.2);">
                    <th style="text-align:left; padding:8px;">Skenario</th>
                    <th style="text-align:center; padding:8px;">Transaksi</th>
                    <th style="text-align:center; padding:8px;">Avg IA</th>
                </tr>
                <tr style="border-bottom:1px solid rgba(102,126,234,0.1);">
                    <td style="padding:8px;">🟢 Sepi</td>
                    <td style="text-align:center;">20</td>
                    <td style="text-align:center;">5.0 s</td>
                </tr>
                <tr style="border-bottom:1px solid rgba(102,126,234,0.1);">
                    <td style="padding:8px;">🔵 Normal</td>
                    <td style="text-align:center;">40</td>
                    <td style="text-align:center;">2.5 s</td>
                </tr>
                <tr style="border-bottom:1px solid rgba(102,126,234,0.1);">
                    <td style="padding:8px;">🟠 Padat</td>
                    <td style="text-align:center;">80</td>
                    <td style="text-align:center;">1.25 s</td>
                </tr>
                <tr>
                    <td style="padding:8px;">🔴 Sangat Padat</td>
                    <td style="text-align:center;">160</td>
                    <td style="text-align:center;">0.625 s</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="model-card">
            <h3>📊 Metrik yang Diukur</h3>
            <ul>
                <li>⏱️ <strong>Average Waiting Time</strong></li>
                <li>📈 <strong>Server Utilization</strong></li>
                <li>📏 <strong>Average Queue Length</strong></li>
                <li>⏲️ <strong>Total Completion Time</strong></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # Research Questions
    st.markdown("### 🔍 Pertanyaan Penelitian")
    questions = [
        "Bagaimana pengaruh kepadatan transaksi terhadap waktu tunggu verifikasi?",
        "Bagaimana pengaruh kepadatan transaksi terhadap utilisasi server?",
        "Apakah 4 server verifikasi mampu menangani seluruh skenario transaksi?",
        "Pada kondisi apa antrean transaksi mulai meningkat secara signifikan?"
    ]
    for i, q in enumerate(questions, 1):
        st.info(f"**Q{i}.** {q}")


# ======================== DATASET PAGE ========================
elif page == "📊 Dataset":
    st.markdown('<p class="section-header">📊 Dataset Transaksi</p>', unsafe_allow_html=True)
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    datasets = load_all_datasets()
    
    if not datasets:
        st.error("❌ Tidak ada dataset ditemukan di folder `data/`")
    else:
        selected_scenario = st.selectbox(
            "Pilih Skenario",
            list(datasets.keys()),
            format_func=lambda x: SCENARIO_LABELS.get(x, x)
        )
        
        data = datasets[selected_scenario]
        df = json_to_dataframe(data)
        stats = data['statistics']
        meta = data['metadata']
        
        # Display metadata
        st.markdown(f"### 📋 {data['scenario_name']} — *{data['description']}*")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <h3>Total Transaksi</h3>
                <h1>{stats['total_transactions']}</h1>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="kpi-card kpi-card-blue">
                <h3>Avg Interarrival</h3>
                <h1>{stats['avg_interarrival']:.2f}s</h1>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="kpi-card kpi-card-green">
                <h3>Avg Verif. Time</h3>
                <h1>{stats['avg_verification_time']:.2f}s</h1>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="kpi-card kpi-card-orange">
                <h3>Total Sim. Time</h3>
                <h1>{stats['total_simulation_time']:.1f}s</h1>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
        
        # Data table
        tab1, tab2 = st.tabs(["📋 Data Tabel", "📊 Distribusi"])
        
        with tab1:
            display_df = df.copy()
            display_df.index = display_df.index + 1
            display_df.index.name = "No"
            st.dataframe(display_df, use_container_width=True, height=400)
        
        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                fig_ia = px.histogram(
                    df, x='Interarrival_Time', nbins=20,
                    title="Distribusi Interarrival Time",
                    labels={'Interarrival_Time': 'Interarrival Time (detik)', 'count': 'Frekuensi'},
                    color_discrete_sequence=['#667eea']
                )
                fig_ia.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12)
                )
                st.plotly_chart(fig_ia, use_container_width=True)
            
            with col2:
                fig_vt = px.histogram(
                    df, x='Verification_Time', nbins=20,
                    title="Distribusi Verification Time",
                    labels={'Verification_Time': 'Verification Time (detik)', 'count': 'Frekuensi'},
                    color_discrete_sequence=['#764ba2']
                )
                fig_vt.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12)
                )
                st.plotly_chart(fig_vt, use_container_width=True)
            
            # Statistik detail
            st.markdown("#### 📈 Statistik Detail")
            stat_col1, stat_col2 = st.columns(2)
            with stat_col1:
                st.markdown("**Interarrival Time**")
                st.write(f"- Min: `{stats['min_interarrival']:.4f}` s")
                st.write(f"- Max: `{stats['max_interarrival']:.4f}` s")
                st.write(f"- Mean: `{stats['avg_interarrival']:.4f}` s")
                st.write(f"- Distribusi: `{meta['interarrival_time_distribution']['type']}` (μ={meta['interarrival_time_distribution']['mean']}, σ={meta['interarrival_time_distribution']['std_dev']})")
            with stat_col2:
                st.markdown("**Verification Time**")
                st.write(f"- Min: `{stats['min_verification_time']:.4f}` s")
                st.write(f"- Max: `{stats['max_verification_time']:.4f}` s")
                st.write(f"- Mean: `{stats['avg_verification_time']:.4f}` s")
                st.write(f"- Distribusi: `{meta['verification_time_distribution']['type']}` [{meta['verification_time_distribution']['min']}, {meta['verification_time_distribution']['max']}]")


# ======================== SIMULATION PAGE ========================
elif page == "🚀 Simulation":
    st.markdown('<p class="section-header">🚀 Jalankan Simulasi</p>', unsafe_allow_html=True)
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    datasets = load_all_datasets()
    
    # Input Parameters
    st.markdown("### ⚙️ Parameter Simulasi")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_scenario = st.selectbox(
            "Skenario",
            list(datasets.keys()),
            format_func=lambda x: SCENARIO_LABELS.get(x, x),
            index=1  # default Normal
        )
    
    with col2:
        num_servers = st.slider("Jumlah Server", min_value=1, max_value=8, value=4)
    
    with col3:
        mc_iterations = st.select_slider(
            "Iterasi Monte Carlo",
            options=[10, 50, 100, 200, 500, 1000],
            value=100
        )
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # Run Simulation Button
    run_col1, run_col2, run_col3 = st.columns([1, 2, 1])
    with run_col2:
        run_simulation = st.button("🚀 Jalankan Simulasi", use_container_width=True, type="primary")
    
    if run_simulation:
        data = datasets[selected_scenario]
        df = json_to_dataframe(data)
        
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
        
        # ---- SINGLE DES RUN (for real-time view) ----
        st.markdown("### 🖥️ Simulasi Real-Time — Single DES Run")
        
        des = DESSimulation(num_servers=num_servers)
        des_results = des.run_simulation(df)
        
        # Real-time server visualization
        max_time = des_results['End_Time'].max()
        
        # Create a set of interesting time points
        time_points = sorted(set(
            list(des_results['Arrival_Time'].values) + 
            list(des_results['Start_Time'].values) +
            list(des_results['End_Time'].values)
        ))
        
        # Pick ~15 time snapshots
        if len(time_points) > 15:
            step = len(time_points) // 15
            time_points = time_points[::step]
        
        realtime_placeholder = st.empty()
        time_slider_val = st.select_slider(
            "⏱️ Waktu Simulasi (detik)",
            options=[round(t, 2) for t in time_points],
            value=round(time_points[len(time_points)//2], 2)
        )
        
        # Show server state at selected time
        server_status, queue = get_server_state_at_time(des_results, time_slider_val, num_servers)
        
        with realtime_placeholder.container():
            st.markdown(f"**⏱️ Time = {time_slider_val:.2f}s**")
            
            server_cols = st.columns(num_servers)
            for s_id in range(1, num_servers + 1):
                with server_cols[s_id - 1]:
                    status = server_status[s_id]
                    if status['status'] == 'Busy':
                        progress = status.get('progress', 0)
                        st.markdown(f"""
                        <div class="server-box server-busy">
                            Server {s_id}<br>
                            <strong>{status['transaction']}</strong><br>
                            <small>{progress:.0f}%</small>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="server-box server-idle">
                            Server {s_id}<br>
                            <strong>Idle</strong>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Queue display
            if queue:
                queue_html = "".join([f'<span class="queue-item">{tx}</span>' for tx in queue])
                st.markdown(f"**📋 Antrian ({len(queue)}):** {queue_html}", unsafe_allow_html=True)
            else:
                st.markdown("**📋 Antrian: —** *(Kosong)*")
        
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
        
        # ---- DES SINGLE RUN RESULTS TABLE ----
        with st.expander("📋 Detail Hasil DES (Single Run)", expanded=False):
            st.dataframe(des_results, use_container_width=True, height=300)
        
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
        
        # ---- MONTE CARLO ----
        st.markdown(f"### 🎲 Monte Carlo Simulation — {mc_iterations} Iterasi")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(current, total):
            progress_bar.progress(current / total)
            status_text.text(f"⏳ Iterasi {current}/{total}...")
        
        mc = MonteCarloSimulation(num_iterations=mc_iterations, num_servers=num_servers)
        
        start_time = time.time()
        mc.run_monte_carlo(df, vt_min=2, vt_max=6, progress_callback=update_progress)
        elapsed = time.time() - start_time
        
        progress_bar.progress(1.0)
        status_text.text(f"✅ Selesai dalam {elapsed:.2f} detik")
        
        aggregated, metrics_df = mc.get_aggregated_metrics()
        
        # Store results in session state
        st.session_state['mc_results'] = {
            'aggregated': aggregated,
            'metrics_df': metrics_df,
            'mc': mc,
            'des_results': des_results,
            'scenario': selected_scenario,
            'num_servers': num_servers,
            'mc_iterations': mc_iterations,
            'elapsed': elapsed
        }
        
        # ---- KPI CARDS ----
        st.markdown("### 📊 Hasil Simulasi (KPI)")
        
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            st.markdown(f"""
            <div class="kpi-card">
                <h3>Avg Waiting Time</h3>
                <h1>{aggregated['Avg_Waiting_Time']:.2f}s</h1>
            </div>
            """, unsafe_allow_html=True)
        with kpi2:
            st.markdown(f"""
            <div class="kpi-card kpi-card-blue">
                <h3>Server Utilization</h3>
                <h1>{aggregated['Avg_Server_Utilization']:.1f}%</h1>
            </div>
            """, unsafe_allow_html=True)
        with kpi3:
            st.markdown(f"""
            <div class="kpi-card kpi-card-green">
                <h3>Avg Queue Length</h3>
                <h1>{aggregated['Avg_Queue_Length']:.2f}</h1>
            </div>
            """, unsafe_allow_html=True)
        with kpi4:
            st.markdown(f"""
            <div class="kpi-card kpi-card-orange">
                <h3>Completion Time</h3>
                <h1>{aggregated['Avg_Completion_Time']:.1f}s</h1>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
        
        # ---- QUICK CHARTS ----
        st.markdown("### 📈 Grafik Cepat")
        
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            fig_wt = px.histogram(
                metrics_df, x='Avg_Waiting_Time', nbins=30,
                title="Histogram: Average Waiting Time (Monte Carlo)",
                labels={'Avg_Waiting_Time': 'Avg Waiting Time (s)', 'count': 'Frekuensi'},
                color_discrete_sequence=['#667eea']
            )
            fig_wt.add_vline(x=aggregated['Avg_Waiting_Time'], line_dash="dash", line_color="#f5576c",
                             annotation_text=f"Mean: {aggregated['Avg_Waiting_Time']:.3f}s")
            fig_wt.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_wt, use_container_width=True)
        
        with chart_col2:
            fig_ct = px.histogram(
                metrics_df, x='Total_Completion_Time', nbins=30,
                title="Histogram: Total Completion Time (Monte Carlo)",
                labels={'Total_Completion_Time': 'Completion Time (s)', 'count': 'Frekuensi'},
                color_discrete_sequence=['#764ba2']
            )
            fig_ct.add_vline(x=aggregated['Avg_Completion_Time'], line_dash="dash", line_color="#f5576c",
                             annotation_text=f"Mean: {aggregated['Avg_Completion_Time']:.1f}s")
            fig_ct.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_ct, use_container_width=True)
        
        st.success(f"✅ Simulasi selesai! Buka tab **📈 Analytics** untuk visualisasi lengkap.")


# ======================== ANALYTICS PAGE ========================
elif page == "📈 Analytics":
    st.markdown('<p class="section-header">📈 Analitik & Visualisasi</p>', unsafe_allow_html=True)
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    if 'mc_results' not in st.session_state:
        st.warning("⚠️ Belum ada hasil simulasi. Silakan jalankan simulasi terlebih dahulu di tab **🚀 Simulation**.")
        st.stop()
    
    results = st.session_state['mc_results']
    aggregated = results['aggregated']
    metrics_df = results['metrics_df']
    mc = results['mc']
    des_results = results['des_results']
    scenario = results['scenario']
    num_servers = results['num_servers']
    
    st.markdown(f"**Skenario:** {SCENARIO_LABELS.get(scenario, scenario)} | "
                f"**Server:** {num_servers} | "
                f"**Iterasi MC:** {results['mc_iterations']} | "
                f"**Waktu:** {results['elapsed']:.2f}s")
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # ---- KPI RECAP ----
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(f"""
        <div class="kpi-card">
            <h3>Avg Waiting Time</h3>
            <h1>{aggregated['Avg_Waiting_Time']:.2f}s</h1>
        </div>
        """, unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"""
        <div class="kpi-card kpi-card-blue">
            <h3>Server Utilization</h3>
            <h1>{aggregated['Avg_Server_Utilization']:.1f}%</h1>
        </div>
        """, unsafe_allow_html=True)
    with kpi3:
        st.markdown(f"""
        <div class="kpi-card kpi-card-green">
            <h3>Avg Queue Length</h3>
            <h1>{aggregated['Avg_Queue_Length']:.2f}</h1>
        </div>
        """, unsafe_allow_html=True)
    with kpi4:
        st.markdown(f"""
        <div class="kpi-card kpi-card-orange">
            <h3>Completion Time</h3>
            <h1>{aggregated['Avg_Completion_Time']:.1f}s</h1>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # ---- GRAFIK 1: Waiting Time per Transaksi (Single DES) ----
    st.markdown("### Grafik 1: Waiting Time per Transaksi")
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=des_results['Transaction_ID'],
        y=des_results['Waiting_Time'],
        marker_color=des_results['Waiting_Time'].apply(
            lambda w: '#43e97b' if w == 0 else ('#fa709a' if w > 2 else '#4facfe')
        ),
        text=des_results['Waiting_Time'].apply(lambda x: f"{x:.2f}s"),
        textposition='outside'
    ))
    fig1.update_layout(
        title="Waiting Time per Transaksi (Single DES Run)",
        xaxis_title="Transaction ID",
        yaxis_title="Waiting Time (detik)",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # ---- GRAFIK 2: Queue Length ----
    st.markdown("### Grafik 2: Queue Length Over Time")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=des_results['Arrival_Time'],
        y=des_results['Queue_Length_At_Arrival'],
        mode='lines+markers',
        name='Queue Length',
        line=dict(color='#667eea', width=2),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor='rgba(102, 126, 234, 0.15)'
    ))
    fig2.update_layout(
        title="Panjang Antrian saat Kedatangan Transaksi",
        xaxis_title="Waktu (detik)",
        yaxis_title="Queue Length",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    # ---- GRAFIK 3: Server Utilization Gantt Chart ----
    st.markdown("### Grafik 3: Server Utilization (Gantt Chart)")
    gantt_data = []
    for _, row in des_results.iterrows():
        gantt_data.append({
            'Server': f"Server {int(row['Server_ID'])}",
            'Start': row['Start_Time'],
            'End': row['End_Time'],
            'Transaction': row['Transaction_ID'],
            'Duration': row['Verification_Time']
        })
    gantt_df = pd.DataFrame(gantt_data)
    
    fig3 = go.Figure()
    colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a', '#fee140', '#f5576c']
    
    for i, (_, row) in enumerate(gantt_df.iterrows()):
        fig3.add_trace(go.Bar(
            x=[row['Duration']],
            y=[row['Server']],
            base=[row['Start']],
            orientation='h',
            marker_color=colors[i % len(colors)],
            text=row['Transaction'],
            textposition='inside',
            hovertemplate=f"<b>{row['Transaction']}</b><br>Start: {row['Start']:.2f}s<br>End: {row['End']:.2f}s<br>Duration: {row['Duration']:.2f}s<extra></extra>",
            showlegend=False
        ))
    
    fig3.update_layout(
        title="Timeline Penggunaan Server",
        xaxis_title="Waktu (detik)",
        yaxis_title="Server",
        barmode='stack',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=300
    )
    st.plotly_chart(fig3, use_container_width=True)
    
    # ---- GRAFIK 4: Completion Time Distribution ----
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Grafik 4: Completion Time")
        fig4 = px.histogram(
            metrics_df, x='Total_Completion_Time', nbins=30,
            title="Distribusi Total Completion Time (Monte Carlo)",
            color_discrete_sequence=['#764ba2']
        )
        fig4.add_vline(x=aggregated['Avg_Completion_Time'], line_dash="dash", line_color="#f5576c",
                       annotation_text=f"μ = {aggregated['Avg_Completion_Time']:.2f}s")
        fig4.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=400)
        st.plotly_chart(fig4, use_container_width=True)
    
    with col2:
        st.markdown("### Grafik 5: Histogram Monte Carlo (Waiting Time)")
        fig5 = px.histogram(
            metrics_df, x='Avg_Waiting_Time', nbins=30,
            title="Distribusi Average Waiting Time (Monte Carlo)",
            color_discrete_sequence=['#667eea']
        )
        fig5.add_vline(x=aggregated['Avg_Waiting_Time'], line_dash="dash", line_color="#f5576c",
                       annotation_text=f"μ = {aggregated['Avg_Waiting_Time']:.3f}s")
        fig5.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=400)
        st.plotly_chart(fig5, use_container_width=True)
    
    # ---- GRAFIK 6: Boxplot Monte Carlo ----
    st.markdown("### Grafik 6: Boxplot Hasil Monte Carlo")
    
    box_data = pd.DataFrame({
        'Avg Waiting Time': metrics_df['Avg_Waiting_Time'],
        'Max Waiting Time': metrics_df['Max_Waiting_Time'],
        'Server Utilization (%)': metrics_df['Server_Utilization'],
        'Completion Time': metrics_df['Total_Completion_Time']
    })
    
    fig6 = make_subplots(rows=1, cols=4, subplot_titles=[
        "Avg Waiting Time", "Max Waiting Time", "Server Utilization (%)", "Completion Time"
    ])
    
    box_colors = ['#667eea', '#764ba2', '#43e97b', '#fa709a']
    for i, col_name in enumerate(box_data.columns):
        fig6.add_trace(
            go.Box(y=box_data[col_name], name=col_name, marker_color=box_colors[i],
                   boxmean='sd'),
            row=1, col=i+1
        )
    
    fig6.update_layout(
        title="Distribusi Metrik dari Monte Carlo Simulation",
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=450
    )
    st.plotly_chart(fig6, use_container_width=True)
    
    # ---- Convergence Chart ----
    st.markdown("### 📉 Konvergensi Monte Carlo")
    running_avg = metrics_df['Avg_Waiting_Time'].expanding().mean()
    
    fig_conv = go.Figure()
    fig_conv.add_trace(go.Scatter(
        x=metrics_df['Iteration'],
        y=running_avg,
        mode='lines',
        name='Running Average',
        line=dict(color='#667eea', width=2)
    ))
    fig_conv.add_hline(y=aggregated['Avg_Waiting_Time'], line_dash="dash",
                       line_color="#f5576c",
                       annotation_text=f"Final: {aggregated['Avg_Waiting_Time']:.4f}s")
    fig_conv.update_layout(
        title="Konvergensi Running Average — Avg Waiting Time",
        xaxis_title="Iterasi",
        yaxis_title="Running Average Waiting Time (s)",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    st.plotly_chart(fig_conv, use_container_width=True)
    
    # ---- Detailed Metrics Table ----
    with st.expander("📋 Tabel Metrik Lengkap"):
        st.markdown("#### Aggregated Metrics")
        agg_table = pd.DataFrame([{
            'Metric': k.replace('_', ' '),
            'Value': f"{v:.4f}" if isinstance(v, float) else str(v)
        } for k, v in aggregated.items()])
        st.dataframe(agg_table, use_container_width=True, hide_index=True)
        
        st.markdown("#### Per-Iteration Metrics (Sample)")
        st.dataframe(metrics_df.head(20), use_container_width=True, hide_index=True)


# ======================== ABOUT MODEL PAGE ========================
elif page == "📐 About Model":
    st.markdown('<p class="section-header">📐 Tentang Model Simulasi</p>', unsafe_allow_html=True)
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # ---- Entitas ----
    st.markdown("### 🔷 Entitas Simulasi")
    st.markdown("""
    <div class="model-card">
        <table style="width:100%; border-collapse:collapse;">
            <tr style="border-bottom:2px solid rgba(102,126,234,0.3);">
                <th style="text-align:left; padding:12px; width:30%;">Entitas</th>
                <th style="text-align:left; padding:12px;">Deskripsi</th>
            </tr>
            <tr style="border-bottom:1px solid rgba(102,126,234,0.1);">
                <td style="padding:12px;"><strong>Transaction</strong></td>
                <td style="padding:12px;">Entitas utama yang merepresentasikan transaksi pembayaran digital yang masuk ke sistem untuk diverifikasi</td>
            </tr>
            <tr style="border-bottom:1px solid rgba(102,126,234,0.1);">
                <td style="padding:12px;"><strong>Verification Server</strong></td>
                <td style="padding:12px;">Server yang memproses verifikasi transaksi. Sistem memiliki 4 server identik yang bekerja paralel</td>
            </tr>
            <tr>
                <td style="padding:12px;"><strong>Queue</strong></td>
                <td style="padding:12px;">Antrian FIFO (First-In-First-Out) yang menampung transaksi saat semua server sibuk</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # ---- State ----
    st.markdown("### 🔄 State Transition")
    
    st.markdown("""
    <div class="model-card" style="text-align:center;">
        <div style="display:flex; align-items:center; justify-content:center; gap:16px; flex-wrap:wrap;">
            <div style="background:linear-gradient(135deg,#ffecd2,#fcb69f); padding:16px 32px; border-radius:12px; font-weight:700; color:#1a1a2e;">
                ⏳ Waiting
            </div>
            <div style="font-size:28px; color:#667eea;">→</div>
            <div style="background:linear-gradient(135deg,#667eea,#764ba2); padding:16px 32px; border-radius:12px; font-weight:700; color:white;">
                🔄 Verifying
            </div>
            <div style="font-size:28px; color:#667eea;">→</div>
            <div style="background:linear-gradient(135deg,#43e97b,#38f9d7); padding:16px 32px; border-radius:12px; font-weight:700; color:#1a1a2e;">
                ✅ Completed
            </div>
        </div>
        <p style="margin-top:16px; font-size:14px; opacity:0.7;">
            Transaksi berpindah dari Waiting ke Verifying ketika ada server tersedia,<br>
            dan dari Verifying ke Completed setelah durasi verifikasi selesai.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # ---- Events ----
    st.markdown("### ⚡ Event Types")
    
    ev_col1, ev_col2, ev_col3 = st.columns(3)
    with ev_col1:
        st.markdown("""
        <div class="model-card" style="text-align:center;">
            <h3>📥 Arrival</h3>
            <p>Transaksi baru tiba di sistem berdasarkan Interarrival Time</p>
        </div>
        """, unsafe_allow_html=True)
    with ev_col2:
        st.markdown("""
        <div class="model-card" style="text-align:center;">
            <h3>▶️ Service Start</h3>
            <p>Transaksi mulai diproses di server yang tersedia</p>
        </div>
        """, unsafe_allow_html=True)
    with ev_col3:
        st.markdown("""
        <div class="model-card" style="text-align:center;">
            <h3>✅ Service End</h3>
            <p>Verifikasi selesai, server dibebaskan</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # ---- Persamaan Matematis ----
    st.markdown("### 📐 Persamaan Matematis")
    
    st.markdown("""
    <div class="equation-block">
        <h4>1. Arrival Time (Waktu Kedatangan)</h4>
        <p style="font-size:18px; font-family:serif;">
            <em>Arrival<sub>i</sub> = Arrival<sub>i-1</sub> + IA<sub>i</sub></em>
        </p>
        <p>Dimana IA<sub>i</sub> adalah Interarrival Time transaksi ke-i. Arrival<sub>1</sub> = 0.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="equation-block">
        <h4>2. Start Time (Waktu Mulai Verifikasi)</h4>
        <p style="font-size:18px; font-family:serif;">
            <em>Start<sub>i</sub> = max(Arrival<sub>i</sub>, AvailableServer<sub>j</sub>)</em>
        </p>
        <p>Transaksi mulai diverifikasi pada waktu maksimal antara kedatangan transaksi dan waktu server j tersedia.</p>
        <ul>
            <li>Jika server tersedia lebih awal: mulai = waktu kedatangan</li>
            <li>Jika server sibuk: mulai = waktu server bebas (harus menunggu)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="equation-block">
        <h4>3. End Time (Waktu Selesai Verifikasi)</h4>
        <p style="font-size:18px; font-family:serif;">
            <em>End<sub>i</sub> = Start<sub>i</sub> + VT<sub>i</sub></em>
        </p>
        <p>Transaksi selesai pada waktu mulai ditambah durasi verifikasi (VT ~ Uniform[2, 6] detik).</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="equation-block">
        <h4>4. Waiting Time (Waktu Tunggu)</h4>
        <p style="font-size:18px; font-family:serif;">
            <em>Waiting<sub>i</sub> = Start<sub>i</sub> - Arrival<sub>i</sub></em>
        </p>
        <p>Lama transaksi menunggu di antrian sebelum diproses.</p>
        <ul>
            <li>Waiting<sub>i</sub> = 0 → transaksi langsung diproses (server tersedia)</li>
            <li>Waiting<sub>i</sub> &gt; 0 → transaksi harus menunggu (congestion)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="equation-block">
        <h4>5. Queue Length Dynamics</h4>
        <p style="font-size:18px; font-family:serif;">
            <em>Queue(t+1) = Queue(t) + Arrival(t) - Departure(t)</em>
        </p>
        <p>Panjang antrian berubah berdasarkan kedatangan (+1) dan keberangkatan (-1) transaksi.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="equation-block">
        <h4>6. Server Utilization</h4>
        <p style="font-size:18px; font-family:serif;">
            <em>Utilization = Σ VT<sub>i</sub> / (N<sub>server</sub> × T<sub>total</sub>) × 100%</em>
        </p>
        <p>Persentase waktu server digunakan dibandingkan total waktu simulasi × jumlah server.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # ---- Server Allocation ----
    st.markdown("### 🖥️ Server Allocation Strategy")
    st.markdown("""
    <div class="model-card">
        <h4>Earliest Available Server (EAS) + FCFS</h4>
        <ol>
            <li>Ketika transaksi tiba, sistem mencari server dengan <code>available_until</code> paling awal</li>
            <li>Jika server tersedia (available_until ≤ arrival_time), transaksi langsung diproses</li>
            <li>Jika semua server sibuk, transaksi masuk antrian dan diproses saat server pertama bebas</li>
            <li>Semua server identik dengan kapabilitas yang sama</li>
            <li>Scheduling mengikuti prinsip <strong>First-Come-First-Served</strong> (FCFS)</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # ---- Monte Carlo ----
    st.markdown("### 🎲 Monte Carlo Simulation")
    st.markdown("""
    <div class="model-card">
        <h4>Mengapa Monte Carlo?</h4>
        <p>Dalam sistem nyata, <strong>verification time bervariasi</strong> karena berbagai faktor:</p>
        <ul>
            <li>🌐 Network delay</li>
            <li>⚡ Server load variations</li>
            <li>🏦 Payment gateway latency</li>
        </ul>
        <p style="margin-top:12px;"><strong>Pendekatan Monte Carlo:</strong></p>
        <ol>
            <li>Ambil dataset base (interarrival time tetap)</li>
            <li>Randomize verification time setiap iterasi: VT ~ Uniform(2, 6) detik</li>
            <li>Jalankan DES untuk setiap set VT yang baru</li>
            <li>Ulangi 1000 kali (atau sesuai parameter)</li>
            <li>Aggregate hasil untuk mendapatkan distribusi metrik</li>
        </ol>
        <p style="margin-top:12px;">Dengan 1000 iterasi, kita mendapatkan <strong>distribusi probabilistik</strong> dari metrik kinerja, 
        bukan hanya satu titik estimasi. Ini memungkinkan analisis <strong>confidence interval</strong>, 
        <strong>worst-case scenario</strong>, dan <strong>probabilitas kejadian</strong>.</p>
    </div>
    """, unsafe_allow_html=True)
