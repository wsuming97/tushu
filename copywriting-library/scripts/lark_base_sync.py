#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书多维表格同步工具 (Lark Base Sync Tool) v3.0
------------------------------------------------
安全与门禁铁律：
1. 默认仅执行 --dry-run (只读预览)，输出待同步的 Markdown 记录表，不发生任何网络请求；
2. 当前版本尚未实现企业自建应用真实授权与 Base 回包校验，因此：
   - 当用户传入 --apply 时，严格返回 status="not_implemented"；
   - 打印未实现提示，并以非零状态码退出 (sys.exit(1))；
   - 严禁打印“同步成功”或返回 applied_success。
"""

import os
import sys
import json
import argparse
from pathlib import Path

# 确保在 Windows 终端下标准输出编码为 UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def sync_to_lark_base(data: dict, app_id: str = None, app_secret: str = None, base_token: str = None, table_id: str = None, apply: bool = False) -> dict:
    score = data.get("quality_score", 0.0)
    book_title = data.get("book_title", "未命名书籍")
    status = data.get("status", "待核验")

    sync_preview = {
        "book_title": book_title,
        "quality_score": score,
        "review_status": status,
        "title_option_a": data.get("title_option_a", ""),
        "script_summary": data.get("script_summary", "")[:80] + "..." if data.get("script_summary") else "",
        "action_mode": "REAL_WRITE" if apply else "DRY_RUN_PREVIEW"
    }

    print("\n=======================================================")
    print(f"📋 【飞书多维表格看板】 (模式: {'🔴 真实写入 (--apply)' if apply else '🟡 只读预览 (默认 Dry-Run)'})")
    print("=======================================================")
    print(f"· 书籍名称: 《{book_title}》")
    print(f"· 真实评分: {score} 分")
    print(f"· 审核状态: {status}")
    print(f"· 爆款标题: {sync_preview['title_option_a']}")
    print(f"· 脚本摘要: {sync_preview['script_summary']}")
    print("-------------------------------------------------------")

    if not apply:
        print("💡 [只读预览] 当前为默认 Dry-Run 模式，未发起网络请求，未修改任何数据。")
        return {"status": "dry_run_preview", "preview": sync_preview}

    # 门禁拦截：当前尚未对接完整飞书企业自建应用鉴权回包
    print("⛔ [NOT IMPLEMENTED] 飞书多维表格真实写入能力尚未正式对接（缺少企业自建应用鉴权、base_token 与 record_id 校验回包）。")
    print("💡 当前仅支持默认只读预览 (--dry-run)。如需正式写入，请等待后续飞书企业应用对接。")
    sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="飞书多维表格同步工具 v3.0")
    parser.add_argument("--book", type=str, default="被讨厌的勇气", help="书名")
    parser.add_argument("--score", type=float, default=0.0, help="真实质检评分 (0~100)")
    parser.add_argument("--status", type=str, default="待审核", help="状态")
    parser.add_argument("--apply", action="store_true", help="显式授权真实写入 (当前未实现，将非零阻断)")
    args = parser.parse_args()

    sample_data = {
        "book_title": args.book,
        "quality_score": args.score,
        "status": args.status,
        "title_option_a": f"为什么你总在讨好别人？《{args.book}》给你的解药",
        "script_summary": "通过真实困境切入，说明课题分离与自我接纳。"
    }

    sync_to_lark_base(sample_data, apply=args.apply)
