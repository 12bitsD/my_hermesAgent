#!/usr/bin/env python3
"""
Hermes Session Analyzer — 从历史 session 中提取 Agent 行为模式
用法: python3 analyze_sessions.py [--session ID] [--top N] [--all]
"""

import sqlite3
import json
import sys
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone

DB_PATH = os.path.expanduser("~/.hermes/state.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def analyze_single_session(conn, session_id):
    """深度分析单个 session"""
    print(f"\n{'='*60}")
    print(f"  SESSION ANALYSIS: {session_id}")
    print(f"{'='*60}")
    
    # Session metadata
    row = conn.execute("SELECT * FROM sessions WHERE id=?", (session_id,)).fetchone()
    if not row:
        print(f"Session {session_id} not found")
        return
    
    print(f"\n  Model:    {row['model']}")
    print(f"  Source:   {row['source']}")
    print(f"  Messages: {row['message_count']}")
    print(f"  Tools:    {row['tool_call_count']}")
    print(f"  Input:    {row['input_tokens']/1000:.1f}K tokens")
    print(f"  Output:   {row['output_tokens']/1000:.1f}K tokens")
    print(f"  Cache R:  {row['cache_read_tokens']/1000:.1f}K tokens")
    started = datetime.fromtimestamp(row['started_at'])
    print(f"  Started:  {started.strftime('%Y-%m-%d %H:%M')}")
    
    # Get all messages
    messages = conn.execute(
        "SELECT * FROM messages WHERE session_id=? ORDER BY timestamp",
        (session_id,)
    ).fetchall()
    
    user_msgs = [m for m in messages if m['role'] == 'user']
    assistant_msgs = [m for m in messages if m['role'] == 'assistant']
    tool_msgs = [m for m in messages if m['role'] == 'tool']
    
    # === 1. User correction patterns ===
    print(f"\n  --- User Corrections ---")
    correction_patterns = {
        'stop/frustration': ['怎么停了', '为什么停了', '怎么不继续', '停了', '停下来'],
        'wrong direction': ['跑偏了', '不对', '错了', '不是这样'],
        'push/commit reminder': ['git push', 'push', '提交'],
        'keep going': ['继续', '不要停', '不要停下来', '一直前进'],
        'quality complaint': ['太复古', '太简', '不够', '浓度'],
    }
    
    corrections_found = []
    for m in user_msgs:
        content = m['content'] or ''
        for category, keywords in correction_patterns.items():
            if any(kw in content for kw in keywords):
                corrections_found.append((category, content[:150], m['timestamp']))
                break
    
    if corrections_found:
        for cat, content, ts in corrections_found:
            t = datetime.fromtimestamp(ts).strftime('%H:%M')
            print(f"    [{t}] {cat}: {content}...")
    else:
        print("    (none found)")
    
    # === 2. Empty/thin assistant responses ===
    print(f"\n  --- Assistant Response Quality ---")
    empty = sum(1 for m in assistant_msgs if not m['content'] or m['content'].strip() == '')
    thin = sum(1 for m in assistant_msgs if m['content'] and 0 < len(m['content'].strip()) < 50)
    compaction = sum(1 for m in assistant_msgs if m['content'] and 'CONTEXT COMPACTION' in m['content'])
    medium = sum(1 for m in assistant_msgs if m['content'] and 50 <= len(m['content'].strip()) < 200)
    long = sum(1 for m in assistant_msgs if m['content'] and len(m['content'].strip()) >= 200)
    
    total_a = len(assistant_msgs) or 1
    print(f"    Empty:    {empty:4d} ({empty/total_a*100:.0f}%)")
    print(f"    Thin(<50):{thin:4d} ({thin/total_a*100:.0f}%)")
    print(f"    Compaction:{compaction:4d}")
    print(f"    Medium:   {medium:4d} ({medium/total_a*100:.0f}%)")
    print(f"    Long:     {long:4d} ({long/total_a*100:.0f}%)")
    
    # === 3. Tool usage analysis ===
    print(f"\n  --- Tool Usage ---")
    tool_counter = Counter()
    tool_errors = 0
    for m in tool_msgs:
        if m['tool_name']:
            tool_counter[m['tool_name']] += 1
        content = m['content'] or ''
        if 'error' in content.lower() or 'Error' in content:
            tool_errors += 1
    
    for tool, count in tool_counter.most_common(15):
        print(f"    {tool:30s} {count:4d}")
    print(f"    ---")
    print(f"    Total tool calls:  {sum(tool_counter.values())}")
    print(f"    Tool errors:       {tool_errors}")
    
    # === 4. Conversation flow analysis ===
    print(f"\n  --- Conversation Flow ---")
    # Find user message clusters (time gaps > 5 min)
    user_timestamps = [m['timestamp'] for m in user_msgs]
    if len(user_timestamps) > 1:
        gaps = [(user_timestamps[i+1] - user_timestamps[i], i) 
                for i in range(len(user_timestamps)-1)]
        long_gaps = [(gap, idx) for gap, idx in gaps if gap > 300]  # > 5 min
        print(f"    User messages:     {len(user_msgs)}")
        print(f"    Assistant turns:   {len(assistant_msgs)}")
        print(f"    Replies per user msg: {len(assistant_msgs)/max(len(user_msgs),1):.1f}")
        if long_gaps:
            print(f"    Long pauses (>5min): {len(long_gaps)}")
            for gap, idx in long_gaps[:3]:
                t = datetime.fromtimestamp(user_timestamps[idx]).strftime('%H:%M')
                print(f"      at {t}: {gap/60:.0f} min gap")
    
    # === 5. Repetition detection ===
    print(f"\n  --- Repetition Detection ---")
    assistant_contents = [m['content'] for m in assistant_msgs if m['content']]
    if len(assistant_contents) > 10:
        # Check for similar consecutive messages
        repeats = 0
        for i in range(1, len(assistant_contents)):
            a = assistant_contents[i-1][:100]
            b = assistant_contents[i][:100]
            if a and b and a == b:
                repeats += 1
        print(f"    Exact consecutive repeats: {repeats}")
    
    # Check for repeated tool patterns
    tool_seq = [m['tool_name'] for m in messages if m['role'] == 'tool' and m['tool_name']]
    if len(tool_seq) > 20:
        # Find most common 3-tool patterns
        trigrams = Counter()
        for i in range(len(tool_seq)-2):
            key = f"{tool_seq[i]} → {tool_seq[i+1]} → {tool_seq[i+2]}"
            trigrams[key] += 1
        print(f"    Top tool patterns:")
        for pattern, count in trigrams.most_common(5):
            if count > 2:
                print(f"      {pattern} (×{count})")


def analyze_overall(conn, limit=20):
    """全局统计"""
    print(f"\n{'='*60}")
    print(f"  OVERALL SESSION STATISTICS")
    print(f"{'='*60}")
    
    stats = conn.execute("""
        SELECT 
            COUNT(*) as total_sessions,
            SUM(message_count) as total_messages,
            SUM(tool_call_count) as total_tools,
            SUM(input_tokens) as total_input,
            SUM(output_tokens) as total_output,
            AVG(message_count) as avg_messages,
            AVG(tool_call_count) as avg_tools,
            COUNT(DISTINCT model) as models_used
        FROM sessions WHERE message_count > 0
    """).fetchone()
    
    print(f"\n  Total sessions:    {stats['total_sessions']}")
    print(f"  Total messages:    {stats['total_messages']}")
    print(f"  Total tool calls:  {stats['total_tools']}")
    print(f"  Total input:       {stats['total_input']/1e6:.1f}M tokens")
    print(f"  Total output:      {stats['total_output']/1e6:.1f}M tokens")
    print(f"  Avg messages:      {stats['avg_messages']:.0f} per session")
    print(f"  Avg tool calls:    {stats['avg_tools']:.0f} per session")
    
    # Model distribution
    print(f"\n  --- Model Distribution ---")
    models = conn.execute("""
        SELECT model, COUNT(*) as sessions, SUM(message_count) as messages,
               SUM(input_tokens) as input_t, SUM(output_tokens) as output_t
        FROM sessions WHERE message_count > 0 AND model IS NOT NULL
        GROUP BY model ORDER BY sessions DESC
    """).fetchall()
    
    for m in models:
        model = m['model'] or 'unknown'
        print(f"    {model:30s} {m['sessions']:5d} sessions  {m['messages']:7d} msgs  {m['input_t']/1e6:.1f}M in  {m['output_t']/1e6:.1f}M out")
    
    # Source distribution
    print(f"\n  --- Source Distribution ---")
    sources = conn.execute("""
        SELECT source, COUNT(*) as sessions, SUM(message_count) as messages
        FROM sessions WHERE message_count > 0
        GROUP BY source ORDER BY sessions DESC
    """).fetchall()
    for s in sources:
        print(f"    {s['source']:20s} {s['sessions']:5d} sessions  {s['messages']:7d} msgs")
    
    # Most corrected sessions
    print(f"\n  --- Sessions with Most User Corrections ---")
    corrected = conn.execute("""
        SELECT 
            s.id,
            substr(s.title, 1, 40) as title,
            s.message_count as msgs,
            s.model,
            datetime(s.started_at, 'unixepoch', 'localtime') as started,
            SUM(CASE WHEN m.content LIKE '%停%' OR m.content LIKE '%不对%' 
                     OR m.content LIKE '%错了%' OR m.content LIKE '%跑偏%' 
                     OR m.content LIKE '%不要%' OR m.content LIKE '%继续%'
                     OR m.content LIKE '%为什么%' THEN 1 ELSE 0 END) as corrections
        FROM sessions s
        JOIN messages m ON m.session_id = s.id AND m.role = 'user'
        WHERE s.message_count > 50
        GROUP BY s.id
        HAVING corrections > 0
        ORDER BY corrections DESC
        LIMIT ?
    """, (limit,)).fetchall()
    
    for r in corrected:
        title = r['title'] or '(untitled)'
        print(f"    [{r['started'][:10]}] {title:40s} {r['msgs']:5d} msgs  {r['corrections']:3d} corrections  model={r['model']}")
    
    # Empty response rate by model
    print(f"\n  --- Empty Response Rate by Model ---")
    empty_rate = conn.execute("""
        SELECT 
            s.model,
            COUNT(*) as total_assistant,
            SUM(CASE WHEN m.content IS NULL OR m.content = '' THEN 1 ELSE 0 END) as empty_count
        FROM messages m
        JOIN sessions s ON s.id = m.session_id
        WHERE m.role = 'assistant' AND s.message_count > 10
        GROUP BY s.model
        HAVING total_assistant > 100
        ORDER BY CAST(empty_count AS FLOAT) / total_assistant DESC
    """).fetchall()
    
    for r in empty_rate:
        rate = r['empty_count'] / r['total_assistant'] * 100
        print(f"    {r['model']:30s} {r['empty_count']:5d}/{r['total_assistant']:5d} empty ({rate:.1f}%)")


def extract_lessons(conn, session_id):
    """从单个 session 提取经验教训"""
    messages = conn.execute(
        "SELECT * FROM messages WHERE session_id=? ORDER BY timestamp",
        (session_id,)
    ).fetchall()
    
    user_msgs = [(m, m['timestamp']) for m in messages if m['role'] == 'user']
    assistant_msgs = [(m, m['timestamp']) for m in messages if m['role'] == 'assistant']
    
    lessons = {
        'good': [],      # 做得好的
        'bad': [],       # 做得不好的
        'pattern': [],   # 可复用的模式
    }
    
    # Detect: user had to remind agent to continue
    for m, ts in user_msgs:
        content = m['content'] or ''
        if any(kw in content for kw in ['怎么停了', '为什么停了', '怎么不继续']):
            lessons['bad'].append({
                'issue': 'Agent 自行停止，用户不得不再次催促',
                'content': content[:200],
                'fix': '设置 max_turns 更高，或在 system prompt 强调 "不要主动停止"',
            })
    
    # Detect: user had to correct direction
    for m, ts in user_msgs:
        content = m['content'] or ''
        if '跑偏了' in content or '不是这样' in content:
            lessons['bad'].append({
                'issue': 'Agent 偏离用户意图',
                'content': content[:200],
                'fix': '每 5-10 个 turn 做一次意图对齐检查',
            })
    
    # Detect: git push had to be reminded
    for m, ts in user_msgs:
        content = m['content'] or ''
        if 'git push' in content or 'push' in content.lower():
            lessons['bad'].append({
                'issue': 'Agent 忘记主动 git commit/push',
                'content': content[:200],
                'fix': '每完成一个阶段性目标就 commit+push',
            })
    
    # Detect: good patterns (user praised or was satisfied)
    for m, ts in user_msgs:
        content = m['content'] or ''
        if any(kw in content for kw in ['不错', '可以', '挺好', 'nice', 'good']):
            # Find what the assistant did just before
            prev_assistant = [a for a, ats in assistant_msgs if ats < ts]
            if prev_assistant:
                last = prev_assistant[-1]
                lessons['good'].append({
                    'what_worked': (last['content'] or '')[:200],
                    'user_feedback': content[:200],
                })
    
    return lessons


if __name__ == '__main__':
    conn = get_db()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--session':
        sid = sys.argv[2]
        analyze_single_session(conn, sid)
        lessons = extract_lessons(conn, sid)
        print(f"\n  --- Extracted Lessons ---")
        for cat, items in lessons.items():
            if items:
                print(f"\n  [{cat.upper()}]")
                for item in items[:5]:
                    for k, v in item.items():
                        print(f"    {k}: {v}")
                    print()
    elif len(sys.argv) > 1 and sys.argv[1] == '--all':
        analyze_overall(conn, limit=50)
    else:
        analyze_overall(conn, limit=20)
    
    conn.close()
