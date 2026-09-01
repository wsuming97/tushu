import sys, re, json, argparse
from pathlib import Path

# 确保 Windows 控制台 UTF-8 输出
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SKILL_DIR = Path(__file__).resolve().parent.parent
REF_DIR = SKILL_DIR / "references"

def search_library(query, category=None, top_k=5):
    query = query.lower()
    results = []

    files = list(REF_DIR.glob("*.md"))
    if category:
        files = [f for f in files if category.lower() in f.stem.lower()]

    for f in files:
        text = f.read_text(encoding="utf-8")
        sections = re.split(r"\n##\s+", text)
        for s in sections:
            if not s.strip():
                continue
            title_line = s.split("\n")[0].strip()
            match_score = sum(1 for w in query.split() if w in s.lower())
            if match_score > 0 or not query:
                snippet = "\n".join(s.strip().split("\n")[:12])
                results.append({
                    "file": f.name,
                    "section": title_line,
                    "score": match_score,
                    "content": snippet
                })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search mechanism cards in references")
    parser.add_argument("query", type=str, nargs="?", default="", help="Search query")
    parser.add_argument("--category", type=str, default=None, help="Filter category (topic, title, etc)")
    parser.add_argument("--top_k", type=int, default=5, help="Top K results")
    args = parser.parse_args()

    res = search_library(args.query, args.category, args.top_k)
    print(f"🔍 找到 {len(res)} 条机制卡片匹配：\n")
    for idx, r in enumerate(res, 1):
        print(f"--- [{idx}] 来自 {r['file']} ➔ ## {r['section']} (匹配分: {r['score']}) ---")
        print(r["content"])
        print()
