def generate_recommendations(metrics):
    recs = []

    # Database efficiency metrics
    if metrics.get('buffer_cache_hit_ratio', 100) < 90:
        recs.append("🔧 Low buffer cache hit ratio. Increase DB_CACHE_SIZE.")

    if metrics.get('parse_calls', 0) > 300:
        recs.append("🔧 High parse calls. Enable cursor sharing and bind variables.")

    if metrics.get('library_hit_pct', 100) < 95:
        recs.append("🔧 Low library cache efficiency. Tune shared pool size or reduce parsing.")

    if metrics.get('soft_parse_pct', 100) < 90:
        recs.append("🔧 Low soft parse ratio. Optimize application to use bind variables.")
    
    if metrics.get('hard_parses', 0) > 100:
        recs.append("🔧 Excessive hard parsing. Check bind variables or use CURSOR_SHARING=FORCE.")

    # Memory metrics
    if metrics.get('shared_pool_free_percent', 100) < 10:
        recs.append("🔧 Low free space in shared pool. Consider increasing SHARED_POOL_SIZE.")

    if metrics.get('memory_usage_pct', 0) > 90:
        recs.append("🔧 High memory usage. Investigate memory-intensive processes.")
    
    if metrics.get('pga_cache_hit_percent', 100) < 60:
        recs.append("🔧 Low PGA cache hit. Increase PGA_AGGREGATE_TARGET.")

    # I/O metrics
    if metrics.get('physical_reads', 0) > 10000:
        recs.append("🔧 High physical reads. Investigate inefficient SQL or missing indexes.")

    if metrics.get('physical_writes', 0) > 10000:
        recs.append("🔧 High physical writes. Optimize write operations and checkpointing.")
    
    if metrics.get('redo_size_bytes', 0) > 10000000:  # 10 MB
        recs.append("🔧 High redo generation. Investigate frequent DMLs or logging overhead.")

    # CPU and timing metrics
    if metrics.get('cpu_utilization_pct', 0) > 80:
        recs.append("🔧 High CPU usage. Identify CPU-intensive SQL or processes.")

    if metrics.get('db_time_ratio', 0) > 90:
        recs.append("🔧 High DB Time. Investigate top wait events and SQLs.")

    if metrics.get('sql_response_time', 0) > 1:
        recs.append("🔧 Poor SQL response time. Check indexes and joins.")

    # Concurrency and contention
    if metrics.get('enqueue_waits', 0) > 0:
        recs.append("🔧 Enqueue waits detected. Investigate object contention.")

    if metrics.get('latch_misses', 0) > 100:
        recs.append("🔧 High latch misses. Tune latch-related parameters or reduce contention.")

    if metrics.get('log_file_sync', 0) > 10:
        recs.append("🔧 High log file sync time. Check I/O performance or commit frequency.")

    # Transaction metrics
    if metrics.get('user_commits', 0) < metrics.get('user_rollbacks', 1):
        recs.append("🔧 Rollbacks are more than commits. Investigate transaction failures.")

    if metrics.get('transaction_count', 0) > 5000:
        recs.append("🔧 High transaction volume. Consider batching operations.")

    # SQL execution metrics
    if metrics.get('full_table_scans', 0) > 1000:
        recs.append("🔧 Many full table scans. Investigate missing indexes or rewrite queries.")

    if metrics.get('top_sql_buffer_gets', 0) > 100000:
        recs.append("🔧 SQL with high buffer gets. Tune expensive queries.")

    if metrics.get('sorts_disk', 0) > 1000:
        recs.append("🔧 High disk sorts. Increase SORT_AREA_SIZE or use temporary tablespaces.")

    if metrics.get('memory_sort_percent', 100) < 80:
        recs.append("🔧 Most sorts not in memory. Increase workarea_size_policy or PGA.")

    # Storage and configuration
    if metrics.get('db_files', 0) > 1000:
        recs.append("🔧 Too many database files. Could affect startup time and file I/O.")

    if metrics.get('log_switches', 0) > 30:
        recs.append("🔧 Frequent log switches. Consider increasing log file size.")

    if metrics.get('checkpoint_time', 0) > 5:
        recs.append("🔧 Long checkpoints. Tune checkpoint parameters or log buffer.")

    if metrics.get('log_file_parallel_write', 0) > 10:
        recs.append("🔧 Slow log writes. Investigate redo log disk I/O.")

    # Top wait events analysis
    top_wait = metrics.get('top_wait_event', "")
    if top_wait == "db file sequential read":
        recs.append("🔧 Index reads dominating. Investigate slow I/O on indexed reads.")
    elif top_wait == "db file scattered read":
        recs.append("🔧 Full table scans common. Check missing indexes.")
    elif top_wait == "log file sync":
        recs.append("🔧 COMMIT frequency too high. Use batch processing.")
    elif top_wait == "buffer busy waits":
        recs.append("🔧 Buffer contention. Tune hot blocks or increase freelists.")
    elif top_wait == "enq: TX - row lock contention":
        recs.append("🔧 Row lock contention. Optimize transaction design and commit frequency.")

    # Connection metrics
    if metrics.get('logons', 0) > 100:
        recs.append("🔧 High connection rate. Implement connection pooling.")

    if metrics.get('session_count', 0) > 500:
        recs.append("🔧 High session count. Review connection management and pooling.")

    # If no issues found
    if not recs:
        recs.append("✅ No critical performance issues detected.")

    return recs
