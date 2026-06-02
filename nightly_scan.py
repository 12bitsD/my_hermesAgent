#!/usr/bin/env python3
"""
Hermes Nightly Scan — 每天 21:00 自动扫描当天 session
输出: 当日摘要 + 发现的问题 + 改进建议
"""

import sqlite3
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta

DB_PATH = os.path.expanduser("~/.hermes/state.db")
BRAIN_DIR = os.path.expanduser("~/Desktop/hermes-brain")
REPORT_DIR = os.path.join(BRAIN_DIR, "reports")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_today_sessions(conn):
    """获取今天的所有 session"""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_ts = today.timestamp()
    
    sessions = conn.execute("""
        SELECT * FROM sessions 
        WHERE started_at >= ? AND message_count > 0
        ORDER BY started_at
    """, (today_ts,)).fetchall()
    return sessions

def get_session_messages(conn, session_id):
    """获取 session 的所有消息"""
    return conn.execute("""
        SELECT * FROM messages 
        WHERE session_id = ? 
        ORDER BY timestamp
    """, (session_id,)).fetchall()

def analyze_session(conn, session):
    """分析单个 session，返回发现"""
    sid = session['id']
    messages = get_session_messages(conn, sid)
    
    user_msgs = [m for m in messages if m['role'] == 'user']
    assistant_msgs = [m for m in messages if m['role'] == 'assistant']
    tool_msgs = [m for m in messages if m['role'] == 'tool']
    
    findings = []
    
    # 1. 检测用户纠正
    correction_keywords = {
        'stop': ['怎么停了', '为什么停了', '怎么不继续', '停了'],
        'direction': ['跑偏了', '不对', '错了', '不是这样'],
        'push': ['git push', 'push'],
        'quality': ['太复古', '太简', '不够', '浓度'],
    }
    
    corrections = []
    for m in user_msgs:
        content = m['content'] or ''
        for cat, keywords in correction_keywords.items():
            if any(kw in content for kw in keywords):
                corrections.append((cat, content[:100]))
                break
    
    if corrections:
        findings.append({
            'type': 'user_corrections',
            'severity': 'high' if len(corrections) > 3 else 'medium',
            'detail': f"{len(corrections)} 次用户纠正",
            'items': corrections,
        })
    
    # 2. 检测空响应率
    total_a = len(assistant_msgs) or 1
    empty = sum(1 for m in assistant_msgs if not m['content'] or m['content'].strip() == '')
    empty_rate = empty / total_a
    
    if empty_rate > 0.3:
        findings.append({
            'type': 'high_empty_rate',
            'severity': 'medium',
            'detail': f"空响应率 {empty_rate:.0%} ({empty}/{total_a})",
        })
    
    # 3. 检测 tool 错误率
    tool_errors = sum(1 for m in tool_msgs if m['content'] and 'error' in (m['content'] or '').lower())
    total_tools = len(tool_msgs) or 1
    error_rate = tool_errors / total_tools
    
    if error_rate > 0.2:
        findings.append({
            'type': 'high_tool_error_rate',
            'severity': 'high' if error_rate > 0.3 else 'medium',
            'detail': f"Tool 错误率 {error_rate:.0%} ({tool_errors}/{len(tool_msgs)})",
        })
    
    # 4. 检测重复模式
    tool_seq = [m['tool_name'] for m in messages if m['role'] == 'tool' and m['tool_name']]
    if len(tool_seq) > 20:
        # 检测连续相同 tool
        consecutive = 0
        max_consecutive = 0
        for i in range(1, len(tool_seq)):
            if tool_seq[i] == tool_seq[i-1]:
                consecutive += 1
                max_consecutive = max(max_consecutive, consecutive)
            else:
                consecutive = 0
        
        if max_consecutive > 10:
            findings.append({
                'type': 'repetitive_tool_pattern',
                'severity': 'low',
                'detail': f"最长连续相同 tool: {max_consecutive} 次 ({tool_seq[0] if tool_seq else 'unknown'})",
            })
    
    # 5. 检测长 session 无汇报
    if len(user_msgs) > 0 and len(assistant_msgs) > 20:
        replies_per_user = len(assistant_msgs) / len(user_msgs)
        if replies_per_user > 15:
            findings.append({
                'type': 'low_user_engagement',
                'severity': 'medium',
                'detail': f"用户消息 {len(user_msgs)} 条，agent 回复 {len(assistant_msgs)} 条 (1:{replies_per_user:.0f})",
            })
    
    return findings

