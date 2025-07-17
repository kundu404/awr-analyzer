from bs4 import BeautifulSoup
import re
from datetime import datetime

def extract_metrics(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    metrics = {}
    
    # 1. Extract snapshot duration from 'Begin Snap:' and 'End Snap:' rows
    snap_begin = None
    snap_end = None
    for row in soup.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) >= 3:
            label = cells[0].get_text(strip=True)
            if label.startswith('Begin Snap:'):
                snap_begin = cells[2].get_text(strip=True)
            elif label.startswith('End Snap:'):
                snap_end = cells[2].get_text(strip=True)
        if snap_begin and snap_end:
            break

    snap_duration = 1800  # default to 30 minutes
    if snap_begin and snap_end:
        # Example format: 16-Jan-25 11:30:26
        try:
            start_time = datetime.strptime(snap_begin, "%d-%b-%y %H:%M:%S")
            end_time = datetime.strptime(snap_end, "%d-%b-%y %H:%M:%S")
            snap_duration = (end_time - start_time).total_seconds()
            if snap_duration < 0:
                # Handle day wrap (if end is after midnight)
                snap_duration += 86400
            metrics['snap_duration_seconds'] = snap_duration
        except Exception as e:
            pass
    
    # 2. Extract CPU cores from host info table (CPUs column)
    cpu_cores = 1
    found_host_table = False
    for table in soup.find_all('table'):
        headers = [th.get_text(strip=True) for th in table.find_all('th')]
        if 'CPUs' in headers and 'Cores' in headers:
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 3:
                    try:
                        cpus_val = cells[2].get_text(strip=True)
                        if cpus_val:
                            cpu_cores = int(cpus_val)
                            metrics['cpu_cores'] = cpu_cores
                            found_host_table = True
                            break
                    except Exception:
                        continue
        if found_host_table:
            break
    # Fallback: regex if table not found
    if not found_host_table:
        cpu_pattern = re.compile(r"CPUs:\s*(\d+)")
        cpu_match = cpu_pattern.search(html_text)
        if cpu_match:
            try:
                cpu_cores = int(cpu_match.group(1))
                metrics['cpu_cores'] = cpu_cores
            except:
                pass
    
    # 3. Extract metrics from tables
    for row in soup.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) >= 2:
            label = cells[0].get_text(strip=True)
            value = cells[1].get_text(strip=True).replace(',', '')

            try:
                # Handle percentage values
                if '%' in value:
                    value = float(value.replace('%', ''))
                # Handle large numbers with suffixes
                elif value.upper().endswith('K'):
                    value = float(value.upper().replace('K', '')) * 1000
                elif value.upper().endswith('M'):
                    value = float(value.upper().replace('M', '')) * 1_000_000
                elif value.upper().endswith('G'):
                    value = float(value.upper().replace('G', '')) * 1_000_000_000
                else:
                    value = float(value)
                
                # Map labels to metric names
                metric_map = {
                    'Buffer  Hit   %': 'buffer_cache_hit_ratio',
                    'Library Hit   %': 'library_hit_pct',
                    'Memory Usage %': 'memory_usage_pct',
                    'Physical read (blocks)': 'physical_reads',
                    'Physical write (blocks)': 'physical_writes',
                    'User calls': 'user_calls',
                    'DB CPU': 'db_cpu_seconds',  # Changed to seconds
                    '%Total CPU': 'cpu_utilization_pct',
                    'CPU Utilization %': 'cpu_utilization_pct',
                    'Parse Calls': 'parse_calls',
                    'Redo size (bytes)': 'redo_size_bytes',
                    'Logical read (blocks)': 'logical_reads',
                    'Hard parses (SQL)': 'hard_parses',
                    'Soft Parse %': 'soft_parse_pct',
                    'Latch Hit %': 'latch_hit_pct',
                    'SQL Work Area (MB)': 'sql_work_area_mb',
                    'Executions': 'executions',
                    'Logons:': 'logons',
                    '%Idle': 'cpu_idle_pct'
                }
                
                # Assign value to metric if label matches
                for pattern, metric_name in metric_map.items():
                    if pattern in label:
                        metrics[metric_name] = value
                        break

            except ValueError:
                continue
    
    # 4. Calculate real CPU utilization
    db_cpu_seconds = metrics.get('db_cpu_seconds', 0)
    cpu_idle_pct = metrics.get('cpu_idle_pct', 100)
    
    # First try: Use idle percentage if available
    if 'cpu_idle_pct' in metrics:
        metrics['cpu_utilization_pct'] = 100 - cpu_idle_pct
    # Second try: Calculate from DB CPU seconds
    elif db_cpu_seconds > 0 and snap_duration > 0 and cpu_cores > 0:
        # Utilization = (CPU seconds / duration) / cores * 100
        utilization = (db_cpu_seconds / snap_duration) / cpu_cores * 100
        metrics['cpu_utilization_pct'] = round(utilization, 2)
    
    return metrics


def extract_top_sql(html_text):
    """
    Placeholder for extracting top SQL statements from AWR HTML.
    Returns an empty list. Implement actual logic as needed.
    """
    return []
