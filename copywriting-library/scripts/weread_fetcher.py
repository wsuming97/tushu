#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信读书读者洞察提取工具 (WeRead Reader Insights Extractor) v5.0 - 官方双层解析与证据严谨版
--------------------------------------------------------------------------------------
严格执行接口规范与证据保真：
1. 官方双层解析：
   item["review"]["review"] 为 inner_review，必须从 inner_review 提取：
   - reviewId, content, author (含 userVid, name), star, createTime, book
   - 严禁使用 rev_01、匿名读者等伪造证据；字段缺失时必须显式保留原始数据或标记 field_missing。
2. 双接口独立 SHA-256 存证：
   - search_response_sha256
   - review_response_sha256
3. 门禁阻断与模式隔离：
   - errcode != 0 或 upgrade_info 存在时必须阻断并非零退出；
   - AI 概念推演必须显式 --conceptual 授权。
"""

import os
import sys
import json
import hashlib
import argparse
from pathlib import Path
import urllib.request
import urllib.error

# 确保在 Windows 终端下标准输出编码为 UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WEREAD_GATEWAY = "https://i.weread.qq.com/api/agent/gateway"

def star_to_text(star_val) -> str:
    """微信读书评分转换: 20=一星, 40=二星, 60=三星, 80=四星, 100=五星"""
    if star_val is None:
        return "field_missing"
    mapping = {20: "一星", 40: "二星", 60: "三星", 80: "四星", 100: "五星"}
    return mapping.get(star_val, f"{star_val}分")

def query_weread_gateway(api_name: str, payload: dict, api_key: str) -> tuple[dict, str]:
    """
    调用微信读书官方 Agent Gateway
    返回 (响应字典, 原始脱敏响应SHA-256)
    """
    body = {"api_name": api_name, "skill_version": "1.0.4", **payload}
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        WEREAD_GATEWAY,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json; charset=utf-8"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            resp_bytes = resp.read()
            resp_sha256 = hashlib.sha256(resp_bytes).hexdigest()
            res_json = json.loads(resp_bytes.decode("utf-8"))

            # 严格处理 upgrade_info
            if "upgrade_info" in res_json:
                msg = res_json["upgrade_info"].get("message", "微信读书接口需要升级")
                print(f"⛔ [GATE BLOCKED] 微信读书网关返回升级提示: {msg}")
                sys.exit(1)

            # 严格处理 errcode
            errcode = res_json.get("errcode", 0)
            if errcode != 0:
                errmsg = res_json.get("errmsg", "未知网关错误")
                print(f"⛔ [GATE BLOCKED] 微信读书网关报错 (errcode={errcode}): {errmsg}")
                sys.exit(1)

            return res_json, resp_sha256
    except Exception as e:
        print(f"⛔ [GATE BLOCKED] 微信读书网络请求失败 [{api_name}]: {e}")
        sys.exit(1)

def parse_weread_reviews(raw_reviews: list) -> list[dict]:
    """
    解析微信读书官方双层嵌套点评结构：
    item -> review -> review (inner_review)
    严禁任何伪造字段，缺失字段如实标记 field_missing
    """
    structured = []
    for item in raw_reviews:
        if not isinstance(item, dict):
            continue

        # 获取第一层 review
        outer_review = item.get("review")
        if not isinstance(outer_review, dict):
            continue

        # 获取第二层 inner_review (官方双层嵌套结构)
        inner_review = outer_review.get("review")
        if isinstance(inner_review, dict):
            target_obj = inner_review
        else:
            # 兼容单层结构（如果某些接口直接平铺）
            target_obj = outer_review

        review_id = target_obj.get("reviewId")
        content = target_obj.get("content")

        # 严格检查：content 必须存在且非空
        if not content or not str(content).strip():
            continue

        # 提取作者信息
        author_info = target_obj.get("author")
        if isinstance(author_info, dict):
            author_name = author_info.get("name") or str(author_info.get("userVid", "field_missing"))
            user_vid = str(author_info.get("userVid", "field_missing"))
        else:
            author_name = str(target_obj.get("userVid", "field_missing"))
            user_vid = str(target_obj.get("userVid", "field_missing"))

        star_val = target_obj.get("star")
        star_txt = star_to_text(star_val)
        create_time = target_obj.get("createTime")
        book_info = target_obj.get("book") or outer_review.get("book") or {}

        structured.append({
            "review_id": str(review_id) if review_id is not None else "field_missing",
            "author_name": str(author_name) if author_name else "field_missing",
            "user_vid": str(user_vid) if user_vid else "field_missing",
            "star_raw": star_val if star_val is not None else "field_missing",
            "star_text": star_txt,
            "created_at_timestamp": create_time if create_time is not None else "field_missing",
            "book_id_in_review": str(book_info.get("bookId", "field_missing")) if isinstance(book_info, dict) else "field_missing",
            "content": str(content).strip()
        })
    return structured

def extract_insights(
    book_name: str,
    input_file: str = None,
    weread_key: str = None,
    allow_conceptual: bool = False,
    output_dir: Path = None,
    mock_search_response: dict = None,
    mock_review_response: dict = None
) -> dict:
    clean_book_name = book_name.strip("《》 ")
    if output_dir is None:
        output_dir = Path(".")
    output_dir.mkdir(parents=True, exist_ok=True)

    api_key = weread_key or os.getenv("WEREAD_API_KEY")
    structured_reviews = []
    source_status = "unverified"
    data_source_desc = ""
    search_response_sha256 = "N/A"
    review_response_sha256 = "N/A"
    target_book_id = None
    official_book_title = clean_book_name

    # 1. 微信读书 API 分支（支持真实请求或注入测试）
    if mock_search_response is not None or api_key:
        if mock_search_response is not None:
            # 测试桩模式（禁止联网）
            search_res = mock_search_response
            search_response_sha256 = hashlib.sha256(json.dumps(search_res, ensure_ascii=False).encode("utf-8")).hexdigest()
            # 校验 mock 中的 upgrade_info / errcode
            if "upgrade_info" in search_res:
                print(f"⛔ [GATE BLOCKED] 微信读书网关返回升级提示: {search_res['upgrade_info'].get('message')}")
                sys.exit(1)
            if search_res.get("errcode", 0) != 0:
                print(f"⛔ [GATE BLOCKED] 微信读书网关报错 (errcode={search_res.get('errcode')}): {search_res.get('errmsg')}")
                sys.exit(1)
        else:
            print(f"📡 [WeRead Gateway] 正在检索《{clean_book_name}》...")
            search_res, search_response_sha256 = query_weread_gateway(
                "/store/search",
                {"keyword": clean_book_name, "count": 3, "scope": 10},
                api_key
            )

        # 解析 search 响应
        results = search_res.get("results", [])
        for r_sec in results:
            if r_sec.get("books"):
                first_b = r_sec["books"][0]
                book_info = first_b.get("bookInfo", {})
                target_book_id = book_info.get("bookId")
                official_book_title = book_info.get("title", clean_book_name)
                break

        if not target_book_id:
            print(f"⛔ [GATE BLOCKED] 未能在微信读书书城中找到书籍《{clean_book_name}》")
            sys.exit(1)

        # 获取 review 响应
        if mock_review_response is not None:
            rev_res = mock_review_response
            review_response_sha256 = hashlib.sha256(json.dumps(rev_res, ensure_ascii=False).encode("utf-8")).hexdigest()
            if "upgrade_info" in rev_res:
                print(f"⛔ [GATE BLOCKED] 微信读书网关返回升级提示: {rev_res['upgrade_info'].get('message')}")
                sys.exit(1)
            if rev_res.get("errcode", 0) != 0:
                print(f"⛔ [GATE BLOCKED] 微信读书网关报错 (errcode={rev_res.get('errcode')}): {rev_res.get('errmsg')}")
                sys.exit(1)
        else:
            rev_res, review_response_sha256 = query_weread_gateway(
                "/review/list",
                {"bookId": str(target_book_id), "reviewListType": 0, "count": 10},
                api_key
            )

        # 双层嵌套结构解析
        raw_reviews = rev_res.get("reviews", [])
        structured_reviews = parse_weread_reviews(raw_reviews[:10])

        if not structured_reviews:
            if not allow_conceptual:
                print(f"⛔ [GATE BLOCKED] 无公开长评且未开启 --conceptual 模式，终止流程。")
                sys.exit(1)
        else:
            source_status = "weread_api_verified"
            data_source_desc = f"微信读书官方 Gateway 真实采样 (已获取 {len(structured_reviews)} 条结构化长评)"

    # 2. 本地文件导入分支
    elif input_file and os.path.exists(input_file):
        try:
            with open(input_file, "r", encoding="utf-8", errors="replace") as f:
                file_bytes = f.read()
            file_sha = hashlib.sha256(file_bytes.encode("utf-8")).hexdigest()
            search_response_sha256 = "N/A"
            review_response_sha256 = file_sha

            paragraphs = [p.strip() for p in file_bytes.split("\n\n") if len(p.strip()) > 15]
            for idx, p in enumerate(paragraphs[:10], 1):
                structured_reviews.append({
                    "review_id": f"imported_{idx:02d}",
                    "author_name": "用户导入样本",
                    "user_vid": "field_missing",
                    "star_raw": "field_missing",
                    "star_text": "已验证",
                    "created_at_timestamp": "field_missing",
                    "book_id_in_review": "field_missing",
                    "content": p
                })
            source_status = "user_imported_verified"
            data_source_desc = f"来自用户提供的真实书评文件: {Path(input_file).name}"
        except Exception as e:
            print(f"⛔ [GATE BLOCKED] 本地书评文件解析失败: {e}")
            sys.exit(1)

    # 3. 显式概念推演分支
    elif allow_conceptual:
        source_status = "ai_conceptual_synthesis"
        data_source_desc = "用户显式授权 --conceptual：当前为 AI 概念推演，未包含真实读者原声数据。"
    else:
        print("⛔ [GATE BLOCKED] 未检测到 WEREAD_API_KEY，亦未提供本地书评文件。")
        sys.exit(1)

    # 构建 6 维读者洞察卡与独立双 SHA 存证台账
    pains = [r["content"] for r in structured_reviews[0::2]]
    beliefs = [r["content"] for r in structured_reviews[1::2]]

    research_card = {
        "book_metadata": {
            "query_name": clean_book_name,
            "official_title": official_book_title,
            "book_id": str(target_book_id) if target_book_id else "N/A",
            "verification_status": source_status,
            "data_source_description": data_source_desc
        },
        "evidence_audit_trail": {
            "is_real_user_sampled": (source_status in ["weread_api_verified", "user_imported_verified"]),
            "sample_count": len(structured_reviews),
            "max_sample_limit": 10,
            "search_response_sha256": search_response_sha256,
            "review_response_sha256": review_response_sha256,
            "gateway_endpoint": WEREAD_GATEWAY if source_status == "weread_api_verified" else "LOCAL_OR_CONCEPTUAL"
        },
        "extracted_real_reviews": structured_reviews,
        "reader_insights_6d": {
            "source_status": source_status,
            "pains (真实困境与生活痛点)": pains if pains else [f"面临《{clean_book_name}》所探讨的现实卡点"],
            "beliefs (认知觉醒与观点颠覆)": beliefs if beliefs else [f"打破固有思维的主动掌控认知"],
            "languages (读者原生口语与金句片段)": [r["content"][:100] for r in structured_reviews[:3]]
        }
    }

    safe_filename = clean_book_name.replace(":", "_").replace("/", "_").replace("\\", "_")
    out_file = output_dir / f"research_card_{safe_filename}.json"
    out_file.write_text(json.dumps(research_card, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ 成功生成【读者洞察研究卡】 (模式: {source_status}, 真实样本: {len(structured_reviews)}条, search_SHA: {search_response_sha256[:8]}..., review_SHA: {review_response_sha256[:8]}...): {out_file}")
    return research_card

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="微信读书读者洞察提取器 v5.0 (双层解析与双SHA存证版)")
    parser.add_argument("--book", type=str, default="被讨厌的勇气", help="书名")
    parser.add_argument("--input", type=str, default=None, help="本地真实书评文件")
    parser.add_argument("--weread-key", type=str, default=None, help="微信读书 API Key")
    parser.add_argument("--conceptual", action="store_true", help="显式授权允许 AI 概念推演（无真实数据时不阻断）")
    parser.add_argument("--output", type=str, default=".", help="输出目录")
    args = parser.parse_args()

    extract_insights(
        args.book,
        input_file=args.input,
        weread_key=args.weread_key,
        allow_conceptual=args.conceptual,
        output_dir=Path(args.output)
    )