def generate_report(conn, sessions, date_str):
    """生成当日报告"""
    all_findings = []
    session_summaries = []
    
    for session in sessions:
        findings = analyze_session(conn, session)
        all_findings.extend(findings)
        
        # Session 摘要
        title = session['title'] or '(untitled)'
        session_summaries.append({
            'id': session['id'],
            'title': title[:50],
            'model': session['model'],
            'messages': session['message_count'],
            'tools': session['tool_call_count'],
            'input_k': f"{session['input_tokens']/1000:.0f}",
            'output_k': f"{session['output_tokens']/1000:.0f}",
            'findings': len(findings),
        })
    
    # 统计发现类型
    finding_types = Counter(f['type'] for f in all_findings)
    high_severity = [f for f in all_findings if f['severity'] == 'high']
    
    # 生成 summary.md
    summary_lines = [
        f"# Daily Summary — {date_str}",
        f"",
        f"## Sessions",
        f"",
        f"| ID | Title | Model | Msgs | Tools | In(K) | Out(K) | Findings |",
        f"|-----|-------|-------|------|-------|-------|--------|----------|",
    ]
    for s in session_summaries:
        summary_lines.append(
            f"| {s['id'][:20]} | {s['title']} | {s['model']} | {s['messages']} | {s['tools']} | {s['input_k']} | {s['output_k']} | {s['findings']} |"
        )
    
    summary_lines.extend([
        f"",
        f"## Overall",
        f"",
        f"- Total sessions: {len(sessions)}",
        f"- Total findings: {len(all_findings)}",
        f"- High severity: {len(high_severity)}",
        f"",
    ])
    
    # 生成 findings.md
    findings_lines = [
        f"# Findings — {date_str}",
        f"",
        f"## Finding Types",
        f"",
    ]
    for ftype, count in finding_types.most_common():
        findings_lines.append(f"- {ftype}: {count}")
    
    findings_lines.extend([
        f"",
        f"## High Severity",
        f"",
    ])
    for f in high_severity:
        findings_lines.append(f"### {f['type']}")
        findings_lines.append(f"- Detail: {f['detail']}")
        if 'items' in f:
            for item in f['items'][:5]:
                findings_lines.append(f"  - [{item[0]}] {item[1]}")
        findings_lines.append("")
    
    findings_lines.extend([
        f"## All Findings",
        f"",
    ])
    for f in all_findings:
        severity_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(f['severity'], '⚪')
        findings_lines.append(f"- {severity_icon} **{f['type']}**: {f['detail']}")
    
    return '\n'.join(summary_lines), '\n'.join(findings_lines)

def main():
    date_str = datetime.now().strftime('%Y-%m-%d')
    report_dir = os.path.join(REPORT_DIR, date_str)
    os.makedirs(report_dir, exist_ok=True)
    
    conn = get_db()
    sessions = get_today_sessions(conn)
    
    if not sessions:
        # 没有今天的 session，分析最近的
        print(f"No sessions found for {date_str}, analyzing last 7 days...")
        week_ago = (datetime.now() - timedelta(days=7)).timestamp()
        sessions = conn.execute("""
            SELECT * FROM sessions 
            WHERE started_at >= ? AND message_count > 0
            ORDER BY started_at DESC
            LIMIT 50
        """, (week_ago,)).fetchall()
    
    print(f"Analyzing {len(sessions)} sessions...")
    
    summary, findings = generate_report(conn, sessions, date_str)
    
    # 写入报告
    summary_path = os.path.join(report_dir, "summary.md")
    findings_path = os.path.join(report_dir, "findings.md")
    
    with open(summary_path, 'w') as f:
        f.write(summary)
    with open(findings_path, 'w') as f:
        f.write(findings)
    
    print(f"Reports written to {report_dir}/")
    print(f"  - summary.md")
    print(f"  - findings.md")
    
    # 同时输出到 stdout 供 cron delivery
    print(f"\n{'='*60}")
    print(findings)
    
    conn.close()

if __name__ == '__main__':
    main()
