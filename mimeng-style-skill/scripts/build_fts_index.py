import os, sys, re, json, csv, sqlite3, time
from pathlib import Path
import pypdf

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ==============================================================================
# 水印与广告全面清洗正则库
# ==============================================================================
AD_PATTERNS = [
    # WCplus 免责声明
    r"数据来自微信公众号平台\s*,\s*WCplus仅作转化工具.*?WCplus对此不[^\n]*",
    r"版权或使用问题请联系原公众号[^\n]*",
    r"请勿将数据用于任何商业用途[^\n]*",
    # 阿呆和新媒体朋友广告
    r"阿呆和他的新媒体朋友\s*:\s*技术支撑传播武器库.*?加入\s*WC\s*社群获得工具更新[^\n]*",
    r"数据打造理性运营手\s*WCplus[^\n]*",
    r"作者阿呆\s*微信\s*：\s*wonderfulcorporation[^\n]*",
    r"公众号\s*\(\s*点击打开二维码\s*\)\s*:\s*数据部落[^\n]*",
    r"网站\s*:\s*askingfordata\.com[^\n]*",
    # 公众号常规模板与导流
    r"点击上方\s*[“\"].*?[”\"]\s*，\s*选择\s*[“\"].*?[”\"]\s*[^\n]*",
    r"置顶公众号|设为星标[^\n]*",
    r"关注.*?每天.*?推送[^\n]*",
    r"商务合作.*?[0-9a-zA-Z_]+[^\n]*",
    r"文\s*/\s*咪蒙[^\n]*",
    r"编辑\s*/\s*[^\n]+",
    r"排版\s*/\s*[^\n]+",
    r"插图\s*/\s*[^\n]+",
    r"来源\s*:\s*[^\n]+"
]

def clean_watermark(text):
    clean = text
    matches = []
    for pat in AD_PATTERNS:
        found = re.findall(pat, clean, flags=re.DOTALL)
        if found:
            matches.extend(found)
        clean = re.sub(pat, "", clean, flags=re.DOTALL)
    clean = re.sub(r"\n{3,}", "\n\n", clean).strip()
    return clean, matches

def tokenize_for_fts(text):
    # 将中文每个字符独立切开，英文单词保持完整，空格分隔
    # 这样在 FTS5 中使用 '"柴" "米" "油" "盐"' 即可 100% 精确匹配中文连续多字短语
    tokens = []
    for token in re.findall(r"[\u4e00-\u9fa5]|[a-zA-Z0-9_]+", text):
        tokens.append(token)
    return " ".join(tokens)

