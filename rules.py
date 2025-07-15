def generate_recommendations(metrics):
    recs = []

    if metrics.get('buffer_cache_hit_ratio', 100) < 90:
        recs.append("🔧 Low buffer cache hit ratio. Increase DB_CACHE_SIZE.")

    if metrics.get('parse_calls', 0) > 300:
        recs.append("🔧 High parse calls. Enable cursor sharing and bind variables.")

    if metrics.get('library_cache_hit_ratio', 100) < 95:
        recs.append("🔧 Low library cache efficiency. Tune shared pool size or reduce parsing.")

    if metrics.get('shared_pool_free_percent', 100) < 10:
        recs.append("🔧 Low free space in shared pool. Consider increasing SHARED_POOL_SIZE.")

    if metrics.get('physical_reads', 0) > 10000:
        recs.append("🔧 High physical reads. Investigate inefficient SQL or missing indexes.")

    if metrics.get('redo_size', 0) > 10000000:
        recs.append("🔧 High redo generation. Investigate frequent DMLs or logging overhead.")

    if metrics.get('sorts_disk', 0) > 1000:
        recs.append("🔧 High disk sorts. Increase SORT_AREA_SIZE or use temporary tablespaces.")

    if metrics.get('enqueue_waits', 0) > 0:
        recs.append("🔧 Enqueue waits detected. Investigate object contention.")

    if metrics.get('log_file_sync', 0) > 10:
        recs.append("🔧 High log file sync time. Check I/O performance or commit frequency.")

    if metrics.get('db_time_ratio', 0) > 90:
        recs.append("🔧 High DB Time. Investigate top wait events and SQLs.")

    if metrics.get('cpu_usage', 0) > 80:
        recs.append("🔧 High CPU usage. Identify CPU-intensive SQL or processes.")

    if metrics.get('user_commits', 0) < metrics.get('user_rollbacks', 1):
        recs.append("🔧 Rollbacks are more than commits. Investigate transaction failures.")

    if metrics.get('latch_misses', 0) > 100:
        recs.append("🔧 High latch misses. Tune latch-related parameters or reduce contention.")

    if metrics.get('cursor_cache_hits', 100) < 90:
        recs.append("🔧 Poor cursor reuse. Enable session cached cursors.")

    if metrics.get('pga_cache_hit_percent', 100) < 60:
        recs.append("🔧 Low PGA cache hit. Increase PGA_AGGREGATE_TARGET.")

    if metrics.get('hard_parses', 0) > 100:
        recs.append("🔧 Excessive hard parsing. Check bind variables or use CURSOR_SHARING=FORCE.")

    if metrics.get('full_table_scans', 0) > 1000:
        recs.append("🔧 Many full table scans. Investigate missing indexes or rewrite queries.")

    if metrics.get('top_sql_buffer_gets', 0) > 100000:
        recs.append("🔧 SQL with high buffer gets. Tune expensive queries.")

    if metrics.get('db_block_changes', 0) > 5000:
        recs.append("🔧 Too many block changes. Tune DML operations.")

    if metrics.get('log_file_parallel_write', 0) > 10:
        recs.append("🔧 Slow log writes. Investigate redo log disk I/O.")

    # Add 30 more similar rules below
    if metrics.get('db_files', 0) > 1000:
        recs.append("🔧 Too many database files. Could affect startup time and file I/O.")

    if metrics.get('db_cpu_percent', 0) > 90:
        recs.append("🔧 High DB CPU %. Investigate top CPU-consuming queries.")

    if metrics.get('sql_response_time', 0) > 1:
        recs.append("🔧 Poor SQL response time. Check indexes and joins.")

    if metrics.get('log_switches', 0) > 30:
        recs.append("🔧 Frequent log switches. Consider increasing log file size.")

    if metrics.get('checkpoint_time', 0) > 5:
        recs.append("🔧 Long checkpoints. Tune checkpoint parameters or log buffer.")

    if metrics.get('memory_sort_percent', 100) < 80:
        recs.append("🔧 Most sorts not in memory. Increase workarea_size_policy or PGA.")

    if metrics.get('top_wait_event') == "db file sequential read":
        recs.append("🔧 Index reads dominating. Investigate slow I/O on indexed reads.")

    if metrics.get('top_wait_event') == "db file scattered read":
        recs.append("🔧 Full table scans common. Check missing indexes.")

    if metrics.get('top_wait_event') == "log file sync":
        recs.append("🔧 COMMIT frequency too high. Use batch processing.")

    if metrics.get('top_wait_event') == "buffer busy waits":
        recs.append("🔧 Buffer contention. Tune hot blocks or increase freelists.")

    if not recs:
        recs.append("✅ No critical performance issues detected.")

    return recs
