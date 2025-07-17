def generate_recommendations(metrics):
    recs = []
    
    # Critical validation check
    cpu_util = metrics.get('cpu_utilization_pct', 0)
    core_count = metrics.get('cpu_cores', 1)
    max_possible = core_count * 100 * 1.2  # 20% buffer
    
    if cpu_util > max_possible:
        recs.append("🚨 CRITICAL: Impossible CPU utilization value detected!")
        recs.append("🔧 Immediate Action: Verify AWR report parsing logic")
        recs.append(f"📊 Details: Reported {cpu_util}% (Max possible: {max_possible}%)")
        # Don't return - continue processing other metrics
    
    # Database efficiency metrics
    if metrics.get('buffer_cache_hit_ratio', 100) < 90:
        recs.append("🔧 Low buffer cache hit ratio. Increase DB_CACHE_SIZE.")
    
    # ... rest of your rules ...
    
    # CPU-specific recommendations (only if value is valid)
    if cpu_util <= max_possible:
        if cpu_util > 80:
            recs.append("⚠️ High CPU usage. Identify CPU-intensive SQL or processes.")
        elif cpu_util < 5:
            recs.append("ℹ️ Low CPU utilization. System may be underutilized.")
    
    if not recs:
        recs.append("✅ No critical performance issues detected.")
    
    return recs
