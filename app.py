import streamlit as st
import pandas as pd
import plotly.express as px
from parser import extract_metrics, extract_top_sql
from rules import generate_recommendations
from datetime import datetime

# Initialize uploaded_file to None at the top level
uploaded_file = None

# Page setup
st.set_page_config(
    page_title="AWR Report Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {padding: 2rem 3rem;}
    .header {color: #2c3e50; border-bottom: 1px solid #eee; margin-bottom: 1rem;}
    .metric-box {border-radius: 10px; padding: 15px; background: #f8f9fa; margin-bottom: 15px;}
    .stAlert {padding: 15px; border-radius: 8px;}
    .developer-info {font-size: 0.9rem; line-height: 1.5;}
    .debug-panel {background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-top: 20px;}
</style>
""", unsafe_allow_html=True)

# Title
st.title("📊 Oracle AWR Report Analyzer")
st.caption("Upload your Automatic Workload Repository (AWR) report for performance analysis and recommendations")

# File uploader - MOVE TO TOP LEVEL SCOPE
uploaded_file = st.file_uploader(
    "Drag and drop your AWR HTML report here",
    type=["html", "htm"],
    accept_multiple_files=False,
    help="Max file size: 200MB",
    label_visibility="collapsed"
)

if uploaded_file is not None:
    html_text = uploaded_file.read().decode("utf-8")
    
    # Extract and show metrics
    with st.expander("📈 Extracted Metrics", expanded=True):
        metrics = extract_metrics(html_text)
        
        # Add validation checks
        if metrics.get('buffer_cache_hit_ratio', 0) == 0 and metrics.get('physical_reads', 0) > 0:
            st.error("⚠️ Impossible buffer cache hit ratio detected! Parsing may be incomplete")
        
        # CPU validation
        cpu_util = metrics.get('cpu_utilization_pct', -1)
        cpu_cores = metrics.get('cpu_cores', 1)
        max_possible = cpu_cores * 100 * 1.2  # 20% buffer
        
        if cpu_util > max_possible:
            st.error(f"⚠️ Invalid CPU utilization ({cpu_util}%). Using alternative calculation.")
            # Attempt to calculate from idle percentage
            if 'cpu_idle_pct' in metrics:
                metrics['cpu_utilization_pct'] = 100 - metrics['cpu_idle_pct']
            # Or calculate from DB CPU seconds
            elif 'db_cpu_seconds' in metrics and 'snap_duration_seconds' in metrics:
                db_cpu = metrics['db_cpu_seconds']
                duration = metrics['snap_duration_seconds']
                metrics['cpu_utilization_pct'] = round((db_cpu / duration) / cpu_cores * 100, 2)
            else:
                metrics['cpu_utilization_pct'] = 0  # Default to 0 if all fails
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Buffer Cache Hit %", f"{metrics.get('buffer_cache_hit_ratio', 0)}%", 
                     help="Should be > 90%")
            st.metric("Physical Reads", f"{metrics.get('physical_reads', 0):,}")
            st.metric("CPU Utilization %", 
                     f"{metrics.get('cpu_utilization_pct', 0)}%",
                     help=f"Based on {cpu_cores} cores")
        
        with col2:
            st.metric("Library Cache Hit %", f"{metrics.get('library_hit_pct', 0)}%", 
                     help="Should be > 95%")
            st.metric("Physical Writes", f"{metrics.get('physical_writes', 0):,}")
            st.metric("DB CPU Seconds", f"{metrics.get('db_cpu_seconds', 0):,}",
                     help="Cumulative CPU time")
        
        with col3:
            st.metric("Memory Usage %", f"{metrics.get('memory_usage_pct', 0)}%")
            st.metric("User Calls", f"{metrics.get('user_calls', 0):,}")
            st.metric("Snapshot Duration", 
                     f"{metrics.get('snap_duration_seconds', 0):,} sec",
                     help="AWR report time period")
        
        with st.expander("View all extracted metrics"):
            st.json(metrics)
    
    # ... rest of the code remains the same ...

# Toggle Developer Info
if st.button("👨‍💻 Show Developer Info"):
    # ... developer info code ...
    pass

# Footer
st.divider()
st.caption("AMARRTHATECH PRIVATE LIMITED 2025 | All rights reserved")
