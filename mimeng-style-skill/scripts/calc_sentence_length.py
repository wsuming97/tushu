# -*- coding: utf-8 -*-
"""
Phase B Full v2 语料真实句长与节奏分布科学统计脚本 (Sentence Length Calculator) v2.0
--------------------------------------------------------------------------------
科学计算与逐篇审计规范：
1. 数据源：Phase B Full v2 (phase_b_956_fts.db) 中 doc_status='available' 的 943 篇纯净文档；
2. 标题剥离纪律（严禁无条件 lines[1:]）：
   - 模式 1 (date_header_split): 匹配 YYYY-MM-DD 或 短日期(X月X日/X周前)，精准剥离标题元数据前缀，保留紧随其后的正文；
   - 模式 2 (title_prefix_split): 匹配 normalized_title 纯标题及作者后缀，剥离元数据前缀，保留后续正文；
   - 模式 3 (no_title_keep_all): 第一行即为正文（无标题元数据），100% 完整保留第一行；
   - 模式 4 (standalone_title_line): 第一行为独立标题行，剥离整行。
3. 输出审计字段：title_removal_mode, removed_title_text, retained_first_line_body；
4. 真实分句口径：以 [。！？!?\n]+ 为边界，过滤纯空白与长度 < 2 的符号噪声；
5. 输出物：sentence_length_per_doc.csv (含逐篇审计字段，UTF-8 无 BOM) 与 sentence_length_stats.json。
"""

import sys, os, sqlite3, json, re, csv, argparse
from pathlib import Path
import numpy as np

# Force UTF-8 stdout
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 严谨的日期元数据识别正则
DATE_HEADER_PATTERN = re.compile(
    r"^(.*?(?:\d{4}[-_/]\d{2}[-_/]\d{2}|\d{1,2}月\d{1,2}日|\d+周前|\d+天前|\d+小时前))(.*)$",
    re.DOTALL
)

def strip_title_metadata(first_line: str, normalized_title: str) -> tuple[str, str, str]:
    """
    智能剥离第一行中的标题/作者/日期元数据，绝不误删粘连正文
    返回: (title_removal_mode, removed_title_text, retained_first_line_body)
    """
    first_line_clean = first_line.strip()

    # 1. 尝试日期结尾元数据匹配
    m_date = DATE_HEADER_PATTERN.match(first_line_clean)
    if m_date:
        meta_text = m_date.group(1).strip()
        body_text = m_date.group(2).strip()
        if body_text:
            return "date_header_with_inline_body", meta_text, body_text
        else:
            return "date_header_standalone_line", meta_text, ""

    # 2. 尝试基于 normalized_title 的纯标题前缀匹配
    clean_title = re.sub(r"^\d{4}_\d{2}_\d{2}\s*", "", normalized_title).strip("_ ")
    if clean_title and clean_title in first_line_clean:
        idx = first_line_clean.find(clean_title) + len(clean_title)
        meta_prefix = first_line_clean[:idx]
        rest = first_line_clean[idx:].strip()
        # 尝试剥离紧随标题后的作者署名（例如 原创：xxx 咪蒙）
        author_m = re.match(r"^(原创[：:][^\s]+\s*)?(咪蒙\s*)?(.*)$", rest, re.DOTALL)
        if author_m:
            meta_author = (author_m.group(1) or "") + (author_m.group(2) or "")
            meta_text = (meta_prefix + " " + meta_author).strip()
            body_text = (author_m.group(3) or "").strip()
        else:
            meta_text = meta_prefix
            body_text = rest

        if body_text:
            return "title_prefix_with_inline_body", meta_text, body_text
        else:
            return "title_standalone_line", meta_text, ""

    # 3. 第一行未检测到标题元数据，完整保留作为正文
    return "no_title_detected_keep_all", "", first_line_clean

