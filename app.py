import streamlit as st
import pandas as pd
import plotly.express as px
from parser import extract_metrics, extract_top_sql
from rules import generate_recommendations
from datetime import datetime
import re

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

# File uploader
with st.container():
    st.subheader("📤 Upload AWR Report", divider='blue')
    uploaded_file = st.file_uploader(
        "Drag and drop your AWR HTML report here",
        type=["html", "htm"],
        accept_multiple_files=False,
        help="Max file size: 200MB",
        label_visibility="collapsed"
    )

if uploaded_file is not None:
    html_text = uploaded_file.read().decode("utf-8")
    
    # Debugging: Allow viewing raw HTML
    with st.expander("🔍 View Raw HTML", expanded=False):
        st.code(html_text[:5000] + "\n\n... [truncated] ...", language='html')

    # Extract and show metrics
    with st.expander("📈 Extracted Metrics", expanded=True):
        metrics = extract_metrics(html_text)
        
        # Add validation checks
        if metrics.get('buffer_cache_hit_ratio', 0) == 0 and metrics.get('physical_reads', 0) > 0:
            st.error("⚠️ Impossible buffer cache hit ratio detected! Parsing may be incomplete")
        if metrics.get('cpu_utilization_pct', -1) == 0:
            st.warning("⚠️ 0% CPU utilization detected. Verify parsing logic")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Buffer Cache Hit %", f"{metrics.get('buffer_cache_hit_ratio', 0)}%", 
                     help="Should be > 90%", delta=None)
            st.metric("Physical Reads", f"{metrics.get('physical_reads', 0):,}")
            st.metric("CPU Utilization %", f"{metrics.get('cpu_utilization_pct', 0)}%", 
                     help="User + System CPU %")
        with col2:
            st.metric("Library Cache Hit %", f"{metrics.get('library_hit_pct', 0)}%", 
                     help="Should be > 95%")
            st.metric("Physical Writes", f"{metrics.get('physical_writes', 0):,}")
        with col3:
            st.metric("Memory Usage %", f"{metrics.get('memory_usage_pct', 0)}%")
            st.metric("User Calls", f"{metrics.get('user_calls', 0):,}")

        with st.expander("View all extracted metrics"):
            st.json(metrics)

    # Debugging panel
    with st.expander("🐞 Debugging Tools", expanded=False):
        st.subheader("Pattern Matching Results")
        
        # Buffer Cache Hit Ratio pattern
        buffer_pattern = r'Buffer\s+Hit\s+%\s*:\s*([\d.]+)'
        buffer_match = re.search(buffer_pattern, html_text)
        st.code(f"Buffer Pattern: {buffer_pattern}")
        st.write(f"Match Found: {bool(buffer_match)}")
        if buffer_match:
            st.write(f"Matched Value: {buffer_match.group(1)}")
        
        # CPU Idle pattern
        idle_pattern = r'%Idle\s*([\d.]+)'
        idle_match = re.search(idle_pattern, html_text)
        st.code(f"Idle Pattern: {idle_pattern}")
        st.write(f"Match Found: {bool(idle_match)}")
        if idle_match:
            st.write(f"Matched Value: {idle_match.group(1)}")
        
        # Show sample of AWR content
        st.subheader("AWR Content Sample")
        st.text(html_text[:2000] + "\n\n... [truncated] ...")

    # Charts
    with st.container():
        st.subheader("📊 Performance Visualizations", divider='blue')
        
        # Create a better structured dataframe for visualization
        display_metrics = {
            "Buffer Cache Hit %": metrics.get('buffer_cache_hit_ratio', 0),
            "Library Cache Hit %": metrics.get('library_hit_pct', 0),
            "Memory Usage %": metrics.get('memory_usage_pct', 0),
            "CPU Utilization %": metrics.get('cpu_utilization_pct', 0),
            "Physical Reads": metrics.get('physical_reads', 0),
            "Physical Writes": metrics.get('physical_writes', 0),
            "User Calls": metrics.get('user_calls', 0)
        }
        df = pd.DataFrame(list(display_metrics.items()), columns=['Metric', 'Value'])

        tab1, tab2 = st.tabs(["Bar Chart", "Pie Chart"])
        with tab1:
            fig = px.bar(df, x="Metric", y="Value", color="Value", 
                         title="Database Metrics Overview",
                         color_continuous_scale='Bluered')
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            percent_metrics = {k: v for k, v in display_metrics.items() if 0 < v <= 100}
            if percent_metrics:
                pie_df = pd.DataFrame(list(percent_metrics.items()), columns=["Metric", "Value"])
                pie_fig = px.pie(pie_df, names="Metric", values="Value", hole=0.3, 
                                title="Percentage Metrics")
                st.plotly_chart(pie_fig, use_container_width=True)
            else:
                st.warning("No percentage-based metrics found")

    # SQL Section
    with st.container():
        st.subheader("🧠 Top SQL Analysis", divider='blue')
        top_sql = extract_top_sql(html_text)

        if top_sql:
            top_sql_df = pd.DataFrame(top_sql)
            st.dataframe(top_sql_df.style.highlight_max(axis=0, color='#d4f1f9'), 
                        use_container_width=True)
            st.plotly_chart(
                px.bar(top_sql_df, x="SQL ID", y="Executions", 
                      color="Elapsed Time (s)", title="Top SQL Queries"),
                use_container_width=True
            )
        else:
            st.warning("No Top SQL data found in the AWR report", icon="⚠️")

    # Recommendations
    with st.container():
        st.subheader("💡 Optimization Recommendations", divider='blue')
        recs = generate_recommendations(metrics)

        if recs:
            for rec in recs:
                if "Investigate" in rec or "High" in rec:
                    st.warning(rec, icon="⚠️")
                elif "Increase" in rec or "Tune" in rec:
                    st.info(rec, icon="ℹ️")
                else:
                    st.success(rec, icon="✅")
        else:
            st.success("✅ No critical performance issues detected")

    # AI Assistant (Simple rule-based)
    with st.expander("🤖 Chat with AWR AI Agent"):
        user_query = st.text_input("Ask about performance, metrics, or SQL:")
        
        def ai_agent(query, metrics):
            query = query.lower()
            if "buffer cache" in query:
                return f"The Buffer Cache Hit Ratio is {metrics.get('buffer_cache_hit_ratio', 'N/A')}%. Consider increasing DB_CACHE_SIZE if it's below 90%."
            elif "parse" in query:
                return f"Total Parse Calls: {metrics.get('parse_calls', 'N/A')}. High parse calls may mean missing bind variables."
            elif "library cache" in query:
                return f"Library Cache Hit Ratio is {metrics.get('library_hit_pct', 'N/A')}%. Should be above 95%."
            elif "sql" in query:
                return "Check the Top SQL Analysis section for detailed execution metrics."
            elif "memory" in query:
                return f"Memory Usage is {metrics.get('memory_usage_pct', 'N/A')}%. High usage may impact performance."
            elif "cpu" in query:
                return f"CPU Utilization is {metrics.get('cpu_utilization_pct', 'N/A')}%. If it's too high, consider checking for inefficient SQL or contention."
            elif "summary" in query or "analysis" in query:
                return "The report shows key metrics for performance tuning. Review buffer cache, parse calls, and I/O activity."
            else:
                return "I'm still learning. Try asking about cache hit ratio, parse calls, memory, or SQL analysis."

        if user_query:
            st.info(ai_agent(user_query, metrics))

