import sys, csv, argparse
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

INDEX_PATH = Path(r"D:\suming\wiki\playbooks\1012篇爆款文章深度拆解总表.csv")

def inspect_case(title_or_id):
    if not INDEX_PATH.exists():
        print(f"索引文件不存在: {INDEX_PATH}")
        return
        
    with open(INDEX_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for idx, r in enumerate(reader, 1):
            if str(idx) == title_or_id or title_or_id in r["title"] or title_or_id in r["filename"]:
                print(f"==================================================")
                print(f"【案例卡编号】：mm_case_{idx:04d}")
                print(f"【所属分类】：{r['category']}")
                print(f"【正式标题】：{r['title']}")
                print(f"【核心摘要】：{r['summary']}")
                print(f"【传播金句】：{r['golden']}")
                print(f"【核心论点】：{r['theme_thesis']}")
                print(f"【写作骨架】：{r['framework']}")
                print(f"【物理文件】：D:\\suming\\raw\\pdf-corpus\\{r['category']}\\{r['filename']}")
                print(f"==================================================\n")
                return
    print(f"未找到匹配案例: {title_or_id}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspect single mechanism case")
    parser.add_argument("case_id", type=str, help="Case index or title keyword")
    args = parser.parse_args()
    inspect_case(args.case_id)
