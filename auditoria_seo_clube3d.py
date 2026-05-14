"""
Auditoria SEO deterministica para Clube 3D Brasil.

Inspirado nos checks publicos do projeto codex-seo, mas adaptado para este
repositorio WordPress sem depender de APIs pagas.

Uso:
  python auditoria_seo_clube3d.py
  python auditoria_seo_clube3d.py https://clube3dbrasil.com --limit 40
  python auditoria_seo_clube3d.py --baseline
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8")

DEFAULT_SITE = "https://clube3dbrasil.com"
DEFAULT_LIMIT = 30
REPORT_ROOT = Path("reports") / "seo-audits"
BASELINE_PATH = REPORT_ROOT / "baseline.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; Clube3DSEOAudit/1.0; "
        "+https://clube3dbrasil.com)"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}

SECURITY_HEADERS = [
    "content-security-policy",
    "strict-transport-security",
    "x-frame-options",
    "x-content-type-options",
    "referrer-policy",
]

DEPRECATED_SCHEMA_TYPES = {
    "HowTo",
    "SpecialAnnouncement",
    "CourseInfo",
    "EstimatedSalary",
    "LearningVideo",
    "ClaimReview",
    "VehicleListing",
    "PracticeProblem",
    "Dataset",
}


@dataclass
class PageAudit:
    url: str
    status: int | None
    title: str
    title_len: int
    meta_description: str
    meta_len: int
    h1_count: int
    h1: list[str]
    h2_count: int
    canonical: str
    canonical_ok: bool
    word_count: int
    internal_links: int
    external_links: int
    images_total: int
    images_missing_alt: int
    images_missing_dimensions: int
    schema_types: list[str]
    has_article_schema: bool
    has_faq_schema: bool
    ai_readiness_score: int
    score: int
    issues: list[str]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_site(url: str) -> str:
    parsed = urlparse(url if "://" in url else f"https://{url}")
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"URL invalida: {url}")
    return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(HEADERS)
    return session


def fetch_text(session: requests.Session, url: str, timeout: int = 20) -> tuple[int | None, str, dict[str, str]]:
    try:
        response = session.get(url, timeout=timeout, allow_redirects=True)
        return response.status_code, response.text, dict(response.headers)
    except requests.RequestException:
        return None, "", {}


def parse_sitemap_urls(xml_text: str) -> list[str]:
    urls: list[str] = []
    try:
        root = ET.fromstring(xml_text.encode("utf-8"))
    except ET.ParseError:
        return urls

    ns = ""
    if root.tag.startswith("{"):
        ns = root.tag.split("}", 1)[0] + "}"

    if root.tag.endswith("sitemapindex"):
        for loc in root.findall(f".//{ns}loc"):
            if loc.text:
                urls.append(loc.text.strip())
    else:
        for loc in root.findall(f".//{ns}url/{ns}loc"):
            if loc.text:
                urls.append(loc.text.strip())
    return urls


def discover_urls(session: requests.Session, site: str, limit: int) -> tuple[list[str], dict[str, Any]]:
    robots_url = f"{site}/robots.txt"
    sitemap_candidates = [f"{site}/sitemap_index.xml", f"{site}/sitemap.xml"]
    robots_status, robots_text, _ = fetch_text(session, robots_url)
    for match in re.findall(r"(?im)^sitemap:\s*(\S+)", robots_text):
        sitemap_candidates.insert(0, match.strip())

    sitemap_urls: list[str] = []
    sitemap_statuses: dict[str, int | None] = {}
    page_urls: list[str] = []

    for sitemap_url in list(dict.fromkeys(sitemap_candidates)):
        status, text, _ = fetch_text(session, sitemap_url)
        sitemap_statuses[sitemap_url] = status
        if status != 200 or not text:
            continue
        discovered = parse_sitemap_urls(text)
        if not discovered:
            continue
        sitemap_urls.append(sitemap_url)
        if discovered and discovered[0].endswith(".xml"):
            for child in discovered[:10]:
                child_status, child_text, _ = fetch_text(session, child)
                sitemap_statuses[child] = child_status
                if child_status == 200:
                    page_urls.extend(parse_sitemap_urls(child_text))
        else:
            page_urls.extend(discovered)

    urls = [site]
    urls.extend(u for u in page_urls if u.startswith(site))
    urls = list(dict.fromkeys(urls))[:limit]
    return urls, {
        "robots_url": robots_url,
        "robots_status": robots_status,
        "sitemaps_found": sitemap_urls,
        "sitemap_statuses": sitemap_statuses,
        "discovered_urls": len(page_urls),
        "sampled_urls": len(urls),
    }


def visible_word_count(soup: BeautifulSoup) -> int:
    clean = BeautifulSoup(str(soup), "html.parser")
    for node in clean(["script", "style", "nav", "footer", "header", "aside", "noscript", "svg"]):
        node.decompose()
    text = re.sub(r"\s+", " ", clean.get_text(" ", strip=True))
    return len(re.findall(r"\b[\w'-]+\b", text))


def extract_schema_types(soup: BeautifulSoup) -> list[str]:
    found: set[str] = set()

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            schema_type = node.get("@type")
            if isinstance(schema_type, list):
                found.update(str(item) for item in schema_type)
            elif isinstance(schema_type, str):
                found.add(schema_type)
            graph = node.get("@graph")
            if isinstance(graph, list):
                for child in graph:
                    visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = script.string or script.get_text()
        if not raw or not raw.strip():
            continue
        try:
            visit(json.loads(raw))
        except json.JSONDecodeError:
            found.add("INVALID_JSON_LD")
    return sorted(found)


def score_ai_readiness(soup: BeautifulSoup, word_count: int, schema_types: list[str]) -> int:
    score = 35
    headings = " ".join(h.get_text(" ", strip=True).lower() for h in soup.find_all(["h2", "h3"]))
    if word_count >= 900:
        score += 20
    if any(token in headings for token in ["perguntas", "faq", "como", "quanto", "qual"]):
        score += 15
    if "Article" in schema_types or "BlogPosting" in schema_types:
        score += 15
    if soup.find("time") or re.search(r"20\d{2}", soup.get_text(" ", strip=True)[:3000]):
        score += 5
    if soup.find(attrs={"rel": "author"}) or "author" in " ".join(schema_types).lower():
        score += 5
    return max(0, min(score, 100))


def audit_page(session: requests.Session, url: str, site: str) -> PageAudit:
    status, html, _ = fetch_text(session, url)
    issues: list[str] = []
    if status != 200 or not html:
        return PageAudit(
            url=url,
            status=status,
            title="",
            title_len=0,
            meta_description="",
            meta_len=0,
            h1_count=0,
            h1=[],
            h2_count=0,
            canonical="",
            canonical_ok=False,
            word_count=0,
            internal_links=0,
            external_links=0,
            images_total=0,
            images_missing_alt=0,
            images_missing_dimensions=0,
            schema_types=[],
            has_article_schema=False,
            has_faq_schema=False,
            ai_readiness_score=0,
            score=0,
            issues=[f"Pagina retornou status {status}."],
        )

    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    meta = soup.find("meta", attrs={"name": "description"})
    meta_description = meta.get("content", "").strip() if meta else ""
    h1 = [h.get_text(" ", strip=True) for h in soup.find_all("h1") if h.get_text(" ", strip=True)]
    h2_count = len([h for h in soup.find_all("h2") if h.get_text(" ", strip=True)])
    canonical_node = soup.find("link", rel="canonical")
    canonical = canonical_node.get("href", "").strip() if canonical_node else ""
    canonical_ok = canonical.rstrip("/") == url.rstrip("/") if canonical else False
    word_count = visible_word_count(soup)

    internal_links = 0
    external_links = 0
    for link in soup.find_all("a", href=True):
        href = urljoin(url, link.get("href", ""))
        if href.startswith(site):
            internal_links += 1
        elif href.startswith("http"):
            external_links += 1

    images = soup.find_all("img")
    images_missing_alt = sum(1 for img in images if img.get("alt") is None or not img.get("alt", "").strip())
    images_missing_dimensions = sum(1 for img in images if not img.get("width") or not img.get("height"))
    schema_types = extract_schema_types(soup)
    ai_readiness = score_ai_readiness(soup, word_count, schema_types)

    score = 100
    if not title:
        score -= 16
        issues.append("Title tag ausente.")
    elif not 30 <= len(title) <= 65:
        score -= 6
        issues.append(f"Title com {len(title)} caracteres, fora da faixa ideal.")
    if not meta_description:
        score -= 14
        issues.append("Meta description ausente.")
    elif not 120 <= len(meta_description) <= 165:
        score -= 5
        issues.append(f"Meta description com {len(meta_description)} caracteres.")
    if len(h1) != 1:
        score -= 12
        issues.append(f"Pagina tem {len(h1)} H1.")
    if not h2_count:
        score -= 8
        issues.append("Pagina sem H2.")
    if not canonical:
        score -= 10
        issues.append("Canonical ausente.")
    elif not canonical_ok:
        score -= 7
        issues.append("Canonical nao corresponde a URL final.")
    if word_count < 500:
        score -= 10
        issues.append(f"Conteudo fino: {word_count} palavras.")
    if images_missing_alt:
        score -= min(12, images_missing_alt * 3)
        issues.append(f"{images_missing_alt} imagem(ns) sem alt.")
    if images_missing_dimensions:
        score -= min(8, images_missing_dimensions * 2)
        issues.append(f"{images_missing_dimensions} imagem(ns) sem width/height.")
    if "INVALID_JSON_LD" in schema_types:
        score -= 10
        issues.append("JSON-LD invalido detectado.")
    deprecated = sorted(set(schema_types) & DEPRECATED_SCHEMA_TYPES)
    if deprecated:
        score -= 8
        issues.append(f"Schema obsoleto detectado: {', '.join(deprecated)}.")
    if ai_readiness < 70:
        score -= 5
        issues.append("Baixa prontidao para AI Overviews/LLMs.")

    return PageAudit(
        url=url,
        status=status,
        title=title,
        title_len=len(title),
        meta_description=meta_description,
        meta_len=len(meta_description),
        h1_count=len(h1),
        h1=h1[:3],
        h2_count=h2_count,
        canonical=canonical,
        canonical_ok=canonical_ok,
        word_count=word_count,
        internal_links=internal_links,
        external_links=external_links,
        images_total=len(images),
        images_missing_alt=images_missing_alt,
        images_missing_dimensions=images_missing_dimensions,
        schema_types=schema_types,
        has_article_schema=bool({"Article", "BlogPosting"} & set(schema_types)),
        has_faq_schema="FAQPage" in schema_types,
        ai_readiness_score=ai_readiness,
        score=max(0, score),
        issues=issues,
    )


def audit_site(site: str, limit: int) -> dict[str, Any]:
    site = normalize_site(site)
    session = build_session()
    urls, discovery = discover_urls(session, site, limit)
    home_status, _, home_headers = fetch_text(session, site)
    pages = [audit_page(session, url, site) for url in urls]

    scores = [p.score for p in pages if p.status == 200]
    security_present = [h for h in SECURITY_HEADERS if h in {k.lower(): v for k, v in home_headers.items()}]
    security_score = 40 + len(security_present) * 12
    if not site.startswith("https://"):
        security_score -= 30
    security_score = max(0, min(security_score, 100))

    category_scores = {
        "technical": round(statistics.mean(scores) if scores else 0),
        "security": security_score,
        "sitemap": 90 if discovery["sitemaps_found"] else 50,
        "schema": round(statistics.mean([90 if p.schema_types else 55 for p in pages]) if pages else 0),
        "images": round(statistics.mean([100 - min(50, p.images_missing_alt * 8 + p.images_missing_dimensions * 4) for p in pages]) if pages else 0),
        "ai_readiness": round(statistics.mean([p.ai_readiness_score for p in pages]) if pages else 0),
    }
    overall = round(statistics.mean(category_scores.values())) if category_scores else 0

    priority_issues: list[dict[str, str]] = []
    if home_status != 200:
        priority_issues.append({"severity": "critical", "issue": f"Homepage retornou status {home_status}."})
    if discovery["robots_status"] != 200:
        priority_issues.append({"severity": "high", "issue": "robots.txt nao retornou 200."})
    if not discovery["sitemaps_found"]:
        priority_issues.append({"severity": "high", "issue": "Sitemap XML nao encontrado."})
    if security_score < 80:
        missing = [h for h in SECURITY_HEADERS if h not in security_present]
        priority_issues.append({"severity": "medium", "issue": f"Headers de seguranca ausentes: {', '.join(missing)}."})

    worst_pages = sorted(pages, key=lambda p: p.score)[:10]
    for page in worst_pages:
        for issue in page.issues[:2]:
            severity = "high" if page.score < 60 else "medium"
            priority_issues.append({"severity": severity, "issue": f"{page.url}: {issue}"})

    return {
        "tool": "auditoria_seo_clube3d",
        "inspired_by": "https://github.com/AgriciDaniel/codex-seo",
        "audited_at": now_iso(),
        "site": site,
        "overall_score": overall,
        "category_scores": category_scores,
        "discovery": discovery,
        "priority_issues": priority_issues[:20],
        "pages": [asdict(p) for p in pages],
    }


def compare_with_baseline(report: dict[str, Any]) -> dict[str, Any] | None:
    if not BASELINE_PATH.exists():
        return None
    try:
        baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return {
        "baseline_date": baseline.get("audited_at"),
        "score_delta": report["overall_score"] - baseline.get("overall_score", 0),
        "category_deltas": {
            key: report["category_scores"].get(key, 0) - baseline.get("category_scores", {}).get(key, 0)
            for key in report["category_scores"]
        },
    }


def render_markdown(report: dict[str, Any], drift: dict[str, Any] | None) -> str:
    scores = "\n".join(f"| {k} | {v} |" for k, v in report["category_scores"].items())
    issues = "\n".join(
        f"- **{item['severity']}**: {item['issue']}" for item in report["priority_issues"][:12]
    ) or "- Nenhum problema prioritario detectado."
    pages = sorted(report["pages"], key=lambda p: p["score"])[:10]
    page_rows = "\n".join(
        f"| {p['score']} | {p['title_len']} | {p['meta_len']} | {p['word_count']} | {p['images_missing_alt']} | {p['url']} |"
        for p in pages
    )
    drift_block = ""
    if drift:
        drift_rows = "\n".join(f"| {k} | {v:+d} |" for k, v in drift["category_deltas"].items())
        drift_block = f"""