def parse_pdf_file(pdf_path, doc_id, category):
    fname = pdf_path.name
    title_clean = re.sub(r"^\d{4}[-_]\d{2}[-_]\d{2}\s*", "", pdf_path.stem).strip()
    if not title_clean:
        title_clean = pdf_path.stem

    reader = pypdf.PdfReader(str(pdf_path))
    num_pages = len(reader.pages)

    pages_data = []
    total_raw_text = ""
    total_clean_text = ""
    all_watermarks = []

    for p_no, page in enumerate(reader.pages, 1):
        p_raw = page.extract_text() or ""
        p_clean, wm = clean_watermark(p_raw)
        if wm:
            all_watermarks.extend(wm)

        p_is_scanned = len(p_clean.strip()) < 15
        p_tok = tokenize_for_fts(p_clean)

        total_raw_text += f"\n--- Page {p_no} ---\n" + p_raw
        total_clean_text += f"\n--- Page {p_no} ---\n" + p_clean

        pages_data.append({
            "doc_id": doc_id,
            "category": category,
            "filename": fname,
            "title": title_clean,
            "page_num": p_no,
            "raw_text": p_raw,
            "clean_text": p_clean,
            "tokenized_text": p_tok,
            "is_scanned": p_is_scanned
        })

    is_doc_scanned = len(total_clean_text.replace(f"--- Page", "").strip()) < 50

    # 提取真实摘要与金句
    if is_doc_scanned:
        clean_summary = "【纯图片素材/扫描件】该文档无有效正文文本层，建议走 OCR 流程。"
        golden_quote = "无（纯图片）"
        golden_page = 0
        theme_thesis = "【纯图片素材】活动海报或图片记录"
        framework = "【纯图片展示】"
    else:
        # 正文摘要（取前几个有效段落）
        clean_stripped = re.sub(r"--- Page \d+ ---", "", total_clean_text).strip()
        paragraphs = [p.strip() for p in clean_stripped.split("\n") if len(p.strip()) > 15]
        if paragraphs:
            summary_raw = " ".join(paragraphs[:3])
            clean_summary = summary_raw[:140] + "..." if len(summary_raw) > 140 else summary_raw
        else:
            clean_summary = clean_stripped[:140]

        # 提炼金句与精确页码（必须严格验证 quote in page_clean）
        golden_quote = ""
        golden_page = 1
        for p in pages_data:
            sentences = [s.strip() for s in re.split(r"[。！？\n]", p["clean_text"]) if len(s.strip()) > 10]
            for s in sentences:
                if any(w in s for w in ["不是", "而是", "所谓的", "所谓", "真正", "越是", "最可怕", "连", "人这辈子", "唯独", "不要"]):
                    if 12 <= len(s) <= 35 and s in p["clean_text"]:
                        golden_quote = s
                        golden_page = p["page_num"]
                        break
            if golden_quote:
                break
        if not golden_quote:
            golden_quote = title_clean
            golden_page = 1

        theme_thesis = f"探讨【{category[3:]}】痛点，核心主张：{golden_quote}"
        if "？" in title_clean or "?" in title_clean:
            framework = "【反问挑衅切入】揭示大众盲区 ➔ 【多层冲突事实】归纳因果 ➔ 【清醒金句收网】"
        elif any(w in clean_stripped[:150] for w in ["昨天", "朋友", "前几天", "上周"]):
            framework = "【真实生活故事入场】戏剧冲突 ➔ 【痛点深度剖析】提炼共性 ➔ 【行动出口与温情赋能】"
        elif "！" in title_clean or "!" in title_clean:
            framework = "【极致情绪断言】替读者宣泄 ➔ 【痛打伪善教条】撕碎吸血逻辑 ➔ 【痛快宣泄收尾】"
        else:
            framework = "【生活常识引入】打破固有误区 ➔ 【逻辑推导与正反案例】 ➔ 【核心金句升华】"

    doc_info = {
        "id": doc_id,
        "category": category,
        "filename": fname,
        "title": title_clean,
        "pages": num_pages,
        "raw_len": len(total_raw_text),
        "clean_len": len(total_clean_text),
        "watermark_count": len(all_watermarks),
        "summary": clean_summary,
        "golden_quote": golden_quote,
        "golden_page": golden_page,
        "theme_thesis": theme_thesis,
        "framework": framework,
        "is_scanned": is_doc_scanned,
        "raw_snippet": total_raw_text[:140].replace("\n", " "),
        "clean_snippet": total_clean_text[:140].replace("\n", " "),
        "watermarks": all_watermarks[:2]
    }

    return doc_info, pages_data

def build_database(db_path, docs, pages):
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    # 1. 结构化页面表
    cur.execute("""
    CREATE TABLE pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doc_id INTEGER,
        category TEXT,
        filename TEXT,
        title TEXT,
        page_num INTEGER,
        clean_text TEXT,
        is_scanned INTEGER
    );
    """)

    # 2. FTS5 虚拟全文检索表（支持跨标题与正文检索）
    cur.execute("""
    CREATE VIRTUAL TABLE fts_pages USING fts5(
        title,
        tokenized_text,
        content='pages',
        content_rowid='id'
    );
    """)

    for p in pages:
        cur.execute("""
        INSERT INTO pages (doc_id, category, filename, title, page_num, clean_text, is_scanned)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (p["doc_id"], p["category"], p["filename"], p["title"], p["page_num"], p["clean_text"], 1 if p["is_scanned"] else 0))
        row_id = cur.lastrowid

        tok_title = tokenize_for_fts(p["title"])
        cur.execute("""
        INSERT INTO fts_pages (rowid, title, tokenized_text)
        VALUES (?, ?, ?)
        """, (row_id, tok_title, p["tokenized_text"]))

    conn.commit()
    conn.close()
    print(f"✅ SQLite FTS5 数据库已成功构建: {db_path}")

if __name__ == "__main__":
    print("mimeng-style-skill build engine loaded.")