def calculate_sentence_stats(db_path: Path = None, out_dir: Path = None) -> tuple[dict, list]:
    if db_path is None:
        db_env = os.getenv("PHASE_B_DB")
        if not db_env:
            raise FileNotFoundError("未指定数据库路径，请通过 --db-path 参数或 PHASE_B_DB 环境变量配置。")
        db_path = Path(db_env)
    else:
        db_path = Path(db_path)

    if out_dir is None:
        out_dir = Path(__file__).resolve().parent.parent / "references"
    else:
        out_dir = Path(out_dir)

    out_dir.mkdir(parents=True, exist_ok=True)

    if not db_path.exists():
        print(f"❌ 数据库不存在: {db_path}", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("""
        SELECT doc_id, category, filename, normalized_title, clean_text
        FROM documents
        WHERE doc_status = 'available'
        ORDER BY doc_id ASC
    """)
    rows = cur.fetchall()
    conn.close()

    all_sentence_lengths = []
    per_doc_stats = []
    split_pattern = re.compile(r"[。！？!?\n]+")

    for doc_id, category, filename, title, text in rows:
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if not lines:
            continue

        first_line = lines[0]
        mode, removed_meta, retained_body = strip_title_metadata(first_line, title)

        # 组装纯净正文（第一行保留部分 + 后续各行）
        body_segments = []
        if retained_body:
            body_segments.append(retained_body)
        if len(lines) > 1:
            body_segments.extend(lines[1:])

        full_body_text = "\n".join(body_segments)
        raw_sentences = split_pattern.split(full_body_text)
        valid_sentences = [s.strip() for s in raw_sentences if len(s.strip()) >= 2]

        doc_lengths = [len(s) for s in valid_sentences]
        if doc_lengths:
            all_sentence_lengths.extend(doc_lengths)
            avg_len = round(float(np.mean(doc_lengths)), 2)
            med_len = round(float(np.median(doc_lengths)), 2)
        else:
            avg_len = 0.0
            med_len = 0.0

        per_doc_stats.append({
            "doc_id": doc_id,
            "category": category,
            "filename": filename,
            "title": title,
            "title_removal_mode": mode,
            "removed_title_text": removed_meta,
            "retained_first_line_body": retained_body,
            "sentence_count": len(doc_lengths),
            "avg_sentence_len": avg_len,
            "median_sentence_len": med_len
        })

    all_arr = np.array(all_sentence_lengths)

    summary = {
        "dataset": "Phase B Full v2 (phase_b_956_fts.db)",
        "doc_filter": "doc_status == 'available'",
        "doc_count": len(rows),
        "total_valid_sentences": int(len(all_arr)),
        "mean_sentence_length": round(float(np.mean(all_arr)), 2),
        "median_sentence_length": round(float(np.median(all_arr)), 2),
        "p25_length": round(float(np.percentile(all_arr, 25)), 2),
        "p75_length": round(float(np.percentile(all_arr, 75)), 2),
        "p90_length": round(float(np.percentile(all_arr, 90)), 2),
        "min_length": int(np.min(all_arr)),
        "max_length": int(np.max(all_arr)),
        "split_rules": "以 [。！？!?\\n]+ 作为断句边界，智能剥离标题元数据前缀，严格保留首行正文"
    }

    # 保存汇总 JSON
    json_path = out_dir / "sentence_length_stats.json"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # 保存逐篇 CSV (UTF-8 无 BOM)
    csv_path = out_dir / "sentence_length_per_doc.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "doc_id", "category", "filename", "title",
            "title_removal_mode", "removed_title_text", "retained_first_line_body",
            "sentence_count", "avg_sentence_len", "median_sentence_len"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(per_doc_stats)

    print("\n=======================================================")
    print("📈 【Phase B Full v2 语料句长科学实测新结果 (无损正文版)】")
    print("=======================================================")
    print(f"· 分析文档总数: {summary['doc_count']} 篇")
    print(f"· 有效分析句子: {summary['total_valid_sentences']:,} 句")
    print(f"· 单句平均字数 (Mean): {summary['mean_sentence_length']} 字")
    print(f"· 单句中位字数 (Median): {summary['median_sentence_length']} 字")
    print(f"· P75 长度 (75%的句子短于): {summary['p75_length']} 字")
    print(f"· P90 长度 (90%的句子短于): {summary['p90_length']} 字")
    print(f"· 逐篇审计 CSV 保存至: {csv_path}")
    print(f"· 汇总审计 JSON 保存至: {json_path}")
    print("=======================================================\n")
    return summary, per_doc_stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate sentence length distribution for Phase B corpus")
    parser.add_argument("--db-path", type=str, default=None, help="Phase B 数据库路径 (或配置 PHASE_B_DB 环境变量)")
    parser.add_argument("--out-dir", type=str, default=None, help="输出目录 (默认 mimeng-style-skill/references)")
    args = parser.parse_args()
    calculate_sentence_stats(db_path=args.db_path, out_dir=args.out_dir)
