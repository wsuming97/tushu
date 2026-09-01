import sys, os, re, sqlite3, argparse, time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SKILL_DIR = Path(__file__).resolve().parent.parent

def tokenize_query_phrase(query):
    tokens = []
    for token in re.findall(r"[\u4e00-\u9fa5]|[a-zA-Z0-9_]+", query):
        tokens.append(f'"{token}"')
    return " ".join(tokens)

def search_full_text(query, top_k=5, db_path=None):
    if db_path is None:
        db_env = os.getenv("PHASE_A_DB")
        if not db_env:
            print("❌ 错误：未配置数据库路径，请通过 --db-path 参数或 PHASE_A_DB 环境变量指定数据库文件。", file=sys.stderr)
            sys.exit(1)
        db_path = Path(db_env)
    else:
        db_path = Path(db_path)

    if not db_path.exists():
        print(f"❌ 错误：数据库文件不存在: {db_path}", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    tok_q = tokenize_query_phrase(query)
    start_t = time.time()

    cur.execute("""
    SELECT p.doc_id, p.category, p.title, p.page_num, p.clean_text, p.filename, p.page_type
    FROM fts_pages f
    JOIN pages p ON f.rowid = p.id
    WHERE fts_pages MATCH ? AND instr(p.clean_text, ?) > 0
    LIMIT ?;
    """, (tok_q, query, top_k))
    rows = cur.fetchall()
    q_time = round((time.time() - start_t) * 1000, 2)

    results = []
    for r in rows:
        c_text = r[4]
        pos = c_text.find(query)
        start_p = max(0, pos - 45)
        end_p = min(len(c_text), pos + len(query) + 45)
        snip = "..." + c_text[start_p:pos] + f"【{query}】" + c_text[pos+len(query):end_p] + "..."
        results.append({
            "doc_id": r[0],
            "category": r[1],
            "title": r[2],
            "page_num": r[3],
            "page_type": r[6],
            "snippet": snip.replace("\n", " "),
            "filename": r[5],
            "time_ms": q_time
        })

    conn.close()
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="全文精确检索语料库 (基于 FTS5 索引)")
    parser.add_argument("query", help="要检索的关键词或短语")
    parser.add_argument("--top", type=int, default=5, help="返回前 N 条结果 (默认 5)")
    parser.add_argument("--db-path", type=str, default=None, help="Phase A 数据库路径 (或配置 PHASE_A_DB 环境变量)")
    args = parser.parse_args()

    res = search_full_text(args.query, top_k=args.top, db_path=args.db_path)
    print(f"\n🔍 检索词: 【{args.query}】 | 命中: {len(res)} 条")
    print("=" * 60)
    for i, item in enumerate(res, 1):
        print(f"[{i}] 《{item['title']}》 (分类: {item['category']} | 第 {item['page_num']} 页 | {item['page_type']})")
        print(f"    文摘: {item['snippet']}")
        print(f"    来源: {item['filename']}")
        print("-" * 60)
