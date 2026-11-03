"""Find public full-text copies by DOI, without interacting with challenges."""

import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlparse

import requests
from bs4 import BeautifulSoup

from config import BASE_DIR, settings
from http_policy import polite_get


def known_public_copy(doi):
    try:
        records = json.loads((BASE_DIR / "official_pdf_sources.json").read_text(encoding="utf-8"))
        return records.get(doi.lower(), {})
    except (OSError, ValueError):
        return {}


def check_openalex(doi):
    settings.refresh_api_credentials()
    headers = {"Accept": "application/json"}
    if settings.OPENALEX_API_KEY:
        headers["Authorization"] = "Bearer " + settings.OPENALEX_API_KEY
    try:
        with polite_get(
            "https://api.openalex.org/works/" + quote("https://doi.org/" + doi, safe=""),
            headers=headers, timeout=8,
        ) as response:
            if response.status_code != 200:
                return {}
            data = response.json()
        if (data.get("doi") or "").removeprefix("https://doi.org/").lower() != doi.lower():
            return {}
        locations = [data.get("best_oa_location") or {}] + (data.get("locations") or [])
        urls = list(dict.fromkeys(
            location["pdf_url"] for location in locations
            if location.get("is_oa") and location.get("pdf_url")
        ))
        return {"urls": urls, "title": data.get("title") or "", "source": "OpenAlex / kho toàn văn công khai"}
    except (requests.RequestException, ValueError, AttributeError, TypeError):
        return {}


def fetch_openalex_classification(doi, openalex_id=None):
    """Return OpenAlex topics and keywords for a work when the record is available."""
    settings.refresh_api_credentials()
    doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", str(doi or "").strip(), flags=re.IGNORECASE)
    openalex_id = str(openalex_id or "").strip()
    if not doi and not re.fullmatch(r"https?://openalex\.org/W\d+|W\d+", openalex_id, re.IGNORECASE):
        return {"status": "NO_IDENTIFIER"}
    work_id = openalex_id or ("https://doi.org/" + doi)
    headers = {"Accept": "application/json"}
    if settings.OPENALEX_API_KEY:
        headers["Authorization"] = "Bearer " + settings.OPENALEX_API_KEY
    try:
        url = "https://api.openalex.org/works/" + quote(work_id, safe="")
        with polite_get(url, headers=headers, timeout=12) as response:
            if response.status_code != 200:
                return {"status": "NOT_FOUND" if response.status_code == 404 else "UNAVAILABLE"}
            work = response.json()
    except (requests.RequestException, ValueError, AttributeError, TypeError):
        return {"status": "UNAVAILABLE"}

    resolved_doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", str(work.get("doi") or "").strip(), flags=re.IGNORECASE)
    if doi and resolved_doi.casefold() != doi.casefold():
        return {"status": "NOT_FOUND"}
    openalex_keywords = []
    seen_keywords = set()
    raw_keywords = work.get("keywords") if isinstance(work.get("keywords"), list) else []
    for item in raw_keywords:
        if not isinstance(item, dict):
            continue
        display_name = str(item.get("display_name") or "").strip()
        normalized = " ".join(display_name.casefold().split())
        if not display_name or normalized in seen_keywords:
            continue
        seen_keywords.add(normalized)
        score = item.get("score")
        openalex_keywords.append({
            "id": item.get("id") if isinstance(item.get("id"), str) else None,
            "display_name": display_name,
            "score": score if isinstance(score, (int, float)) and not isinstance(score, bool) else None,
        })
    open_access = work.get("open_access") if isinstance(work.get("open_access"), dict) else {}
    open_access_fields = {}
    if isinstance(open_access.get("is_oa"), bool):
        open_access_fields["isOpenAccess"] = open_access["is_oa"]
    best_oa_location = work.get("best_oa_location") if isinstance(work.get("best_oa_location"), dict) else {}
    open_access_url = (open_access.get("oa_url") or best_oa_location.get("pdf_url") or best_oa_location.get("landing_page_url"))
    if isinstance(open_access_url, str) and open_access_url.startswith(("https://", "http://")):
        open_access_fields["openAccessUrl"] = open_access_url
    primary = work.get("primary_topic") if isinstance(work.get("primary_topic"), dict) else {}
    topics = work.get("topics") if isinstance(work.get("topics"), list) else []
    topics = [topic for topic in topics if isinstance(topic, dict) and isinstance(topic.get("id"), str)]
    if isinstance(primary.get("id"), str) and all(topic.get("id") != primary["id"] for topic in topics):
        topics = [primary] + topics
    topics = topics[:20]
    if not topics:
        return {"status": "NOT_FOUND", "openAlexId": work.get("id"),
                "keywords": openalex_keywords, **open_access_fields}
    primary_topic_id = primary.get("id") if isinstance(primary.get("id"), str) else None

    def unique_ids(key):
        return list(dict.fromkeys(
            item[key]["id"] for item in topics
            if isinstance(item.get(key), dict) and isinstance(item[key].get("id"), str)
        ))

    classification = {
        "primaryTopicId": primary_topic_id,
        "topicIds": list(dict.fromkeys(topic["id"] for topic in topics)),
        "subfieldIds": unique_ids("subfield"),
        "fieldIds": unique_ids("field"),
        "domainIds": unique_ids("domain"),
    }
    classification = {key: value for key, value in classification.items() if value}
    return {
        "status": "MATCHED",
        **open_access_fields,
        "keywords": openalex_keywords,
        "classification": classification,
        "openAlexId": work.get("id"),
        "classificationProvenance": {
            "source": "OPENALEX_TOPICS",
            "workId": work.get("id"),
            "retrievedAt": datetime.now(timezone.utc).isoformat(),
            "topics": [{
                "id": topic.get("id"),
                "label": topic.get("display_name"),
                "score": topic.get("score"),
                "subfieldId": (topic.get("subfield") or {}).get("id")
                if isinstance(topic.get("subfield"), dict) else None,
                "subfield": (topic.get("subfield") or {}).get("display_name")
                if isinstance(topic.get("subfield"), dict) else None,
                "fieldId": (topic.get("field") or {}).get("id")
                if isinstance(topic.get("field"), dict) else None,
                "field": (topic.get("field") or {}).get("display_name")
                if isinstance(topic.get("field"), dict) else None,
                "domainId": (topic.get("domain") or {}).get("id")
                if isinstance(topic.get("domain"), dict) else None,
                "domain": (topic.get("domain") or {}).get("display_name")
                if isinstance(topic.get("domain"), dict) else None,
            } for topic in topics[:20]],
        },
    }