## Drift desde baseline

- Baseline: {drift['baseline_date']}
- Delta geral: {drift['score_delta']:+d}

| Categoria | Delta |
|---|---:|
{drift_rows}
"""

    return f"""# Auditoria SEO Clube 3D Brasil

- Site: {report['site']}
- Data: {report['audited_at']}
- Score geral: **{report['overall_score']}/100**
- URLs descobertas no sitemap: {report['discovery']['discovered_urls']}
- URLs analisadas: {report['discovery']['sampled_urls']}

## Scores

| Categoria | Score |
|---|---:|
{scores}

## Prioridades

{issues}
{drift_block}
## Piores paginas na amostra

| Score | Title | Meta | Palavras | Alt ausente | URL |
|---:|---:|---:|---:|---:|---|
{page_rows}

## Como usar

1. Corrija primeiro problemas de indexacao, sitemap, canonical e meta.
2. Depois ajuste imagens sem alt e paginas com conteudo fino.
3. Rode novamente este script apos grandes mudancas no WordPress.
4. Use `--baseline` para salvar um ponto de comparacao.
"""


def save_report(report: dict[str, Any], baseline: bool) -> tuple[Path, Path]:
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    json_path = REPORT_ROOT / f"auditoria-seo-{stamp}.json"
    md_path = REPORT_ROOT / f"auditoria-seo-{stamp}.md"
    drift = compare_with_baseline(report)
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(report, drift), encoding="utf-8")
    if baseline:
        BASELINE_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return json_path, md_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Auditoria SEO deterministica do Clube 3D Brasil.")
    parser.add_argument("site", nargs="?", default=DEFAULT_SITE, help="Site raiz a auditar.")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="Limite de URLs do sitemap.")
    parser.add_argument("--baseline", action="store_true", help="Salva esta auditoria como baseline.")
    parser.add_argument("--json", action="store_true", help="Imprime JSON no terminal.")
    args = parser.parse_args()

    report = audit_site(args.site, max(1, min(args.limit, 200)))
    json_path, md_path = save_report(report, baseline=args.baseline)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Score geral: {report['overall_score']}/100")
        print(f"JSON: {json_path}")
        print(f"Markdown: {md_path}")
        if args.baseline:
            print(f"Baseline atualizado: {BASELINE_PATH}")


if __name__ == "__main__":
    main()