# Toggle Developer Info
if st.button("👨‍💻 Show Developer Info"):
    with st.container():
        st.subheader("👨‍💼 Developer & Internship Details", divider="gray")
        st.markdown("""
        <div class='developer-info'>
        <b>Developed By:</b><br>
        Mukesh Prashant Kundu<br>
        📧 <a href="mailto:mukesh.kundu009@gmail.com">mukesh.kundu009@gmail.com</a><br><br>

        Nimisha Khairnar<br>
        📧 <a href="mailto:nimishamkhairnar@gmail.com">nimishamkhairnar@gmail.com</a><br><br>

        <b>Research Internship:</b><br>
        AMARRTHATECH PRIVATE LIMITED<br>
        (U62099PN2025PTC238967)<br><br>

        <b>Mentor:</b><br>
        Mahesh Khairnar<br>
        Director, AMARRTHATECH
        </div>
        """, unsafe_allow_html=True)

        if uploaded_file:
            st.markdown("---")
            st.subheader("📄 Report Info", divider="gray")
            st.caption(f"📎 Filename: `{uploaded_file.name}`")
            st.caption(f"📦 Size: {round(uploaded_file.size / 1024 / 1024, 2)} MB")
        st.caption(f"📅 Analyzed on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# Footer
st.divider()
st.caption("AMARRTHATECH PRIVATE LIMITED 2025 | All rights reserved")
