#!/usr/bin/env python3
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  모두의 창업  |  아이디어 카드 크롤러
  URL : https://www.modoo.or.kr/idea/list
  작성 : Claude for KICON
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[사전 준비] 터미널에서 아래 명령어 실행:
  pip install playwright
  python -m playwright install chromium

[실행]
  python crawl_modoo_idea.py
"""

import json
import time
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

ROOT = Path(__file__).resolve().parent
TARGET_URL = "https://www.modoo.or.kr/idea/list"
OUTPUT_JSON = ROOT / "modoo_idea_cards.json"
SCREENSHOT_FILE = ROOT / "modoo_screenshot.png"

# ── 카드 후보 셀렉터 (우선순위 순) ─────────────────────────────
CARD_SELECTORS = [
    "article",
    ".card",
    "[class*='card']",
    "[class*='Card']",
    "[class*='IdeaCard']",
    "[class*='idea-card']",
    "[class*='IdeaItem']",
    "[class*='idea-item']",
    "[class*='ListItem']",
    "[class*='list-item']",
    "ul > li[class]",
    "ol > li[class]",
    ".swiper-slide",
    "[class*='slide']",
    "[class*='item']",
    "section > div > div",
    "main > section > *",
    "main > div > div > div",
]

MIN_CARD_TEXT_LEN = 10
MIN_VALID_COUNT = 3


def print_banner():
    print("=" * 60)
    print("  모두의 창업 | 아이디어 카드 크롤러")
    print(f"  대상: {TARGET_URL}")
    print(f"  시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


def extract_card_data(element) -> dict:
    text = element.inner_text().strip()

    links = []
    try:
        anchors = element.query_selector_all("a[href]")
        for a in anchors:
            href = a.get_attribute("href") or ""
            label = a.inner_text().strip() or a.get_attribute("aria-label") or ""
            if href:
                links.append({"label": label, "href": href})
    except Exception:
        pass

    images = []
    try:
        imgs = element.query_selector_all("img[alt]")
        for img in imgs:
            alt = img.get_attribute("alt") or ""
            src = img.get_attribute("src") or ""
            if alt:
                images.append({"alt": alt, "src": src})
    except Exception:
        pass

    return {"text": text, "links": links, "images": images}


def try_selectors(page) -> tuple[list, str]:
    for sel in CARD_SELECTORS:
        try:
            elements = page.query_selector_all(sel)
            cards = []
            for el in elements:
                data = extract_card_data(el)
                if len(data["text"]) >= MIN_CARD_TEXT_LEN:
                    cards.append(data)
            if len(cards) >= MIN_VALID_COUNT:
                print(f"  [+] 셀렉터 '{sel}' → {len(cards)}개 카드 추출 성공")
                return cards, sel
        except Exception:
            continue
    return [], "미발견"


def fallback_full_text(page) -> list:
    try:
        text = page.inner_text("main") or page.inner_text("body")
        return [{"text": text, "links": [], "images": []}]
    except Exception:
        return []


def save_results(cards: list, selector: str) -> dict:
    result = {
        "crawled_at": datetime.now().isoformat(),
        "url": TARGET_URL,
        "selector_used": selector,
        "total_cards": len(cards),
        "cards": [
            {
                "index": i,
                "content": c["text"],
                "links": c["links"],
                "images": c["images"],
            }
            for i, c in enumerate(cards, 1)
        ],
    }
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"  [+] JSON 저장 완료: {OUTPUT_JSON}")
    return result


def print_cards(result: dict):
    print("\n" + "=" * 60)
    print(f"  총 {result['total_cards']}개 카드 추출 완료")
    print("=" * 60)
    for card in result["cards"]:
        print(f"\n── 카드 {card['index']:02d} ──────────────────────────────────")
        text_preview = card["content"][:500]
        if len(card["content"]) > 500:
            text_preview += "..."
        print(text_preview)
        if card["links"]:
            print("  📎 링크:", ", ".join(
                f"{lk['label']}({lk['href']})" for lk in card["links"][:3]
            ))


def crawl():
    print_banner()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="ko-KR",
            viewport={"width": 1440, "height": 900},
        )

        page = context.new_page()

        print(f"\n[1/4] 페이지 로딩 중... ({TARGET_URL})")
        try:
            page.goto(TARGET_URL, wait_until="networkidle", timeout=30000)
        except PlaywrightTimeout:
            print("  [!] networkidle 타임아웃 → domcontentloaded 모드로 재시도")
            page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=20000)

        print("[2/4] JS 렌더링 대기 (3초)...")
        time.sleep(3)

        print("[3/4] 스크롤로 lazy-load 콘텐츠 로드 중...")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1)

        page.screenshot(path=SCREENSHOT_FILE, full_page=True)
        print(f"  [+] 스크린샷 저장: {SCREENSHOT_FILE}")

        print("\n[4/4] 카드 데이터 추출 중...")
        cards, selector = try_selectors(page)

        if not cards:
            print("  [!] 자동 셀렉터 실패 → 전체 텍스트 모드로 전환")
            cards = fallback_full_text(page)
            selector = "fallback:body"

        browser.close()

    result = save_results(cards, selector)
    print_cards(result)
    print(f"\n[완료] {datetime.now().strftime('%H:%M:%S')} — "
          f"{result['total_cards']}개 카드, 파일: {OUTPUT_JSON}")
    return result


if __name__ == "__main__":
    crawl()
