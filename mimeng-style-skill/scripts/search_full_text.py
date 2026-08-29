import sys, re, json, argparse
from pathlib import Path

INDEX_PATH = Path(r"D:\suming\wiki\playbooks\1012篇爆款文章深度拆解总表.csv")
CORPUS_DIR = Path(r"D:\suming\raw\pdf-corpus")

def search_full_text(query, top_k=5):
    import csv
    if not INDEX_PATH.exists():
        print(f"索引文件不存在: {INDEX_PATH}")
        return []
        
    results = []
    with open(INDEX_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            score = 0
            comb = f"{r['title']} {r['summary']} {r['golden']} {r['theme_thesis']} {r['category']}"
            for w in query.split():
                if w in comb:
                    score += 2
                if w in r["title"]:
                    score += 5
            if score > 0:
                results.append((score, r))
                
    results.sort(key=lambda x: x[0], reverse=True)
    return [r[1] for r in results[:top_k]]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search 1012 corpus full-text records")
    parser.add_argument("query", type=str, help="Search query")
    parser.add_argument("--top_k", type=int, default=5, help="Top K results")
    args = parser.parse_args()
    
    res = search_full_text(args.query, args.top_k)
    print(f"📖 在 1012 篇语料库中检索到 {len(res)} 条相关证据：\n")
    for idx, r in enumerate(res, 1):
        print(f"--- [{idx}] 《{r['title']}》 ({r['category']}) ---")
        print(f"【摘要】：{r['summary']}")
        print(f"【核心金句】：{r['golden']}")
        print(f"【论点与框架】：{r['theme_thesis']} | {r['framework']}")
        print(f"【原文件名】：{r['filename']}\n")