def check_pmc(doi):
    """Use PMC's official identifier/OA APIs, including embargo checks."""
    try:
        with polite_get("https://pmc.ncbi.nlm.nih.gov/tools/idconv/api/v1/articles/",
                        params={"ids": doi, "idtype": "doi", "format": "json", "tool": "SLRPaperFetcher", "email": settings.UNPAYWALL_EMAIL},
                        timeout=8) as response:
            if response.status_code != 200:
                return {}
            records = response.json().get("records", [])
        record = next((record for record in records if str(record.get("doi", "")).lower() == doi.lower()), {})
        pmcid = record.get("pmcid", "")
        if not re.fullmatch(r"PMC\d+", pmcid) or str(record.get("live", "true")).lower() == "false":
            return {}
        with polite_get("https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi", params={"id": pmcid}, timeout=8) as response:
            if response.status_code != 200:
                return {}
            document = BeautifulSoup(response.content, "xml")
        urls = []
        for link in document.select('record link[format="pdf"]'):
            url = link.get("href", "")
            if urlparse(url).hostname == "ftp.ncbi.nlm.nih.gov":
                urls.append(url.replace("ftp://", "https://", 1))
        return {"urls": urls, "source": "PMC Open Access", "landing_url": "https://pmc.ncbi.nlm.nih.gov/articles/" + pmcid + "/"}
    except (requests.RequestException, ValueError, AttributeError, TypeError):
        return {}


def download_public_copy(doi, title, output_path, progress_callback=None, status_callback=None):
    # Imported here so the browser engine can call this module without a cycle.
    from downloader_engine import check_arxiv, check_unpaywall, check_semantic_scholar, download_file_direct

    attempted = set()
    failures = []

    def try_source(info):
        urls = info.get("urls") or ([info["url"]] if info.get("url") else [])
        for url in urls[:6]:
            if url in attempted or urlparse(url).scheme not in ("https", "http"):
                continue
            attempted.add(url)
            success, message = download_file_direct(
                url, Path(output_path),
                (lambda percent, received, total: progress_callback(percent)) if progress_callback else None,
            )
            if success:
                return True, f"Đã tải PDF tự động từ {info.get('source') or 'nguồn toàn văn công khai'}."
            failures.append((urlparse(url).hostname or "nguồn PDF") + ": " + message)
        return False, ""

    if status_callback:
        status_callback("checking_public_sources")
    known = known_public_copy(doi)
    if known:
        success, message = try_source(known)
        if success:
            return success, message
        title = title or known.get("title")

    # One request per provider at a time per article, maximum three independent
    # providers. The application's download lanes bound concurrent articles.
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(provider, doi) for provider in (check_unpaywall, check_semantic_scholar, check_openalex, check_pmc)]
        candidates = []
        for future in as_completed(futures):
            try:
                info = future.result()
            except Exception:
                continue
            title = title or info.get("title")
            if info.get("urls") or (info.get("has_pdf") and info.get("url")):
                candidates.append(info)
    for info in candidates:
        success, message = try_source(info)
        if success:
            return success, message

    if status_callback:
        status_callback("checking_arxiv")
    info = check_arxiv(doi, title or None)
    if info.get("has_pdf"):
        success, message = try_source(info)
        if success:
            return success, message
    from downloader_engine import publisher_pdf_candidates
    constructed = publisher_pdf_candidates(doi)
    if constructed:
        success, message = try_source({"urls": constructed, "source": "đường dẫn PDF chuẩn của nhà xuất bản"})
        if success:
            return success, message
    from paper_io import safe_message
    details = " Phản hồi nguồn: " + "; ".join(failures[-3:]) if failures else ""
    return False, safe_message("Chưa tìm được PDF tải được từ các nguồn toàn văn công khai." + details)
