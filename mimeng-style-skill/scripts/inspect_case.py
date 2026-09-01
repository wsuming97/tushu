#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
咪蒙观点文写作机制与案例检索器 (Mimeng Style Case Inspector) v2.0
------------------------------------------------------------------
权威语料基线：挂载 Phase B Full v2 数据库 (phase_b_956_fts.db)
消除旧表污染，基于有效正文进行案例透视。
"""

import sys, os, sqlite3, argparse, json
from pathlib import Path

# 确保在 Windows 终端下标准输出编码为 UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def inspect_case(title_or_id: str, db_path_str: str = None):
    if db_path_str is None:
        db_env = os.getenv("PHASE_B_DB")
        if not db_env:
            print("❌ 错误：未配置权威数据库路径，请通过 --db-path 参数或 PHASE_B_DB 环境变量指定数据库文件。", file=sys.stderr)
            sys.exit(1)
        db_path = Path(db_env)
    else:
        db_path = Path(db_path_str)

    if not db_path.exists():
        print(f"❌ 错误：权威数据库不存在: {db_path}", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    # 支持 doc_id 整数检索或标题模糊检索
    if title_or_id.isdigit():
        cur.execute("""
            SELECT doc_id, category, filename, normalized_title, doc_status,
                   raw_char_count, clean_char_count, quality_flags, clean_text
            FROM documents
            WHERE doc_id = ?
        """, (int(title_or_id),))
    else:
        cur.execute("""
            SELECT doc_id, category, filename, normalized_title, doc_status,
                   raw_char_count, clean_char_count, quality_flags, clean_text
            FROM documents
            WHERE normalized_title LIKE ? OR filename LIKE ?
            ORDER BY doc_id ASC
            LIMIT 1
        """, (f"%{title_or_id}%", f"%{title_or_id}%"))

    row = cur.fetchone()
    conn.close()

    if not row:
        print(f"❌ 未在权威库中找到匹配案例: {title_or_id}")
        return

    doc_id, category, filename, title, doc_status, raw_chars, clean_chars, q_flags, clean_text = row

    # 提取文章开篇前 200 字作为开头机制样本
    clean_lines = [l.strip() for l in clean_text.splitlines() if l.strip()]
    hook_sample = "\n".join(clean_lines[:3]) if clean_lines else "（该文档为占位/下架文档，正文已置空）"

    print("==================================================")
    print(f"【案例卡编号】：mm_case_{doc_id:04d} (Phase B Full v2 权威基线)")
    print(f"【所属分类】：{category}")
    print(f"【正式标题】：{title}")
    print(f"【文档状态】：{'🟢 有效正文' if doc_status == 'available' else '🔴 下架/占位 (不可读)'}")
    print(f"【有效字数】：{clean_chars:,} 字符 (原始: {raw_chars:,} 字符)")
    print(f"【开篇黄金 Hook 样本】：\n{hook_sample}")
    print(f"【物理原文路径】：${{CORPUS_ROOT}}/text-corpus/{category}/{filename}")
    print(f"【物理版式对照】：${{CORPUS_ROOT}}/pdf-corpus/{category}/{title}.pdf")
    print("==================================================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspect single mechanism case from Phase B v2 Authority")
    parser.add_argument("case_id", type=str, help="Case doc_id or title keyword (e.g. 6 or 康熙来了)")
    parser.add_argument("--db-path", type=str, default=None, help="Phase B 数据库路径 (或配置 PHASE_B_DB 环境变量)")
    args = parser.parse_args()
    inspect_case(args.case_id, db_path_str=args.db_path)
