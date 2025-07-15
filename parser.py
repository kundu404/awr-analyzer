from bs4 import BeautifulSoup

def extract_metrics(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    metrics = {}

    for row in soup.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) >= 2:
            label = cells[0].get_text(strip=True)
            value = cells[1].get_text(strip=True).replace(',', '')

            try:
                if '%' in value:
                    value = float(value.replace('%', ''))
                elif value.upper().endswith('K'):
                    value = float(value.upper().replace('K', '')) * 1000
                elif value.upper().endswith('M'):
                    value = float(value.upper().replace('M', '')) * 1_000_000
                elif value.upper().endswith('G'):
                    value = float(value.upper().replace('G', '')) * 1_000_000_000
                else:
                    value = float(value)

                if 'Buffer Cache Hit Ratio' in label:
                    metrics['buffer_cache_hit_ratio'] = value
                elif 'Parse Calls' in label:
                    metrics['parse_calls'] = value
                elif 'Redo size (bytes)' in label:
                    metrics['redo_size_bytes'] = value
                elif 'Logical read (blocks)' in label:
                    metrics['logical_reads'] = value
                elif 'Physical read (blocks)' in label:
                    metrics['physical_reads'] = value
                elif 'Physical write (blocks)' in label:
                    metrics['physical_writes'] = value
                elif 'User calls' in label:
                    metrics['user_calls'] = value
                elif 'Hard parses (SQL)' in label:
                    metrics['hard_parses'] = value
                elif 'Soft Parse %' in label:
                    metrics['soft_parse_pct'] = value
                elif 'Library Hit   %' in label:
                    metrics['library_hit_pct'] = value
                elif 'Latch Hit %' in label:
                    metrics['latch_hit_pct'] = value
                elif 'Memory Usage %' in label:
                    metrics['memory_usage_pct'] = value
                elif 'SQL Work Area (MB)' in label:
                    metrics['sql_work_area_mb'] = value
                elif 'Executions' in label:
                    metrics['executions'] = value
                elif 'Logons:' in label:
                    metrics['logons'] = value

            except ValueError:
                pass

    return metrics

def extract_top_sql(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    top_sql = []

    for table in soup.find_all('table'):
        headers = [th.get_text(strip=True) for th in table.find_all('th')]
        if 'SQL ID' in headers and 'Executions' in headers:
            for row in table.find_all('tr')[1:]:
                cells = row.find_all('td')
                if len(cells) >= 4:
                    try:
                        entry = {
                            'SQL ID': cells[0].get_text(strip=True),
                            'Executions': int(cells[1].get_text(strip=True).replace(',', '')),
                            'Elapsed Time (s)': float(cells[2].get_text(strip=True).replace(',', '')),
                            'CPU Time (s)': float(cells[3].get_text(strip=True).replace(',', ''))
                        }
                        top_sql.append(entry)
                    except:
                        continue
            break
    return top_sql
