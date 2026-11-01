import sys
import asyncio

import os
import re
import io
import json
from datetime import datetime, timezone
import hashlib
import webbrowser
import threading
import subprocess
from pathlib import Path
import uvicorn
import requests
from typing import List, Optional
from urllib.parse import urlparse
from fastapi import FastAPI, File, UploadFile, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
from config import settings
from config import BASE_DIR
from contextlib import asynccontextmanager
from paper_io import download_path, safe_filename, valid_pdf_file, valid_pdf_bytes, safe_message, public_url, institutional_url, generate_standardized_filename, normalize_doi
from paper_store import get_store
from doi_resolver import resolve_doi
from browser_session import browser_manager, browser_worker

_ANALYSIS_QUEUE = None
_ANALYSIS_WORKER = None
_BROWSER_START_TASK = None
_UI_OPEN_TASK = None
_SAFFRON_START_TASK = None
_SAFFRON_RETRY_LOCKS = {}
_SAFFRON_RUNTIME_STATE = {"status": "disabled", "message": "SAFFRON is disabled."}
_OPENALEX_BACKFILL_LOCK = threading.Lock()
_OPENALEX_BACKFILL_STATE = {
    "status": "idle", "total": 0, "processed": 0, "matched": 0,
    "not_found": 0, "unavailable": 0, "current_doi": "", "message": "",
}

def _analysis_paper_id(value):
    doi = normalize_doi(str(value or ""))
    if doi:
        return doi
    candidate = str(value or "").strip()
    return candidate if re.fullmatch(r"slrwork_[A-Za-z0-9_-]{1,200}", candidate) else ""


def _valid_analysis_source(path):
    source = Path(path or "")
    if not source.is_file():
        return False
    if source.suffix.lower() == ".pdf":
        return valid_pdf_file(source)
    if source.suffix.lower() in {".md", ".markdown"}:
        try:
            return bool(source.read_text(encoding="utf-8").strip())
        except (OSError, UnicodeDecodeError):
            return False
    return False


async def _analysis_worker():
    while True:
        doi, provider = await _ANALYSIS_QUEUE.get()
        store = get_store()
        try:
            store.save_analysis(doi, "PROCESSING", provider=provider, stage="starting")
            paper = store.get(doi)
            metadata = json.loads((paper or {}).get("metadata") or "{}")
            from ai_analysis import analyze_markdown, analyze_pdf
            def report_stage(stage):
                store.update_analysis_stage(doi, stage)
            analyzer = analyze_markdown if Path(paper["file_path"]).suffix.lower() in {".md", ".markdown"} else analyze_pdf
            result, model = await asyncio.to_thread(analyzer, doi, paper["file_path"], provider, report_stage)
            if settings.SAFFRON_ENABLED:
                store.update_analysis_stage(doi, "saffron_term_taxonomy")
                try:
                    from saffron_client import SaffronClient
                    mapping_path = Path(paper["file_path"]).with_suffix(".fulltext.json")
                    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
                    document_metadata = result.get("document", {}).get("metadata", {})
                    if mapping.get("source_kind") == "markdown":
                        expected_source_hash = document_metadata.get("source_markdown", {}).get("sha256")
                        if mapping.get("source_markdown_sha256") != expected_source_hash:
                            raise ValueError("Markdown mapping SHA-256 does not match this paper analysis run.")
                    else:
                        expected_source_hash = document_metadata.get("pdf_artifact", {}).get("sha256")
                        if mapping.get("source_pdf_sha256") != expected_source_hash:
                            raise ValueError("Full-text mapping SHA-256 does not match this paper analysis run.")
                    result["saffron_analysis"] = await asyncio.to_thread(
                        SaffronClient().analyze_paper,
                        doi=doi,
                        title=metadata.get("title") or doi,
                        mapping=mapping,
                        paper_metadata=metadata,
                    )
                except Exception as exc:
                    result["saffron_analysis"] = {
                        "schema_version": "1.0", "status": "FAILED",
                        "error": str(exc)[:500],
                        "terms": [], "taxonomy": {"status": "FAILED", "nodes": [], "edges": []},
                    }
            else:
                result["saffron_analysis"] = {
                    "schema_version": "1.0", "status": "SKIPPED",
                    "error": "SAFFRON is disabled in Fetcher settings.",
                    "terms": [], "taxonomy": {"status": "SKIPPED", "nodes": [], "edges": []},
                }
            try:
                from automatic_sources import fetch_openalex_classification
                classification_doi = "" if str(doi).startswith("slrwork_") else doi
                openalex_fields = await asyncio.to_thread(
                    fetch_openalex_classification, classification_doi, metadata.get("openAlexId")
                )
                result["openalex_classification"] = _openalex_classification_artifact(openalex_fields) or {
                    "schema_version": "openalex-topics.v1",
                    "status": (openalex_fields or {}).get("status", "NOT_FOUND"),
                    "provenance": {"source": "OPENALEX_TOPICS"},
                }
            except Exception as exc:
                print(f"[OPENALEX] Per-paper classification unavailable for {doi}: {exc}")
                result["openalex_classification"] = {
                    "schema_version": "openalex-topics.v1", "status": "UNAVAILABLE",
                    "provenance": {"source": "OPENALEX_TOPICS"},
                }
            result["argumentation"]["document"]["metadata"].update({
                "paper_title": metadata.get("title") or doi,
                "filename": paper.get("filename") or "",
            })
            await asyncio.to_thread(store.save_argumentation, doi, result["argumentation"])
            store.save_analysis(
                doi, "DONE", provider=provider, model=model,
                draft={**result, "paper": {
                    "title": metadata.get("title") or doi,
                    "filename": paper.get("filename") or "",
                }}, stage="completed",
            )
            if metadata.get("slr_repository_work_id"):
                sync = await asyncio.to_thread(
                    _push_paper_to_repository, store, doi, paper, paper.get("file_path"),
                    settings.SLR_API_BASE_URL, settings.SLR_API_KEY,
                )
                if not sync.get("success"):
                    print(f"[REPOSITORY] Analysis for {metadata['slr_repository_work_id']} remains local: {sync.get('message', 'sync failed')}")
        except Exception as exc:
            store.save_analysis(doi, "FAILED", provider=provider, error=str(exc)[:500], stage="failed")
        finally:
            _ANALYSIS_QUEUE.task_done()

@asynccontextmanager
async def lifespan(app):
    global _ANALYSIS_QUEUE, _ANALYSIS_WORKER, _BROWSER_START_TASK, _UI_OPEN_TASK, _SAFFRON_START_TASK
    get_store()
    await asyncio.to_thread(get_store().recover_interrupted_downloads)
    _ANALYSIS_QUEUE = asyncio.Queue()
    for analysis in await asyncio.to_thread(get_store().list_analyses):
        if analysis["status"] == "PENDING":
            _ANALYSIS_QUEUE.put_nowait((analysis["doi"], analysis.get("provider") or "ollama"))
        elif analysis["status"] == "PROCESSING":
            get_store().save_analysis(analysis["doi"], "FAILED", provider=analysis.get("provider"), error="App đã khởi động lại khi đang phân tích. Hãy thử lại.")
    _ANALYSIS_WORKER = asyncio.create_task(_analysis_worker())
    if settings.SAFFRON_ENABLED:
        async def start_saffron():
            global _SAFFRON_RUNTIME_STATE
            _SAFFRON_RUNTIME_STATE = {"status": "starting", "message": "Checking SAFFRON service."}
            try:
                from saffron_client import SaffronClient
                await asyncio.to_thread(SaffronClient().ensure_ready)
                _SAFFRON_RUNTIME_STATE = {"status": "ready", "message": "SAFFRON service is ready."}
            except Exception as exc:
                _SAFFRON_RUNTIME_STATE = {"status": "unavailable", "message": str(exc)[:500]}
                print(f"[SAFFRON] Warning: service is unavailable: {exc}")
        _SAFFRON_START_TASK = asyncio.create_task(start_saffron())
    else:
        _SAFFRON_RUNTIME_STATE = {"status": "disabled", "message": "SAFFRON is disabled."}
    async def start_browser():
        try:
            await browser_manager.start()
        except Exception as e:
            print(f"[BROWSER] Warning: Could not start browser at startup: {e}")

    # Browser/profile startup can take a while or fail independently of the web
    # app. Keep it out of ASGI startup so the UI and API remain available.
    _BROWSER_START_TASK = asyncio.create_task(start_browser())
    if settings.AUTO_OPEN_BROWSER:
        async def open_ui():
            import urllib.request
            url = f"http://{settings.APP_HOST}:{settings.APP_PORT}"
            health_url = f"{url}/api/health"
            try:
                ready = False
                for _ in range(30):
                    await asyncio.sleep(0.5)
                    try:
                        def check_health():
                            with urllib.request.urlopen(health_url, timeout=1) as resp:
                                return resp.status == 200
                        ready = await asyncio.to_thread(check_health)
                        if ready:
                            break
                    except Exception:
                        continue
                if not ready:
                    print("[UI] Warning: Web interface did not become ready; browser was not opened.")
                    return

                try:
                    await asyncio.wait_for(asyncio.shield(_BROWSER_START_TASK), timeout=10)
                except asyncio.TimeoutError:
                    print("[BROWSER] Startup is taking longer than expected; opening the web interface directly.")

                if browser_manager.anchor and not browser_manager.anchor.is_closed():
                    print(f"[UI] Opening web interface in primary browser window: {url}")
                    await browser_manager.run(browser_manager.anchor.goto, url)
                    await browser_manager.run(browser_manager.anchor.bring_to_front)
                else:
                    await asyncio.to_thread(webbrowser.open, url)
            except Exception as e:
                print(f"[UI] Warning: Could not open web interface automatically: {e}")
        _UI_OPEN_TASK = asyncio.create_task(open_ui())
    yield
    for task in (_UI_OPEN_TASK, _BROWSER_START_TASK):
        if task and not task.done():
            task.cancel()
    await asyncio.gather(*[task for task in (_UI_OPEN_TASK, _BROWSER_START_TASK) if task], return_exceptions=True)
    if _ANALYSIS_WORKER:
        _ANALYSIS_WORKER.cancel()
        await asyncio.gather(_ANALYSIS_WORKER, return_exceptions=True)
    browser_manager.request_shutdown()
    if _DOWNLOAD_JOBS:
        await asyncio.gather(*list(_DOWNLOAD_JOBS), return_exceptions=True)
    from downloader_engine import _PIPELINE_JOBS
    if _PIPELINE_JOBS:
        await asyncio.gather(*list(_PIPELINE_JOBS), return_exceptions=True)
    await browser_manager.shutdown()

app = FastAPI(title="SLR Paper Fetcher", lifespan=lifespan)
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

def _publisher_url_from_message(message: str) -> Optional[str]:
    match = re.search(r"URL='([^']+)'", message or "")
    if not match:
        return None
    candidate = match.group(1).strip()
    parsed = urlparse(candidate)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return None
    return candidate

# Check if templates directory exists, if not, create it
os.makedirs("templates", exist_ok=True)
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

from downloader_engine import (
    extract_doi, 
    find_paper_fulltext, 
    download_file_direct, 
    auto_download_paper,
    import_verified_pdf,
    get_paper_ris,
    generate_combined_ris
)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={
        "vnu_configured": bool(settings.VNU_LIBRARY_ID and settings.VNU_LIBRARY_PASSWORD),
        "active_tab": "fetch"
    })

@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse(request=request, name="upload.html", context={
        "vnu_configured": bool(settings.VNU_LIBRARY_ID and settings.VNU_LIBRARY_PASSWORD),
        "active_tab": "upload"
    })

@app.get("/repository", response_class=HTMLResponse)
async def repository_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={
        "vnu_configured": bool(settings.VNU_LIBRARY_ID and settings.VNU_LIBRARY_PASSWORD),
        "active_tab": "repository"
    })


@app.get("/analysis", response_class=HTMLResponse)
async def analysis_page(request: Request):
    response = templates.TemplateResponse(request=request, name="analysis.html", context={"paper_detail_mode": False, "active_tab": "analysis", "vnu_configured": bool(settings.VNU_LIBRARY_ID and settings.VNU_LIBRARY_PASSWORD)})
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    return response


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    return templates.TemplateResponse(request=request, name="settings.html", context={
        "active_tab": "settings",
        "vnu_configured": bool(settings.VNU_LIBRARY_ID and settings.VNU_LIBRARY_PASSWORD),
    })


@app.get("/analysis/paper/{doi:path}", response_class=HTMLResponse)
async def paper_analysis_page(request: Request, doi: str):
    normalized = _analysis_paper_id(doi)
    if not normalized:
        return HTMLResponse("Invalid paper identifier.", status_code=404)
    response = templates.TemplateResponse(request=request, name="analysis.html", context={
        "paper_detail_mode": True, "paper_id": normalized, "active_tab": "analysis",
        "vnu_configured": bool(settings.VNU_LIBRARY_ID and settings.VNU_LIBRARY_PASSWORD),
    })
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    return response


@app.get("/api/analysis/pdf/{doi:path}")
async def analysis_pdf(doi: str):
    normalized = _analysis_paper_id(doi)
    if not normalized:
        return JSONResponse({"error": "Invalid DOI."}, status_code=400)
    record = await asyncio.to_thread(get_store().downloaded, normalized)
    if not record or Path(record.get("file_path") or "").suffix.lower() != ".pdf" or not valid_pdf_file(record.get("file_path") or ""):
        return JSONResponse({"error": "A valid saved PDF is not available for this paper."}, status_code=404)
    return FileResponse(path=record["file_path"], media_type="application/pdf",
                        headers={"Content-Disposition": "inline"})


@app.get("/api/analysis/source/{paper_id:path}")
async def analysis_source(paper_id: str):
    normalized = _analysis_paper_id(paper_id)
    if not normalized:
        return JSONResponse({"error": "Invalid paper identifier."}, status_code=400)
    record = await asyncio.to_thread(get_store().downloaded, normalized)
    if not record or not _valid_analysis_source(record.get("file_path")):
        return JSONResponse({"error": "A valid saved PDF or Markdown source is not available for this paper."}, status_code=404)
    path = Path(record["file_path"])
    media_type = "application/pdf" if path.suffix.lower() == ".pdf" else "text/markdown; charset=utf-8"
    return FileResponse(path=path, media_type=media_type, headers={"Content-Disposition": "inline"})


@app.get("/api/analysis/papers")
async def analysis_papers():
    store = get_store()
    records = await asyncio.to_thread(store.list, 2000)
    analyses = {row["doi"]: row for row in await asyncio.to_thread(store.list_analyses)}
    papers = []
    for record in records:
        if record["status"] != "DOWNLOADED" or not _valid_analysis_source(record.get("file_path")):
            continue
        try:
            metadata = json.loads(record.get("metadata") or "{}")
        except (TypeError, ValueError):
            metadata = {}
        analysis = analyses.get(record["doi"], {})
        papers.append({
            "doi": record["doi"], "title": metadata.get("title") or record["doi"],
            "authors": metadata.get("authors") or "", "year": metadata.get("year") or "",
            "journal": metadata.get("journal") or metadata.get("venue") or "",
            "filename": record.get("filename") or "", "provider": record.get("provider") or "",
            "source_kind": "markdown" if Path(record["file_path"]).suffix.lower() in {".md", ".markdown"} else "pdf",
            "analysis_status": analysis.get("status", "NOT_STARTED"),
            "analysis_provider": analysis.get("provider") or "",
            "analysis_model": analysis.get("model") or "",
            "analysis_error": analysis.get("error") or "",
            "analysis_stage": analysis.get("stage") or "",
            "updated_at": analysis.get("updated_at") or "",
        })
    return {"papers": papers, "total": len(papers)}


@app.get("/api/analysis/config")
async def analysis_config():
    def reachable(url):
        try:
            return requests.get(url, timeout=2).status_code == 200
        except requests.RequestException:
            return False
    grobid_ready, ollama_ready = await asyncio.gather(
        asyncio.to_thread(reachable, f"{settings.GROBID_URL}/api/isalive"),
        asyncio.to_thread(reachable, f"{settings.OLLAMA_URL}/api/tags"),
    )
    return JSONResponse({
        "default_provider": settings.AI_DEFAULT_PROVIDER if settings.AI_DEFAULT_PROVIDER in {"ollama", "gemini"} and (settings.AI_DEFAULT_PROVIDER != "gemini" or settings.GEMINI_API_KEY) else "ollama",
        "ollama_url": settings.OLLAMA_URL,
        "ollama_model": settings.OLLAMA_MODEL,
        "gemini_model": settings.GEMINI_MODEL,
        "gemini_configured": bool(settings.GEMINI_API_KEY),
        "grobid_ready": grobid_ready,
        "ollama_ready": ollama_ready,
    }, headers={"Cache-Control": "no-store"})


@app.post("/api/analysis/config")
async def update_analysis_config(request: Request):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"success": False, "error": "Invalid JSON configuration."}, status_code=400)
    if not isinstance(data, dict):
        return JSONResponse({"success": False, "error": "Configuration must be a JSON object."}, status_code=400)

    provider = str(data.get("default_provider") or "").strip().lower()
    ollama_url = str(data.get("ollama_url") or "").strip().rstrip("/")
    ollama_model = str(data.get("ollama_model") or "").strip()
    gemini_model = str(data.get("gemini_model") or "").strip()
    api_key = str(data.get("gemini_api_key") or "").strip()
    clear_api_key = data.get("clear_gemini_key") is True

    if provider not in {"ollama", "gemini"}:
        return JSONResponse({"success": False, "error": "Choose Ollama or Gemini as the default provider."}, status_code=400)
    try:
        parsed_url = urlparse(ollama_url)
    except ValueError:
        return JSONResponse({"success": False, "error": "Enter a valid Ollama URL starting with http:// or https://."}, status_code=400)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.hostname or parsed_url.username or parsed_url.password or len(ollama_url) > 500:
        return JSONResponse({"success": False, "error": "Enter a valid Ollama URL starting with http:// or https://."}, status_code=400)
    if not ollama_model or len(ollama_model) > 200 or not gemini_model or len(gemini_model) > 200:
        return JSONResponse({"success": False, "error": "Model names must be between 1 and 200 characters."}, status_code=400)
    if len(api_key) > 4096 or "\n" in api_key or "\r" in api_key:
        return JSONResponse({"success": False, "error": "The Gemini API key is invalid."}, status_code=400)

    next_api_key = "" if clear_api_key else (api_key or settings.GEMINI_API_KEY)
    if provider == "gemini" and not next_api_key:
        return JSONResponse({"success": False, "error": "Enter a Gemini API key before choosing Gemini."}, status_code=400)

    try:
        from config import ENV_PATH
        from dotenv import set_key
        for key, value in (
            ("AI_DEFAULT_PROVIDER", provider),
            ("OLLAMA_URL", ollama_url),
            ("OLLAMA_MODEL", ollama_model),
            ("GEMINI_MODEL", gemini_model),
            ("GEMINI_API_KEY", next_api_key),
        ):
            result = set_key(str(ENV_PATH), key, value, quote_mode="always")
            if not result[0]:
                raise OSError(f"Could not persist {key} to .env")
    except Exception as exc:
        print(f"[AI CONFIG] Could not save settings: {exc}")
        return JSONResponse({"success": False, "error": "Could not save settings to the local .env file."}, status_code=500)

    settings.AI_DEFAULT_PROVIDER = provider
    settings.OLLAMA_URL = ollama_url
    settings.OLLAMA_MODEL = ollama_model
    settings.GEMINI_MODEL = gemini_model
    settings.GEMINI_API_KEY = next_api_key
    return {
        "success": True,
        "config": {
            "default_provider": provider,
            "ollama_url": ollama_url,
            "ollama_model": ollama_model,
            "gemini_model": gemini_model,
            "gemini_configured": bool(next_api_key),
        },
    }


@app.get("/api/analysis/draft/{doi:path}")
async def analysis_draft(doi: str):
    normalized = _analysis_paper_id(doi)
    if not normalized:
        return JSONResponse({"error": "Invalid DOI."}, status_code=400)
    record = await asyncio.to_thread(get_store().get_analysis, normalized)
    if not record or record.get("status") != "DONE" or not record.get("draft"):
        return JSONResponse({"error": "No completed analysis draft is available."}, status_code=404)
    try:
        draft = json.loads(record["draft"])
    except (TypeError, ValueError):
        return JSONResponse({"error": "The saved analysis draft has an invalid format."}, status_code=500)
    # The analysis draft also stores the full extracted document and a copy of
    # the argumentation graph. The detail page only needs these display fields;
    # send the graph through its own request so the overview can render first.
    record["draft"] = {
        "grobid": draft.get("grobid") or {},
        "analysis": draft.get("analysis") or {},
        "saffron_analysis": draft.get("saffron_analysis") or {
            "schema_version": "1.0", "status": "NOT_AVAILABLE", "terms": [],
            "taxonomy": {"status": "NOT_AVAILABLE", "nodes": [], "edges": []},
        },
        "openalex_classification": draft.get("openalex_classification") or {
            "schema_version": "openalex-topics.v1", "status": "NOT_ANALYZED",
            "provenance": {"source": "OPENALEX_TOPICS"},
        },
    }
    return {"analysis": record}


@app.post("/api/analysis/saffron/retry")
async def retry_saffron_analysis(request: Request):
    if not settings.SAFFRON_ENABLED:
        return JSONResponse({"error": "SAFFRON is disabled in Fetcher settings."}, status_code=503)
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON request."}, status_code=400)
    doi = extract_doi(str(body.get("doi") or "")) if isinstance(body, dict) else ""
    if not doi:
        return JSONResponse({"error": "A valid DOI is required."}, status_code=400)

    lock = _SAFFRON_RETRY_LOCKS.setdefault(doi, asyncio.Lock())
    async with lock:
        store = get_store()
        analysis = await asyncio.to_thread(store.get_analysis, doi)
        if not analysis or analysis.get("status") != "DONE" or not analysis.get("draft"):
            return JSONResponse({"error": "A completed AI analysis is required before retrying SAFFRON."}, status_code=409)
        paper = await asyncio.to_thread(store.get, doi)
        if not paper or paper.get("status") != "DOWNLOADED" or not valid_pdf_file(paper.get("file_path") or ""):
            return JSONResponse({"error": "A valid saved PDF is not available for this paper."}, status_code=409)

        pdf_path = Path(paper["file_path"])
        mapping_path = pdf_path.with_suffix(".fulltext.json")
        if not mapping_path.is_file():
            return JSONResponse({"error": "The validated full-text mapping is missing."}, status_code=409)
        try:
            draft = json.loads(analysis["draft"]) if isinstance(analysis["draft"], str) else analysis["draft"]
            mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
            metadata = json.loads(paper.get("metadata") or "{}") if isinstance(paper.get("metadata"), str) else (paper.get("metadata") or {})
        except (OSError, TypeError, ValueError):
            return JSONResponse({"error": "The saved analysis metadata or full-text mapping is invalid."}, status_code=409)
        if not isinstance(draft, dict) or not isinstance(mapping, dict) or not isinstance(metadata, dict):
            return JSONResponse({"error": "The saved analysis metadata or full-text mapping is invalid."}, status_code=409)

        try:
            current_pdf_sha256 = await asyncio.to_thread(lambda: hashlib.sha256(pdf_path.read_bytes()).hexdigest())
        except OSError:
            return JSONResponse({"error": "The saved PDF could not be read."}, status_code=409)
        mapped_pdf_sha256 = mapping.get("source_pdf_sha256")
        document = draft.get("document") if isinstance(draft.get("document"), dict) else {}
        document_metadata = document.get("metadata") if isinstance(document.get("metadata"), dict) else {}
        pdf_artifact = document_metadata.get("pdf_artifact") if isinstance(document_metadata.get("pdf_artifact"), dict) else {}
        analyzed_pdf_sha256 = pdf_artifact.get("sha256")
        if not mapped_pdf_sha256:
            return JSONResponse({"error": "This full-text mapping predates checksum pinning; reanalyze the paper before retrying SAFFRON."}, status_code=409)
        if mapped_pdf_sha256 != current_pdf_sha256 or (analyzed_pdf_sha256 and analyzed_pdf_sha256 != current_pdf_sha256):
            return JSONResponse({"error": "The PDF changed after its analysis; regenerate the full-text mapping before retrying SAFFRON."}, status_code=409)

        try:
            from saffron_client import SaffronClient
            grobid = draft.get("grobid") if isinstance(draft.get("grobid"), dict) else {}
            result = await asyncio.to_thread(
                SaffronClient().analyze_paper,
                doi=doi,
                title=metadata.get("title") or grobid.get("title") or doi,
                mapping=mapping,
                paper_metadata=metadata,
            )
        except Exception as exc:
            return JSONResponse({"error": str(exc)[:500]}, status_code=502)

        updated = await asyncio.to_thread(store.update_saffron_analysis, doi, result)
        if not updated:
            return JSONResponse({"error": "The AI analysis changed while SAFFRON was running; retry against the latest draft."}, status_code=409)
        return {
            "success": True,
            "status": result.get("status", "FAILED"),
            "term_count": len(result.get("terms") or []),
            "taxonomy_status": (result.get("taxonomy") or {}).get("status", "NOT_AVAILABLE"),
        }


@app.get("/api/analysis/argumentation/{doi:path}")
async def analysis_argumentation(doi: str):
    normalized = _analysis_paper_id(doi)
    if not normalized:
        return JSONResponse({"error": "Invalid DOI."}, status_code=400)
    argumentation = await asyncio.to_thread(get_store().get_argumentation, normalized)
    if not argumentation:
        return JSONResponse({"error": "No structured argumentation is available for this paper."}, status_code=404)
    return {"argumentation": argumentation}


@app.post("/api/analysis/review/{doi:path}")
async def review_analysis_item(doi: str, request: Request):
    normalized = _analysis_paper_id(doi)
    if not normalized:
        return JSONResponse({"error": "Invalid DOI."}, status_code=400)
    body = await request.json()
    try:
        accepted = await asyncio.to_thread(get_store().review_analysis_item, normalized,
            str(body.get("item_id") or ""), str(body.get("item_type") or ""),
            str(body.get("decision") or ""), str(body.get("note") or ""))
    except ValueError as exc:
        return JSONResponse({"error": str(exc)}, status_code=400)
    if not accepted:
        return JSONResponse({"error": "Analysis item not found for review."}, status_code=404)
    return {"success": True}


@app.patch("/api/analysis/edit/{doi:path}")
async def edit_analysis_item(doi: str, request: Request):
    normalized = _analysis_paper_id(doi)
    if not normalized:
        return JSONResponse({"error": "Invalid DOI."}, status_code=400)
    body = await request.json()
    try:
        accepted = await asyncio.to_thread(get_store().edit_analysis_item, normalized,
            str(body.get("item_id") or ""), str(body.get("item_type") or ""),
            body.get("changes") or {}, str(body.get("note") or ""))
    except ValueError as exc:
        return JSONResponse({"error": str(exc)}, status_code=400)
    if not accepted:
        return JSONResponse({"error": "Analysis item not found for editing."}, status_code=404)
    return {"success": True}


@app.post("/api/analysis/mvp3/{doi:path}")
async def evaluate_mvp3(doi: str, request: Request):
    normalized = _analysis_paper_id(doi)
    if not normalized:
        return JSONResponse({"error": "Invalid DOI."}, status_code=400)
    body = await request.json()
    argument_id = str(body.get("argument_id") or "").strip()
    if not argument_id:
        return JSONResponse({"error": "Select one argument before running MVP3."}, status_code=400)
    provider = str(body.get("provider") or settings.AI_DEFAULT_PROVIDER or "ollama").strip().lower()
    if provider not in {"ollama", "gemini"}:
        return JSONResponse({"error": "Invalid AI provider."}, status_code=400)
    if provider == "gemini" and not settings.GEMINI_API_KEY:
        return JSONResponse({"error": "GEMINI_API_KEY is not configured in .env."}, status_code=400)
    store = get_store()
    run = await asyncio.to_thread(store.get_argumentation, normalized)
    if not run:
        return JSONResponse({"error": "No saved argument analysis is available."}, status_code=404)
    if not any(item.get("id") == argument_id for item in run.get("analysis_payload", {}).get("arguments", [])):
        return JSONResponse({"error": "The selected argument is not part of this analysis."}, status_code=404)

    document_metadata = run.get("document_metadata", {})
    selected_argument = next(item for item in run.get("analysis_payload", {}).get("arguments", [])
                             if item.get("id") == argument_id)
    selected_proposition = next((item for item in run.get("propositions", [])
                                 if item.get("id") == selected_argument.get("claim_proposition_id")), {})
    source_quote = " ".join((selected_proposition.get("source_quote") or "").split()).casefold()
    relevant_reference_ids = {
        str(reference_id).lstrip("#")
        for callout in document_metadata.get("citation_callouts", [])
        if " ".join((callout.get("marker") or "").split()).casefold() in source_quote
        for reference_id in callout.get("reference_ids", [])
    }
    reference_sources = {}
    for entry in document_metadata.get("bibliography", []):
        if not isinstance(entry, dict):
            continue
        if str(entry.get("reference_id") or "").lstrip("#") not in relevant_reference_ids:
            continue
        cited_doi = normalize_doi(entry.get("doi"))
        if not cited_doi or cited_doi in reference_sources:
            continue
        cited_run = await asyncio.to_thread(store.get_argumentation, cited_doi)
        sections = (cited_run or {}).get("sections", [])
        section_priority = {"abstract": 0, "results": 1, "discussion": 2, "conclusion": 3,
                            "methods": 4, "introduction": 5}
        ordered_sections = sorted(sections, key=lambda section: section_priority.get(section.get("section_type"), 6))
        section_parts, remaining, original_characters = [], 8000, 0
        for section in ordered_sections:
            text = (section.get("text") or "").strip()
            original_characters += len(text)
            if text and remaining > 0:
                part = ((section.get("heading") or "") + "\n" + text)[:remaining]
                section_parts.append(part)
                remaining -= len(part)
        section_text = "\n\n".join(section_parts)
        if not section_text:
            continue
        metadata = (cited_run or {}).get("document_metadata", {})
        reference_sources[cited_doi] = {
            "source_type": "local_full_text",
            "source_title": metadata.get("title") or entry.get("title"),
            "source_uri": "https://doi.org/" + cited_doi,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "source_text": section_text,
            "source_excerpt": section_text[:700],
            "source_character_count": original_characters,
            "full_text_available": True,
        }
    from ai_analysis import run_mvp3_evaluation
    try:
        evaluation = await asyncio.to_thread(
            run_mvp3_evaluation, run.get("propositions", []), run.get("graph", {}),
            run.get("analysis_payload", {}), run.get("document_metadata", {}), provider,
            argument_id, reference_sources,
        )
        evaluation.setdefault("provenance", {})["analysis_run_id"] = run["id"]
        saved = await asyncio.to_thread(store.save_mvp3_evaluation, normalized, evaluation)
    except ValueError as exc:
        return JSONResponse({"error": str(exc)}, status_code=400)
    except Exception as exc:
        return JSONResponse({"error": str(exc)[:500]}, status_code=502)
    if not saved:
        return JSONResponse({"error": "The analysis run changed before MVP3 results could be saved."}, status_code=409)
    refreshed = await asyncio.to_thread(store.get_argumentation, normalized)
    return {"success": True, "mvp3": (refreshed or {}).get("analysis_payload", {}).get("mvp3", saved)}


@app.post("/api/analysis/rubric-review/{doi:path}")
async def review_mvp3_rubric(doi: str, request: Request):
    normalized = _analysis_paper_id(doi)
    if not normalized:
        return JSONResponse({"error": "Invalid DOI."}, status_code=400)
    body = await request.json()
    score = body.get("score")
    try:
        accepted = await asyncio.to_thread(get_store().save_rubric_review, normalized,
            str(body.get("argument_id") or ""), str(body.get("dimension") or ""), score,
            str(body.get("reviewer") or ""), str(body.get("rationale") or ""))
    except ValueError as exc:
        return JSONResponse({"error": str(exc)}, status_code=400)
    if not accepted:
        return JSONResponse({"error": "The selected argument is not part of this analysis."}, status_code=404)
    refreshed = await asyncio.to_thread(get_store().get_argumentation, normalized)
    return {"success": True, "mvp3": (refreshed or {}).get("analysis_payload", {}).get("mvp3", {})}


@app.post("/api/analysis/citation-review/{doi:path}")
async def review_mvp3_citation(doi: str, request: Request):
    normalized = _analysis_paper_id(doi)
    if not normalized:
        return JSONResponse({"error": "Invalid DOI."}, status_code=400)
    body = await request.json()
    try:
        accepted = await asyncio.to_thread(get_store().save_citation_review, normalized,
            str(body.get("citation_id") or ""), str(body.get("status") or ""),
            str(body.get("reviewer") or ""), str(body.get("rationale") or ""))
    except ValueError as exc:
        return JSONResponse({"error": str(exc)}, status_code=400)
    if not accepted:
        return JSONResponse({"error": "The selected citation verification is not part of this analysis."}, status_code=404)
    refreshed = await asyncio.to_thread(get_store().get_argumentation, normalized)
    return {"success": True, "mvp3": (refreshed or {}).get("analysis_payload", {}).get("mvp3", {})}


@app.get("/api/analysis/export/{doi:path}")
async def export_argumentation(doi: str):
    normalized = _analysis_paper_id(doi)
    if not normalized:
        return JSONResponse({"error": "Invalid DOI."}, status_code=400)
    run = await asyncio.to_thread(get_store().get_argumentation, normalized)
    if not run:
        return JSONResponse({"error": "No saved AIF graph is available."}, status_code=404)
    graph = run["graph"]
    nodes = [{"nodeID": node["id"], "type": node["node_type"], "text": node.get("text"),
              "metadata": node.get("metadata", {})} for node in graph["nodes"]]
    edges = [{"edgeID": edge["id"], "fromID": edge["source_node_id"], "toID": edge["target_node_id"]}
             for edge in graph["edges"]]
    return {"format": "AIF-compatible internal graph JSON", "run_id": run["id"],
            "version": graph["version"], "schema_version": graph.get("schema_version", 1),
            "provenance": {"provider": run.get("provider"),
            "model": run.get("model"), "prompt_versions": run.get("prompt_versions")},
            "validation": graph.get("validation", run.get("validation", {})),
            "argumentationFramework": graph.get("semantics", {}),
            "mvp3Evaluation": run.get("analysis_payload", {}).get("mvp3"),
            "AIF": {"nodes": nodes, "edges": edges}}


@app.post("/api/analysis/cross-paper")
async def analyze_cross_paper(request: Request):
    body = await request.json()
    provider = str(body.get("provider") or settings.AI_DEFAULT_PROVIDER or "ollama").strip().lower()
    if provider not in {"ollama", "gemini"}:
        return JSONResponse({"error": "Invalid AI provider."}, status_code=400)
    if provider == "gemini" and not settings.GEMINI_API_KEY:
        return JSONResponse({"error": "GEMINI_API_KEY is not configured in .env."}, status_code=400)
    store = get_store()
    propositions = await asyncio.to_thread(store.approved_propositions_for_synthesis)
    if len({item["doi"] for item in propositions}) < 2:
        return JSONResponse({"error": "At least two papers must have approved, source-quoted propositions."}, status_code=400)
    from ai_analysis import PROMPT_VERSIONS, analyze_cross_paper_relationships
    batch_id = __import__("uuid").uuid4().hex
    await asyncio.to_thread(store.create_cross_paper_batch, batch_id, provider,
                            PROMPT_VERSIONS["cross_paper_relationship_analysis"])
    try:
        relationships, model = await asyncio.to_thread(analyze_cross_paper_relationships, propositions, provider)
        await asyncio.to_thread(store.complete_cross_paper_batch, batch_id, model, relationships)
    except Exception as exc:
        await asyncio.to_thread(store.fail_cross_paper_batch, batch_id, str(exc))
        return JSONResponse({"error": str(exc)[:500], "batch_id": batch_id}, status_code=502)
    return {"batch_id": batch_id, "candidate_count": len(relationships), "status": "DONE",
            "human_review_required": True, "included_studies_filtered": False}


@app.get("/api/analysis/cross-paper")
async def list_cross_paper_relationships():
    return await asyncio.to_thread(get_store().list_cross_paper_relationships)


@app.post("/api/analysis/cross-paper/{relationship_id}/review")
async def review_cross_paper_relationship(relationship_id: str, request: Request):
    body = await request.json()
    try:
        accepted = await asyncio.to_thread(get_store().review_cross_paper_relationship, relationship_id,
                                           str(body.get("decision") or ""), str(body.get("note") or ""))
    except ValueError as exc:
        return JSONResponse({"error": str(exc)}, status_code=400)
    if not accepted:
        return JSONResponse({"error": "Cross-paper relationship not found."}, status_code=404)
    return {"success": True}


@app.get("/api/analysis/review-graph")
async def review_argument_graph():
    store = get_store()
    paper_graphs = await asyncio.to_thread(store.approved_argumentation_graphs)
    cross = await asyncio.to_thread(store.list_cross_paper_relationships)
    propositions = [item for graph in paper_graphs for item in graph["propositions"]]
    by_id = {item["id"]: item for item in propositions}
    nodes, edges, semantic_links = [], [], []
    for paper in paper_graphs:
        for node in paper["graph"]["nodes"]:
            proposition = by_id.get(node.get("proposition_id"), {})
            nodes.append({"nodeID": node["id"], "type": node["node_type"], "text": node.get("text"),
                "metadata": {**node.get("metadata", {}), "paperId": paper["doi"],
                    "propositionType": proposition.get("proposition_type"),
                    "roles": proposition.get("argumentative_roles", []),
                    "sourceQuote": proposition.get("source_quote"),
                    "sourceOffsets": proposition.get("source_offsets"),
                    "isInferred": proposition.get("is_inferred", False)}})
        edges.extend({"edgeID": edge["id"], "fromID": edge["source_node_id"], "toID": edge["target_node_id"]}
                     for edge in paper["graph"]["edges"])
    known_node_ids = {node["nodeID"] for node in nodes}
    approved_links = [item for item in cross["relationships"] if item["review_status"] == "approved" and not item["stale"]]
    for item in approved_links:
        source, target = by_id.get(item["source_proposition_id"]), by_id.get(item["target_proposition_id"])
        if not source or not target or "i:" + source["id"] not in known_node_ids or "i:" + target["id"] not in known_node_ids:
            continue
        if item["relationship"] == "supports":
            ra_id = "ra:cross:" + item["id"]
            nodes.append({"nodeID": ra_id, "type": "RA", "text": "Cross-paper support",
                          "relation_id": item["id"],
                          "metadata": {"relationshipId": item["id"], "explanation": item["explanation"],
                                       "sourcePaperId": item["source_doi"], "targetPaperId": item["target_doi"],
                                       "sourceQuote": item["source_quote"], "targetQuote": item["target_quote"],
                                       "confidence": item["confidence"], "provenance": item["provenance"],
                                       "premise_proposition_ids": [source["id"]],
                                       "conclusion_proposition_id": target["id"],
                                       "source_evidence": [{"proposition_id": source["id"], "text": source["text"],
                                           "source_quote": item["source_quote"], "review_status": "approved",
                                           "provenance": item["provenance"]}],
                                       "supporting_quote": item["source_quote"], "scheme_id": "cross-paper-support",
                                       "review_status": "approved", "reviewStatus": "approved"}})
            edges.extend([{"edgeID": "e:cross:source:" + item["id"], "fromID": "i:" + source["id"], "toID": ra_id},
                          {"edgeID": "e:cross:target:" + item["id"], "fromID": ra_id, "toID": "i:" + target["id"]}])
        elif item["relationship"] == "contradicts":
            ca_id = "ca:cross:" + item["id"]
            nodes.append({"nodeID": ca_id, "type": "CA", "text": "Cross-paper rebuttal",
                          "relation_id": item["id"],
                          "metadata": {"relationshipId": item["id"], "explanation": item["explanation"],
                                       "sourcePaperId": item["source_doi"], "targetPaperId": item["target_doi"],
                                       "sourceQuote": item["source_quote"], "targetQuote": item["target_quote"],
                                       "confidence": item["confidence"], "provenance": item["provenance"],
                                       "attack_type": "rebut", "premise_proposition_ids": [source["id"]],
                                       "target_proposition_id": target["id"],
                                       "source_evidence": [{"proposition_id": source["id"], "text": source["text"],
                                           "source_quote": item["source_quote"], "review_status": "approved",
                                           "provenance": item["provenance"]}],
                                       "supporting_quote": item["source_quote"],
                                       "review_status": "approved", "reviewStatus": "approved"}})
            edges.extend([{"edgeID": "e:cross:source:" + item["id"], "fromID": "i:" + source["id"], "toID": ca_id},
                          {"edgeID": "e:cross:target:" + item["id"], "fromID": ca_id, "toID": "i:" + target["id"]}])
        else:
            semantic_links.append({"id": item["id"], "sourceNodeId": "i:" + source["id"],
                "targetNodeId": "i:" + target["id"], "relationship": item["relationship"],
                "explanation": item["explanation"], "sourceQuote": item["source_quote"],
                "targetQuote": item["target_quote"], "reviewStatus": "approved"})
    from ai_analysis import evaluate_aif_semantics, validate_aif_graph
    internal_nodes = []
    for node in nodes:
        metadata = node.get("metadata", {})
        proposition = by_id.get(node["nodeID"][2:]) if node["nodeID"].startswith("i:") else None
        if proposition:
            offsets = proposition.get("source_offsets") or {}
            source_quote = proposition.get("source_quote")
            metadata["source_reference"] = {"proposition_id": proposition["id"],
                "section_id": proposition.get("section_id"), "page": proposition.get("source_page"),
                "start_offset": offsets.get("start") if isinstance(offsets, dict) else None,
                "end_offset": offsets.get("end") if isinstance(offsets, dict) else None,
                "quote": source_quote,
                "location_complete": bool(source_quote and isinstance(offsets, dict) and
                    offsets.get("start") is not None and offsets.get("end") is not None)}
        internal_nodes.append({"id": node["nodeID"], "node_type": node["type"],
                               "relation_id": node.get("relation_id"), "metadata": metadata})
    internal_graph = {"nodes": internal_nodes,
                      "edges": [{"id": edge["edgeID"], "source_node_id": edge["fromID"],
                                 "target_node_id": edge["toID"]} for edge in edges]}
    validation = validate_aif_graph(internal_graph)
    semantics = evaluate_aif_semantics(internal_graph)
    for node, internal in zip(nodes, internal_nodes):
        node["metadata"] = internal["metadata"]
    return {"format": "AIF-compatible internal review graph JSON", "version": {
            "paperAnalysisRuns": sorted({graph["run_id"] for graph in paper_graphs}),
            "crossPaperBatch": (cross.get("batch") or {}).get("id")},
        "includedStudyFilter": False,
        "validation": validation, "argumentationFramework": semantics,
        "AIF": {"nodes": nodes, "edges": edges}, "semanticLinks": semantic_links}


@app.post("/api/analysis/enqueue")
async def enqueue_analysis(request: Request):
    body = await request.json()
    provider = str(body.get("provider") or settings.AI_DEFAULT_PROVIDER or "ollama").strip().lower()
    if provider not in {"ollama", "gemini"}:
        return JSONResponse({"error": "Invalid AI provider."}, status_code=400)
    if provider == "gemini" and not settings.GEMINI_API_KEY:
        return JSONResponse({"error": "GEMINI_API_KEY is not configured in .env."}, status_code=400)
    requested = body.get("dois") or []
    if not isinstance(requested, list):
        return JSONResponse({"error": "dois must be a list."}, status_code=400)
    store = get_store()
    if requested:
        normalized_dois = {_analysis_paper_id(value) for value in requested}
        normalized_dois.discard("")
        records = [await asyncio.to_thread(store.get, doi) for doi in normalized_dois]
    else:
        records = await asyncio.to_thread(store.list, 2000)
    queued = []
    skipped = []
    for record in records:
        if not record or record.get("status") != "DOWNLOADED" or not _valid_analysis_source(record.get("file_path")):
            continue
        doi = record["doi"]
        accepted = await asyncio.to_thread(
            store.try_queue_analysis, doi, provider, allow_done=bool(requested)
        )
        if not accepted:
            skipped.append(doi)
            continue
        _ANALYSIS_QUEUE.put_nowait((doi, provider))
        queued.append(doi)
    return {"queued": queued, "skipped": skipped, "total": len(queued)}

@app.get("/api/health")
async def health():
    get_store()
    return {"status": "ok"}


@app.get("/api/saffron/health")
async def saffron_health():
    if not settings.SAFFRON_ENABLED:
        return {"enabled": False, **_SAFFRON_RUNTIME_STATE}
    try:
        from saffron_client import SaffronClient
        ready = await asyncio.to_thread(SaffronClient().health)
        if ready:
            return {"enabled": True, "status": "ready", "message": "SAFFRON service is ready."}
        return JSONResponse({"enabled": True, "status": "unavailable",
                             "message": _SAFFRON_RUNTIME_STATE.get("message") or "SAFFRON is not ready."}, status_code=503)
    except Exception as exc:
        return JSONResponse({"enabled": True, "status": "unavailable", "message": str(exc)[:500]}, status_code=503)


@app.post("/api/focus-verification")
async def focus_verification():
    focused = await browser_manager.run(browser_manager.focus_verification_page)
    if not focused and not browser_worker.request_focus_verification():
        return JSONResponse({"error": "Không có tab xác minh đang mở."}, status_code=409)
    return {"success": True}


@app.get("/api/papers")
async def paper_status(doi: Optional[str] = None):
    if doi is not None:
        normalized = _analysis_paper_id(doi)
        if not normalized:
            return JSONResponse({"error": "INVALID_DOI"}, status_code=400)
        record = await asyncio.to_thread(get_store().get, normalized)
        if record and record["status"] == "DOWNLOADED" and not _valid_analysis_source(record.get("file_path")):
            get_store().update(normalized, "INVALID_PDF", message="PDF đã bị xóa hoặc không còn đầy đủ.")
            record = get_store().get(normalized)
        return {"paper": record}
    papers = await asyncio.to_thread(get_store().list, 2000)
    for record in papers:
        if record["status"] == "DOWNLOADED" and not _valid_analysis_source(record.get("file_path")):
            get_store().update(record["doi"], "INVALID_PDF", message="PDF đã bị xóa hoặc không còn đầy đủ.")
            record["status"] = "INVALID_PDF"
    return {"papers": papers}

@app.get("/api/downloaded-papers")
async def downloaded_papers_endpoint():
    from pathlib import Path
    import json
    store = get_store()
    records = await asyncio.to_thread(store.list, 2000)
    analyses = {row["doi"]: row for row in await asyncio.to_thread(store.list_analyses)}
    downloaded = []
    for r in records:
        if r["status"] == "DOWNLOADED" and r.get("file_path"):
            p = Path(r["file_path"])
            if p.exists() and valid_pdf_file(p):
                try:
                    size_bytes = p.stat().st_size
                except OSError:
                    size_bytes = 0
                size_formatted = f"{size_bytes / (1024 * 1024):.2f} MB" if size_bytes >= 1024*1024 else f"{size_bytes / 1024:.1f} KB"
                meta = {}
                try:
                    meta = json.loads(r.get("metadata") or "{}")
                except Exception:
                    pass
                analysis = analyses.get(r["doi"], {})
                openalex_classification = meta.get("openalex_classification")
                if analysis.get("draft"):
                    try:
                        analysis_draft = json.loads(analysis["draft"])
                        if isinstance(analysis_draft, dict):
                            openalex_classification = (analysis_draft.get("openalex_classification")
                                                       or openalex_classification)
                    except (TypeError, ValueError):
                        pass
                downloaded.append({
                    "doi": r["doi"],
                    "filename": r["filename"],
                    "file_path": r["file_path"],
                    "file_size": size_bytes,
                    "file_size_formatted": size_formatted,
                    "title": meta.get("title") or r["doi"],
                    "authors": meta.get("authors") or "",
                    "journal": meta.get("journal") or r.get("provider") or "",
                    "year": meta.get("year") or "",
                    "source": r.get("source") or "Unknown",
                    "provider": r.get("provider") or "Generic",
                    "resolved_url": r.get("resolved_url") or "",
                    "updated_at": r.get("updated_at") or "",
                    "last_uploaded_project": meta.get("last_uploaded_project") or "",
                    "uploaded_at": meta.get("uploaded_at") or "",
                    "analysis_status": analysis.get("status", "NOT_STARTED"),
                    "openalex_classification": openalex_classification or {
                        "schema_version": "openalex-topics.v1", "status": "NOT_ANALYZED",
                    },
                })
    return {"papers": downloaded, "total": len(downloaded)}


def _openalex_artifact_is_current(artifact):
    if not isinstance(artifact, dict) or artifact.get("status") != "MATCHED":
        return False
    provenance = artifact.get("provenance") or {}
    topics = provenance.get("topics") if isinstance(provenance, dict) else None
    classification = artifact.get("classification")
    has_hierarchy_ids = isinstance(classification, dict) and all(
        isinstance(classification.get(key), list) and classification[key]
        for key in ("topicIds", "subfieldIds", "fieldIds", "domainIds")
    )
    return has_hierarchy_ids and bool(topics) and all(
        isinstance(topic, dict) and topic.get("id") and topic.get("subfieldId")
        and topic.get("fieldId") and topic.get("domainId")
        for topic in topics
    )


def _run_openalex_backfill(items):
    from automatic_sources import fetch_openalex_classification

    store = get_store()
    try:
        for item in items:
            doi = item["doi"]
            with _OPENALEX_BACKFILL_LOCK:
                _OPENALEX_BACKFILL_STATE["current_doi"] = doi
            try:
                fields = fetch_openalex_classification(doi, item["openAlexId"])
                artifact = _openalex_classification_artifact(fields) or {
                    "schema_version": "openalex-topics.v1",
                    "status": (fields or {}).get("status", "UNAVAILABLE"),
                    "provenance": (fields or {}).get("classificationProvenance") or {
                        "source": "OPENALEX_TOPICS",
                    },
                }
                store.update_openalex_classification(doi, artifact)
                state_key = "matched" if artifact["status"] == "MATCHED" else (
                    "unavailable" if artifact["status"] == "UNAVAILABLE" else "not_found"
                )
            except Exception as exc:
                print(f"[OPENALEX] Backfill failed for {doi}: {exc}")
                artifact = {"schema_version": "openalex-topics.v1", "status": "UNAVAILABLE",
                            "provenance": {"source": "OPENALEX_TOPICS"}}
                store.update_openalex_classification(doi, artifact)
                state_key = "unavailable"
            with _OPENALEX_BACKFILL_LOCK:
                _OPENALEX_BACKFILL_STATE["processed"] += 1
                _OPENALEX_BACKFILL_STATE[state_key] += 1
    except Exception as exc:
        print(f"[OPENALEX] Backfill job failed: {exc}")
        with _OPENALEX_BACKFILL_LOCK:
            _OPENALEX_BACKFILL_STATE["status"] = "failed"
            _OPENALEX_BACKFILL_STATE["message"] = "OpenAlex update stopped unexpectedly. Check the Fetcher log."
    finally:
        with _OPENALEX_BACKFILL_LOCK:
            if _OPENALEX_BACKFILL_STATE["status"] == "running":
                _OPENALEX_BACKFILL_STATE["status"] = "completed"
            _OPENALEX_BACKFILL_STATE["current_doi"] = ""


@app.post("/api/openalex/backfill")
async def start_openalex_backfill():
    store = get_store()
    records = await asyncio.to_thread(store.list, 2000)
    analyses = {row["doi"]: row for row in await asyncio.to_thread(store.list_analyses)}
    items = []
    for record in records:
        if record.get("status") != "DOWNLOADED" or not valid_pdf_file(record.get("file_path") or ""):
            continue
        doi = extract_doi(record.get("doi") or "")
        if not doi:
            continue
        try:
            metadata = json.loads(record.get("metadata") or "{}")
        except (TypeError, ValueError):
            metadata = {}
        if not isinstance(metadata, dict):
            metadata = {}
        analysis = analyses.get(record["doi"], {})
        artifact = metadata.get("openalex_classification")
        if analysis.get("draft"):
            try:
                draft = json.loads(analysis["draft"])
                if isinstance(draft, dict):
                    artifact = draft.get("openalex_classification") or artifact
            except (TypeError, ValueError):
                pass
        if not _openalex_artifact_is_current(artifact):
            items.append({"doi": doi, "openAlexId": metadata.get("openAlexId") or ""})

    with _OPENALEX_BACKFILL_LOCK:
        if _OPENALEX_BACKFILL_STATE.get("status") == "running":
            return JSONResponse({"error": "An OpenAlex update is already running.",
                                 "state": dict(_OPENALEX_BACKFILL_STATE)}, status_code=409)
        _OPENALEX_BACKFILL_STATE.update({
            "status": "running" if items else "completed", "total": len(items), "processed": 0,
            "matched": 0, "not_found": 0, "unavailable": 0, "current_doi": "",
            "message": "" if items else "All downloaded papers already have current OpenAlex topics.",
        })
        if items:
            worker = threading.Thread(target=_run_openalex_backfill, args=(items,), daemon=True,
                                      name="openalex-backfill")
            worker.start()
        state = dict(_OPENALEX_BACKFILL_STATE)
    return JSONResponse({"state": state}, status_code=202 if items else 200)


@app.get("/api/openalex/backfill")
async def openalex_backfill_status():
    with _OPENALEX_BACKFILL_LOCK:
        return {"state": dict(_OPENALEX_BACKFILL_STATE)}

@app.get("/api/download-file/{filename}")
async def get_downloaded_file(filename: str):
    from pathlib import Path
    try:
        target_path = download_path(settings.DOWNLOAD_FOLDER, filename, ".pdf")
    except ValueError as error:
        return JSONResponse({"success": False, "error": str(error)}, status_code=400)
    if not target_path.exists() or not valid_pdf_file(target_path):
        return JSONResponse({"success": False, "error": "File PDF không tồn tại hoặc không hợp lệ."}, status_code=404)
    return FileResponse(
        path=str(target_path),
        filename=filename,
        media_type="application/pdf"
    )

@app.post("/api/process")
async def process_dois(dois: str = Form(None), file: UploadFile = File(None)):
    results = []
    items_to_process = []
    
    if file:
        content = await file.read()
        try:
            if (file.filename or '').lower().endswith('.csv'):
                df = pd.read_csv(io.BytesIO(content))
            elif (file.filename or '').lower().endswith(('.xls', '.xlsx')):
                df = pd.read_excel(io.BytesIO(content))
            else:
                return JSONResponse({"error": "Định dạng file không hỗ trợ. Vui lòng dùng file .xlsx, .xls hoặc .csv."})
            
            # Identify columns
            doi_col = None
            filename_col = None
            title_col = None
            oa_col = None
            journal_col = None
            author_col = None
            year_col = None
            
            for col in df.columns:
                col_str = str(col).lower()
                if doi_col is None and ('doi' in col_str or 'link doi' in col_str):
                    doi_col = col
                elif filename_col is None and ('tên file' in col_str or 'filename' in col_str or 'file_name' in col_str):
                    filename_col = col
                elif title_col is None and ('title' in col_str or 'tiêu đề' in col_str or 'tên bài' in col_str):
                    title_col = col
                elif oa_col is None and ('link oa' in col_str or 'oa' in col_str or 'open access' in col_str):
                    oa_col = col
                elif journal_col is None and any(k in col_str for k in ['journal', 'tạp chí', 'nguồn', 'source', 'publisher', 'venue']):
                    journal_col = col
                elif author_col is None and any(k in col_str for k in ['author', 'tác giả', 'authors']):
                    author_col = col
                elif year_col is None and any(k in col_str for k in ['year', 'năm', 'pub_year', 'date']):
                    year_col = col

            if doi_col is None:
                for col in df.columns:
                    sample = df[col].dropna().astype(str).head(10).tolist()
                    if any('10.' in s for s in sample):
                        doi_col = col
                        break

            if doi_col is None:
                return JSONResponse({"error": "Không tìm thấy cột chứa mã DOI trong file Excel/CSV."})

            for _, row in df.iterrows():
                raw_doi = str(row[doi_col]) if pd.notna(row[doi_col]) else ""
                custom_name = str(row[filename_col]) if filename_col and pd.notna(row[filename_col]) else ""
                custom_title = str(row[title_col]) if title_col and pd.notna(row[title_col]) else ""
                existing_oa = str(row[oa_col]) if oa_col and pd.notna(row[oa_col]) else ""
                custom_journal = str(row[journal_col]) if journal_col and pd.notna(row[journal_col]) else ""
                custom_author = str(row[author_col]) if author_col and pd.notna(row[author_col]) else ""
                custom_year = str(row[year_col]) if year_col and pd.notna(row[year_col]) else ""

                if raw_doi.strip() and raw_doi.strip().lower() != 'nan':
                    items_to_process.append({
                        "raw": raw_doi,
                        "custom_name": custom_name,
                        "custom_title": custom_title,
                        "existing_oa": existing_oa,
                        "custom_journal": custom_journal,
                        "custom_author": custom_author,
                        "custom_year": custom_year
                    })
        except Exception as e:
            return JSONResponse({"error": f"Lỗi đọc file: {str(e)}"})
    elif dois:
        for line in dois.split('\n'):
            line = line.strip()
            if line:
                items_to_process.append({
                    "raw": line,
                    "custom_name": "",
                    "custom_title": "",
                    "existing_oa": ""
                })
    
    if not items_to_process:
        return JSONResponse({"error": "Không có danh sách DOI nào được cung cấp."})

    seen = set()
    unique = []
    duplicate_count = 0
    for item in items_to_process:
        doi = extract_doi(item["raw"])
        if doi and doi in seen:
            duplicate_count += 1
            continue
        if doi:
            seen.add(doi)
        unique.append(item)
    items_to_process = unique

    async def stream_results():
        import json
        total = len(items_to_process)
        yield json.dumps({"type": "start", "total": total, "duplicates": duplicate_count, "concurrency": 6}) + "\n"
        results = [None] * total
        semaphore = asyncio.Semaphore(6)

        def process_one_item(item):
            raw_text = item["raw"]
            doi = extract_doi(raw_text)
            if not doi or not doi.startswith("10."):
                import hashlib
                get_store().update("invalid:" + hashlib.sha256(raw_text.encode()).hexdigest(), "INVALID_DOI",
                                   message="Invalid DOI.")
                return {"original": raw_text, "custom_name": item.get("custom_name") or "paper.pdf",
                        "title": item.get("custom_title") or raw_text, "status": "INVALID_DOI",
                        "oa_link": None, "vnu_link": None}

            oa_link = oa_landing = source = None
            status = "Paywalled"
            if item.get("existing_oa") and item["existing_oa"].startswith("http"):
                oa_link = item["existing_oa"]
                title = item["custom_title"] or "T\u00e0i li\u1ec7u Open Access"
                source, status = "Excel Data", "Open Access"
            else:
                fulltext_info = find_paper_fulltext(doi)
                title = item["custom_title"] or fulltext_info.get("title") or "Unknown Title"
                oa_link = fulltext_info.get("pdf_url")
                oa_landing = fulltext_info.get("landing_url")
                source = fulltext_info.get("source")
                status = fulltext_info.get("status") or ("Open Access" if oa_link else "Paywalled")

            resolution = resolve_doi(doi)
            saved = get_store().downloaded(doi)
            if saved:
                custom_name = saved["filename"]
            else:
                custom_name = generate_standardized_filename(doi, item.get("custom_name"), title)

            record = get_store().get(doi) or {}
            prior_status = record.get("status", "PENDING")
            if saved:
                persistent_status = "DOWNLOADED"
            elif prior_status in _KEPT_FAILURE_STATES:
                # A re-scan must not erase why the last download attempt failed.
                persistent_status = prior_status
            else:
                persistent_status = "OPEN_ACCESS" if oa_link else prior_status
            get_store().update(doi, persistent_status, filename=custom_name,
                               metadata={"title": title, "authors": item.get("custom_author") or "",
                                         "journal": item.get("custom_journal") or source or "", "year": item.get("custom_year") or ""})

            return {
                "original": raw_text, "doi": doi, "custom_name": custom_name, "title": title,
                "journal": item.get("custom_journal") or source or "",
                "authors": item.get("custom_author") or "", "year": item.get("custom_year") or "",
                "status": status, "state": (get_store().get(doi) or {}).get("status", "PENDING"), "already_exists": bool(saved),
                "message": None if saved else record.get("message"),
                "download_method": record.get("source") if saved else None,
                "resolved_url": resolution.get("resolved_url"), "provider": resolution.get("provider"),
                "oa_link": oa_link, "oa_landing": oa_landing, "source": source,
                "vnu_link": institutional_url(settings.VNU_OPENATHENS_BASE_URL, doi)
            }

        async def process_index(index, item):
            async with semaphore:
                try:
                    result = await asyncio.to_thread(process_one_item, item)
                except Exception as exc:
                    result = {"original": item["raw"], "doi": extract_doi(item["raw"]),
                              "custom_name": item.get("custom_name") or "paper.pdf",
                              "title": item.get("custom_title") or item["raw"],
                              "status": "FAILED", "message": type(exc).__name__, "oa_link": None, "vnu_link": None}
                return index, result

        tasks = [asyncio.create_task(process_index(i, item)) for i, item in enumerate(items_to_process)]
        try:
            completed = 0
            for task in asyncio.as_completed(tasks):
                index, result = await task
                results[index] = result
                completed += 1
                yield json.dumps({"type": "progress", "completed": completed, "total": total,
                                  "index": index, "result": result}, ensure_ascii=False) + "\n"
            yield json.dumps({"type": "done", "results": results}, ensure_ascii=False) + "\n"
        finally:
            for task in tasks:
                if not task.done():
                    task.cancel()

    return StreamingResponse(stream_results(), media_type="application/x-ndjson",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

@app.post("/api/download")
async def download_file(url: str = Form(...), filename: str = Form(""), doi: str = Form("")):
    doi = extract_doi(doi)
    if not doi:
        return JSONResponse({"success": False, "error": "Cần DOI hợp lệ để tải và theo dõi đúng bài."}, status_code=400)
    if not filename:
        filename = generate_standardized_filename(doi)
    try:
        target_path = download_path(settings.DOWNLOAD_FOLDER, filename)
    except ValueError as error:
        return JSONResponse({"success": False, "error": str(error)}, status_code=400)
    success, msg, method = await auto_download_paper(doi, target_path.name, oa_url=url)
    if success:
        record = get_store().get(doi) or {}
        return {"success": True, "path": record.get("file_path", str(target_path)), "message": msg, "method": method}
    return JSONResponse({"success": False, "error": msg})

_DOWNLOAD_JOBS = set()
_KEPT_FAILURE_STATES = {"PURCHASE_REQUIRED", "NO_ACCESS", "FAILED", "CAPTCHA_REQUIRED", "MFA_REQUIRED", "LOGIN_REQUIRED", "INVALID_PDF"}


@app.post("/api/download-all")
async def download_all(request: Request):
    try:
        payload = await request.json()
        items = payload.get("items") if isinstance(payload, dict) else None
        if not isinstance(items, list) or not items or len(items) > 2000 or any(not isinstance(item, dict) for item in items):
            raise ValueError("Invalid items")
        seen = set()
        names = set()
        for item in items:
            doi = extract_doi(item.get("doi"))
            filename = safe_filename(item.get("filename") or generate_standardized_filename(doi, "", item.get("title", "")))
            if not doi or doi in seen or filename.lower() in names:
                raise ValueError("Invalid DOI, duplicate DOI or duplicate filename")
            seen.add(doi)
            names.add(filename.lower())
            item.update(doi=doi, filename=filename)
    except (ValueError, TypeError):
        return JSONResponse({"error": "Danh sach DOI/ten file khong hop le hoac bi trung."}, status_code=400)

    async def stream_downloads():
        loop = asyncio.get_running_loop()
        events = asyncio.Queue()
        total = len(items)
        oa_total = total
        oa_done = vnu_done = vnu_total = completed = 0
        success_count = fail_count = 0

        async def download_one(index, item):
            lane = "oa"

            def send(event):
                loop.call_soon_threadsafe(events.put_nowait, event)

            def status(value):
                nonlocal lane
                if value == "public_sources_finished" and lane == "oa":
                    lane = "vnu"
                    send({"type": "lane_done", "lane": "oa"})
                    send({"type": "lane_add", "lane": "vnu"})
                elif value == "public_fallback_started" and lane == "vnu":
                    lane = "oa"
                    send({"type": "lane_done", "lane": "vnu"})
                    send({"type": "lane_add", "lane": "oa"})
                send({"type": "item_progress", "index": index, "lane": lane, "percent": None, "status": value})

            try:
                success, message, method = await auto_download_paper(
                    item["doi"], item["filename"], str(item.get("title") or ""),
                    progress_callback=lambda percent: send({"type": "item_progress", "index": index, "lane": lane, "percent": percent}),
                    status_callback=status, oa_url=item.get("oa_link"))
                record = get_store().get(item["doi"]) or {}
                result = {"success": success, "filename": record.get("filename") or item["filename"],
                          "method": method, "message": message, "state": record.get("status"),
                          "open_url": record.get("resolved_url") or _publisher_url_from_message(message) or "https://doi.org/" + item["doi"]}
            except Exception as error:
                result = {"success": False, "filename": item["filename"], "message": type(error).__name__, "state": "FAILED"}
            send({"type": "lane_done", "lane": lane})
            send({"type": "progress", "index": index, "result": result})

        yield json.dumps({"type": "start", "total": total, "oa_total": total, "vnu_total": 0}) + "\n"
        tasks = [asyncio.create_task(download_one(index, item)) for index, item in enumerate(items)]
        # A disconnected tab does not cancel an authenticated file write.
        for task in tasks:
            _DOWNLOAD_JOBS.add(task)
            task.add_done_callback(_DOWNLOAD_JOBS.discard)
        while completed < total:
            try:
                event = await asyncio.wait_for(events.get(), timeout=10)
            except asyncio.TimeoutError:
                yield json.dumps({"type": "heartbeat", "completed": completed, "total": total}) + "\n"
                continue
            if event["type"] == "lane_add":
                if event["lane"] == "oa":
                    oa_total += 1
                else:
                    vnu_total += 1
            elif event["type"] == "lane_done":
                if event["lane"] == "oa":
                    oa_done += 1
                else:
                    vnu_done += 1
            elif event["type"] == "progress":
                completed += 1
                if event["result"]["success"]:
                    success_count += 1
                else:
                    fail_count += 1
            event.update(completed=completed, total=total, oa_done=oa_done, oa_total=oa_total,
                         vnu_done=vnu_done, vnu_total=vnu_total, success_count=success_count, fail_count=fail_count)
            yield json.dumps(event, ensure_ascii=False) + "\n"
        yield json.dumps({"type": "done", "total": total, "success_count": success_count, "fail_count": fail_count}) + "\n"

    return StreamingResponse(stream_downloads(), media_type="application/x-ndjson",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.post("/api/sync-recent-download")
async def sync_recent_download(filename: str = Form(...), source_filename: str = Form(...), doi: str = Form(...)):
    """Explicit import only: never assign the latest Windows download to a DOI."""
    from pathlib import Path
    doi = extract_doi(doi)
    if not doi:
        return JSONResponse({"success": False, "error": "INVALID_DOI"}, status_code=400)
    try:
        source = download_path(Path.home() / "Downloads", source_filename)
        target = download_path(settings.DOWNLOAD_FOLDER, filename)
        success, message = await asyncio.to_thread(import_verified_pdf, doi, source, target)
        return JSONResponse({"success": success, "filename": target.name, "message": message}, status_code=200 if success else 409)
    except (ValueError, OSError) as error:
        return JSONResponse({"success": False, "error": type(error).__name__}, status_code=400)

@app.post("/api/auto-vnu")
async def auto_vnu_endpoint(doi: str = Form(...), filename: str = Form(...), title: str = Form("")):
    doi = extract_doi(doi)
    if not doi.startswith("10."):
        return JSONResponse({"success": False, "error": "Invalid DOI."}, status_code=400)
    try:
        if filename:
            filename = safe_filename(filename)
        else:
            filename = generate_standardized_filename(doi, "", title)
    except ValueError as error:
        return JSONResponse({"success": False, "error": str(error)}, status_code=400)
    success, msg, method = await auto_download_paper(doi, filename, title)
    if success:
        return {"success": True, "message": msg, "method": method, "filename": (get_store().get(doi) or {}).get("filename", filename)}
    record = get_store().get(doi) or {}
    return JSONResponse({"success": False, "error": msg, "state": record.get("status"), "open_url": record.get("resolved_url") or _publisher_url_from_message(msg)})


@app.get("/api/elsevier-status")
async def elsevier_status():
    settings.refresh_api_credentials()
    return {"api_key_configured": bool(settings.ELSEVIER_API_KEY),
            "institution_token_configured": bool(settings.ELSEVIER_INST_TOKEN),
            "automatic_download_enabled": False, "download_strategy": "institutional_browser",
            "manual_verification_enabled": settings.VNU_ALLOW_MANUAL_VERIFICATION}


@app.get("/api/elsevier-search")
async def elsevier_search(doi: str):
    return JSONResponse({"found": False, "message": "Đã ngừng dùng API Elsevier. Tải qua phiên đăng nhập VNU/OpenAthens."}, status_code=410)

@app.get("/api/open-folder")
async def open_download_folder():
    folder_str = str(settings.DOWNLOAD_FOLDER.resolve())
    if os.name == 'nt':
        os.startfile(folder_str)
    return {"success": True, "folder": folder_str}

@app.post("/api/export-ris")
async def export_ris_endpoint(request: Request):
    """Xuất file trích dẫn RIS (.ris) cho danh sách các bài báo."""
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"success": False, "error": "Dữ liệu JSON không hợp lệ."})

    items = data.get("items", []) if isinstance(data, dict) else []
    if not isinstance(items, list) or not items or any(not isinstance(item, dict) for item in items):
        return JSONResponse({"success": False, "error": "Không có bài báo nào để xuất RIS."})

    try:
        filename = safe_filename(data.get("filename", "slr_citations.ris"), ".ris")
    except ValueError as error:
        return JSONResponse({"success": False, "error": str(error)}, status_code=400)

    try:
        ris_content = await generate_combined_ris(items)
        if not ris_content.strip():
            return JSONResponse({"success": False, "error": "Không tạo được nội dung RIS nào."})

        # Lưu một bản sao vào thư mục downloads của project
        target_path = download_path(settings.DOWNLOAD_FOLDER, filename, ".ris")
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(ris_content)

        return {
            "success": True,
            "filename": filename,
            "content": ris_content,
            "count": len(items),
            "saved_path": str(target_path)
        }
    except Exception as e:
        return JSONResponse({"success": False, "error": f"Lỗi tạo file RIS: {str(e)}"})

@app.get("/api/download-ris")
async def download_ris_endpoint(filename: str = "slr_citations.ris"):
    try:
        target_path = download_path(settings.DOWNLOAD_FOLDER, filename, ".ris")
    except ValueError as error:
        return JSONResponse({"success": False, "error": str(error)}, status_code=400)
    if not target_path.exists():
        return JSONResponse({"success": False, "error": "File không tồn tại."})
    return FileResponse(
        path=str(target_path),
        filename=filename,
        media_type="application/x-research-info-systems"
    )


# ========================================================
# SLR SYSTEM INTEGRATION ENDPOINTS
# ========================================================

@app.get("/api/slr/config")
async def get_slr_config():
    settings.refresh_api_credentials()
    key = settings.SLR_API_KEY
    masked_key = f"{key[:4]}...{key[-4:]}" if len(key) > 8 else ("***" if key else "")
    return {
        "base_url": settings.SLR_API_BASE_URL,
        "has_api_key": bool(key),
        "api_key_masked": masked_key,
        "default_project_id": settings.SLR_DEFAULT_PROJECT_ID,
    }

@app.post("/api/slr/config")
async def update_slr_config(request: Request):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"success": False, "error": "Dữ liệu JSON không hợp lệ."}, status_code=400)
    
    base_url = str(data.get("base_url") or "").strip().rstrip("/")
    api_key = str(data.get("api_key") or "").strip()
    default_project_id = str(data.get("default_project_id") or "").strip()

    if base_url:
        settings.SLR_API_BASE_URL = base_url
    if "api_key" in data and api_key:
        settings.SLR_API_KEY = api_key
        settings.SLR_PUBLIC_API_KEY = api_key
        settings.SLR_REPOSITORY_API_KEY = api_key
    if "default_project_id" in data:
        settings.SLR_DEFAULT_PROJECT_ID = default_project_id

    # Persist to .env
    try:
        from config import ENV_PATH
        env_lines = []
        if ENV_PATH.exists():
            with open(ENV_PATH, "r", encoding="utf-8") as f:
                env_lines = f.readlines()
        
        updated_keys = set()
        new_lines = []
        for line in env_lines:
            if line.startswith("SLR_API_KEY="):
                new_lines.append(f"SLR_API_KEY={settings.SLR_API_KEY}\n")
                updated_keys.add("SLR_API_KEY")
            elif line.startswith("SLR_API_BASE_URL="):
                new_lines.append(f"SLR_API_BASE_URL={settings.SLR_API_BASE_URL}\n")
                updated_keys.add("SLR_API_BASE_URL")
            elif line.startswith("SLR_PUBLIC_API_KEY="):
                new_lines.append(f"SLR_PUBLIC_API_KEY={settings.SLR_PUBLIC_API_KEY}\n")
                updated_keys.add("SLR_PUBLIC_API_KEY")
            elif line.startswith("SLR_REPOSITORY_API_KEY="):
                new_lines.append(f"SLR_REPOSITORY_API_KEY={settings.SLR_REPOSITORY_API_KEY}\n")
                updated_keys.add("SLR_REPOSITORY_API_KEY")
            elif line.startswith("SLR_DEFAULT_PROJECT_ID="):
                new_lines.append(f"SLR_DEFAULT_PROJECT_ID={settings.SLR_DEFAULT_PROJECT_ID}\n")
                updated_keys.add("SLR_DEFAULT_PROJECT_ID")
            else:
                new_lines.append(line)
        
        if "SLR_API_KEY" not in updated_keys:
            new_lines.append(f"SLR_API_KEY={settings.SLR_API_KEY}\n")
        if "SLR_API_BASE_URL" not in updated_keys:
            new_lines.append(f"SLR_API_BASE_URL={settings.SLR_API_BASE_URL}\n")
        if "SLR_PUBLIC_API_KEY" not in updated_keys:
            new_lines.append(f"SLR_PUBLIC_API_KEY={settings.SLR_PUBLIC_API_KEY}\n")
        if "SLR_REPOSITORY_API_KEY" not in updated_keys:
            new_lines.append(f"SLR_REPOSITORY_API_KEY={settings.SLR_REPOSITORY_API_KEY}\n")
        if "SLR_DEFAULT_PROJECT_ID" not in updated_keys:
            new_lines.append(f"SLR_DEFAULT_PROJECT_ID={settings.SLR_DEFAULT_PROJECT_ID}\n")

        with open(ENV_PATH, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
    except Exception as e:
        print(f"[SLR CONFIG] Warning writing .env: {e}")

    return {
        "success": True,
        "message": "Đã lưu cấu hình kết nối SLR System thành công!",
        "config": {
            "base_url": settings.SLR_API_BASE_URL,
            "has_api_key": bool(settings.SLR_API_KEY),
            "default_project_id": settings.SLR_DEFAULT_PROJECT_ID,
            }
    }

@app.get("/api/slr/projects")
async def get_slr_projects():
    settings.refresh_api_credentials()
    base_url = settings.SLR_API_BASE_URL or "http://127.0.0.1:5000"
    api_key = settings.SLR_API_KEY
    if not api_key:
        return JSONResponse({
            "success": False,
            "error": "Chưa cấu hình SLR API key. Vui lòng cấu hình trước."
        }, status_code=400)

    url = f"{base_url}/api/public/papers/projects"
    try:
        def fetch():
            return requests.get(url, headers={"X-API-Key": api_key}, timeout=5)
        resp = await asyncio.to_thread(fetch)
        if resp.status_code == 200:
            data = resp.json()
            return {"success": True, "projects": data.get("data", [])}
        elif resp.status_code == 401:
            return JSONResponse({
                "success": False,
                "error": "Mã API Key không hợp lệ (401 Unauthorized). Vui lòng kiểm tra lại."
            }, status_code=401)
        else:
            return JSONResponse({
                "success": False,
                "error": f"SLR Backend trả về lỗi {resp.status_code}: {resp.text}"
            }, status_code=resp.status_code)
    except requests.exceptions.ConnectionError:
        return JSONResponse({
            "success": False,
            "error": f"Không thể kết nối tới SLR Backend tại {base_url}. Hãy chắc chắn server backend đang chạy (PORT 5000)."
        }, status_code=503)
    except Exception as e:
        return JSONResponse({"success": False, "error": f"Lỗi kiểm tra dự án: {str(e)}"}, status_code=500)

def _normalize_fetcher_draft(draft):
    """Expose the legacy nested review result in the Repository API draft schema."""
    if not isinstance(draft, dict) or not isinstance(draft.get("analysis"), dict):
        return draft
    outer_fields = {key: value for key, value in draft.items() if key != "analysis"}
    return {**outer_fields, **draft["analysis"]}


def _openalex_upload_fields(metadata, doi, analysis_draft=None):
    """Attach canonical OpenAlex topic IDs for the Repository's existing filters."""
    artifact = analysis_draft.get("openalex_classification") if isinstance(analysis_draft, dict) else None
    classification = (artifact.get("classification") if isinstance(artifact, dict) else None)
    provenance = (artifact.get("provenance") if isinstance(artifact, dict) else None)
    if not isinstance(classification, dict):
        classification = metadata.get("classification") if isinstance(metadata, dict) else None
        provenance = metadata.get("classificationProvenance") if isinstance(metadata, dict) else None
    openalex_id = ((artifact.get("openAlexId") if isinstance(artifact, dict) else None)
                   or (metadata.get("openAlexId") if isinstance(metadata, dict) else None))
    clean_classification = {}
    has_topics = False
    if isinstance(classification, dict):
        # Metadata can come from imported records; only forward bounded ID lists
        # accepted by the SLR-BE contract.
        for key in ("topicIds", "subfieldIds", "fieldIds", "domainIds"):
            values = classification.get(key)
            if isinstance(values, list):
                clean_values = list(dict.fromkeys(
                    value.strip()[:300] for value in values
                    if isinstance(value, str) and value.strip()
                ))[:20]
                if clean_values:
                    clean_classification[key] = clean_values
        primary_topic = classification.get("primaryTopicId")
        if isinstance(primary_topic, str) and primary_topic.strip():
            clean_classification["primaryTopicId"] = primary_topic.strip()[:300]
        taxonomy_version = classification.get("taxonomyVersion")
        if isinstance(taxonomy_version, str) and taxonomy_version.strip():
            clean_classification["taxonomyVersion"] = taxonomy_version.strip()[:100]
        has_topics = bool(clean_classification.get("topicIds"))
        has_complete_hierarchy = has_topics and all(
            clean_classification.get(key)
            for key in ("subfieldIds", "fieldIds", "domainIds")
        )
        if has_complete_hierarchy:
            return {
                "classification": clean_classification,
                "classificationProvenance": provenance if isinstance(provenance, dict) else None,
                "openAlexId": openalex_id.strip()[:300] if isinstance(openalex_id, str) and openalex_id.strip() else None,
            }
    openalex_id_is_valid = isinstance(openalex_id, str) and re.fullmatch(
        r"https?://openalex\.org/W\d+|W\d+", openalex_id, re.IGNORECASE
    )
    if (not doi or str(doi).startswith("slrwork_")) and not openalex_id_is_valid:
        return ({
            "classification": clean_classification,
            "classificationProvenance": provenance if isinstance(provenance, dict) else None,
            "openAlexId": openalex_id.strip()[:300] if isinstance(openalex_id, str) and openalex_id.strip() else None,
        } if has_topics else {})
    try:
        from automatic_sources import fetch_openalex_classification
        lookup_doi = "" if str(doi).startswith("slrwork_") else doi
        result = fetch_openalex_classification(lookup_doi, openalex_id)
        if isinstance(result, dict) and result.get("status") == "MATCHED":
            refreshed = result.get("classification")
            if isinstance(refreshed, dict) and refreshed.get("topicIds"):
                # Prefer OpenAlex's current hierarchy, but retain any existing
                # classification values the response did not include.
                merged_classification = dict(clean_classification)
                merged_classification.update(refreshed)
                result["classification"] = merged_classification
                if not result.get("classificationProvenance") and isinstance(provenance, dict):
                    result["classificationProvenance"] = provenance
                return result
        if has_topics:
            # A temporary OpenAlex failure must not erase previously saved topic IDs.
            return {
                "classification": clean_classification,
                "classificationProvenance": provenance if isinstance(provenance, dict) else None,
                "openAlexId": openalex_id.strip()[:300] if isinstance(openalex_id, str) and openalex_id.strip() else None,
            }
        return result or {}
    except Exception as exc:
        print(f"[OPENALEX] Topic classification unavailable for {doi}: {exc}")
        return {}


def _openalex_classification_artifact(fields):
    classification = fields.get("classification") if isinstance(fields, dict) else None
    if not isinstance(classification, dict) or not classification.get("topicIds"):
        return None
    provenance = fields.get("classificationProvenance")
    if not isinstance(provenance, dict):
        provenance = {"source": "PAPER_METADATA"}
    return {
        "schema_version": "openalex-topics.v1",
        "status": "MATCHED",
        "openAlexId": fields.get("openAlexId"),
        "classification": classification,
        "provenance": provenance,
    }


def _push_analysis_run_to_slr(store, doi, record, target_path, base_url, api_key, project_id):
    """Upload a completed Fetcher run and its exact full-text mapping snapshot."""
    from pathlib import Path

    analysis_record = store.get_analysis(doi)
    if not analysis_record or analysis_record.get("status") != "DONE" or not analysis_record.get("draft"):
        return {"success": True, "status": "not_available"}
    try:
        draft = analysis_record["draft"]
        if isinstance(draft, str):
            draft = json.loads(draft)
        draft = _normalize_fetcher_draft(draft)
        argumentation = store.get_argumentation(doi)
        if not isinstance(draft, dict) or not isinstance(argumentation, dict):
            raise ValueError("Analysis payload is incomplete")
        mapping_path = Path(target_path).with_suffix(".fulltext.json")
        if not mapping_path.is_file():
            raise FileNotFoundError(f"Missing full-text mapping: {mapping_path.name}")
        analysis_payload = {"analysis": {**analysis_record, "draft": draft, "argumentation": argumentation}}
        mapping_bytes = mapping_path.read_bytes()
        source_run_id = str(argumentation.get("id") or doi)

        metadata = record.get("metadata")
        if isinstance(metadata, str):
            metadata = json.loads(metadata) if metadata.strip() else {}
        if not isinstance(metadata, dict):
            metadata = {}
        openalex_fields = _openalex_upload_fields(metadata, doi, draft)
        authors = metadata.get("authors")
        if isinstance(authors, str):
            authors = [{"name": name.strip()} for name in authors.replace(";", ",").split(",") if name.strip()]
        elif isinstance(authors, list):
            authors = [{"name": author} if isinstance(author, str) else author for author in authors]
        try:
            year = int(str(metadata.get("year"))[:4]) if metadata.get("year") else None
        except (TypeError, ValueError):
            year = None
        metadata_payload = {
            "title": metadata.get("title") or record.get("title") or doi,
            "abstract": metadata.get("abstract"), "authors": authors, "year": year,
            "journal": metadata.get("journal") or metadata.get("venue"),
            "journalIssn": metadata.get("journalIssn") or metadata.get("issn"),
            "volume": metadata.get("volume"), "issue": metadata.get("issue"),
            "pages": metadata.get("pages"), "publicationDate": metadata.get("publicationDate"),
            "publisher": metadata.get("publisher"), "language": metadata.get("language"),
            "publicationType": metadata.get("publicationType"), "keywords": metadata.get("keywords"),
            "openAlexId": metadata.get("openAlexId") or openalex_fields.get("openAlexId"),
            "externalIdentifiers": metadata.get("externalIdentifiers"),
            **{key: value for key, value in openalex_fields.items() if key in {"classification", "classificationProvenance"}},
            "doi": doi, "sourceUrl": record.get("resolved_url") or metadata.get("sourceUrl") or metadata.get("url"),
            "sourceProvider": record.get("source") or metadata.get("sourceProvider") or "SLR_PAPER_FETCHER",
            "sourceId": source_run_id, "sourcePriority": 10,
        }
        metadata_payload = {key: value for key, value in metadata_payload.items() if value is not None}
        openalex_artifact = _openalex_classification_artifact(openalex_fields)
        if openalex_artifact:
            analysis_payload["analysis"]["draft"]["openalex_classification"] = openalex_artifact
        analysis_bytes = json.dumps(analysis_payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        digest = hashlib.sha256(analysis_bytes + b"\0" + mapping_bytes).hexdigest()
        response = requests.post(
            f"{base_url}/api/public/projects/{project_id}/analysis-runs",
            headers={"X-API-Key": api_key, "Idempotency-Key": f"paper-fetcher-{source_run_id[:80]}-{digest}"},
            data={"doi": doi, "metadata": json.dumps(metadata_payload, ensure_ascii=False)},
            files={
                "analysis": ("analysis.json", analysis_bytes, "application/json"),
                "fullTextMapping": (mapping_path.name, mapping_bytes, "application/json"),
            },
            timeout=180,
        )
        if response.status_code not in (200, 201):
            try:
                body = response.json()
                message = body.get("message") or body.get("error", {}).get("message") or response.text
            except Exception:
                message = response.text
            return {"success": False, "status": "failed", "message": f"Analysis sync HTTP {response.status_code}: {message}"}
        return {"success": True, "status": "uploaded", "run_id": (response.json().get("data") or {}).get("runId")}
    except Exception as exc:
        return {"success": False, "status": "failed", "message": str(exc)}

def _push_paper_to_repository(store, doi, record, target_path, base_url, api_key):
    """Upload a PDF and, when available, its completed analysis to the shared Repository."""
    from pathlib import Path
    try:
        raw = record.get("metadata")
        meta = json.loads(raw) if isinstance(raw, str) and raw.strip() else raw
        if not isinstance(meta, dict):
            meta = {}
        work_id = str(meta.get("slr_repository_work_id") or "").strip()
        work_doi = str(meta.get("doi") or "").strip() or ("" if str(doi).startswith("slrwork_") else str(doi))
        analysis = None
        analysis_draft = None
        openalex_fields = None
        mapping = None
        analysis_sync = {"status": "not_available"}
        row = store.get_analysis(doi)
        if row and row.get("status") == "DONE" and row.get("draft"):
            try:
                draft = row["draft"]
                if isinstance(draft, str):
                    draft = json.loads(draft)
                draft = _normalize_fetcher_draft(draft)
                analysis_draft = draft
                openalex_fields = _openalex_upload_fields(meta, doi, analysis_draft)
                argumentation = store.get_argumentation(doi)
                mapping_path = Path(target_path).with_suffix(".fulltext.json")
                if not isinstance(draft, dict) or not isinstance(argumentation, dict) or not mapping_path.is_file():
                    raise ValueError("Completed analysis or full-text mapping is missing")
                analysis = {"analysis": {**row, "draft": draft, "argumentation": argumentation}}
                openalex_artifact = _openalex_classification_artifact(openalex_fields)
                if openalex_artifact:
                    analysis["analysis"]["draft"]["openalex_classification"] = openalex_artifact
                mapping = mapping_path.read_bytes()
                analysis_sync = {"status": "ready"}
            except Exception as exc:
                analysis_sync = {"status": "failed", "message": str(exc)}
        if openalex_fields is None:
            openalex_fields = _openalex_upload_fields(meta, doi, analysis_draft)
        authors = meta.get("authors")
        if isinstance(authors, str):
            authors = [{"name": a.strip()} for a in authors.replace(";", ",").split(",") if a.strip()]
        elif isinstance(authors, list):
            authors = [{"name": a} if isinstance(a, str) else a for a in authors]
        try:
            year = int(str(meta.get("year"))[:4]) if meta.get("year") else None
        except (ValueError, TypeError):
            year = None
        run_id = str(((analysis or {}).get("analysis", {}).get("argumentation") or {}).get("id") or doi)
        metadata = {
            "title": meta.get("title") or record.get("title") or doi, "abstract": meta.get("abstract"),
            "authors": authors, "year": year, "journal": meta.get("journal") or meta.get("venue"),
            "journalIssn": meta.get("journalIssn") or meta.get("issn"), "volume": meta.get("volume"),
            "issue": meta.get("issue"), "pages": meta.get("pages"), "publicationDate": meta.get("publicationDate"),
            "publisher": meta.get("publisher"), "language": meta.get("language"),
            "publicationType": meta.get("publicationType"), "keywords": meta.get("keywords"),
            "openAlexId": meta.get("openAlexId") or openalex_fields.get("openAlexId"),
            "externalIdentifiers": meta.get("externalIdentifiers"),
            **{key: value for key, value in openalex_fields.items() if key in {"classification", "classificationProvenance"}},
            "doi": work_doi or None, "sourceUrl": record.get("resolved_url") or meta.get("sourceUrl") or meta.get("url"),
            "sourceProvider": record.get("source") or meta.get("sourceProvider") or "SLR_PAPER_FETCHER",
            "sourceId": run_id, "sourcePriority": 10,
        }
        # Zod optional fields must be absent when unknown; JSON null is not accepted.
        metadata = {key: value for key, value in metadata.items() if value is not None}
        source_path = Path(target_path)
        source_bytes = source_path.read_bytes()
        source_is_markdown = source_path.suffix.lower() in {".md", ".markdown"}
        metadata_bytes = json.dumps(metadata, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        analysis_bytes = json.dumps(analysis, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode() if analysis else b""
        digest = hashlib.sha256(source_bytes + b"\0" + metadata_bytes + b"\0" + analysis_bytes + b"\0" + (mapping or b"")).hexdigest()
        files = {} if source_is_markdown else {"pdf": (source_path.name, source_bytes, "application/pdf")}
        if analysis and mapping is not None:
            files["analysis"] = ("analysis.json", analysis_bytes, "application/json")
            files["fullTextMapping"] = (Path(target_path).with_suffix(".fulltext.json").name, mapping, "application/json")
        import_data = {"metadata": metadata_bytes.decode("utf-8"), **({"workId": work_id} if work_id else {"doi": work_doi})}
        if source_is_markdown and meta.get("slr_repository_source_artifact_id"):
            import_data["sourceArtifactId"] = meta["slr_repository_source_artifact_id"]
        response = requests.post(f"{base_url}/api/public/v1/repository/works/import",
            headers={"X-API-Key": api_key, "Idempotency-Key": f"paper-fetcher-repository-{digest}"},
            data=import_data, files=files, timeout=180)
        if response.status_code not in (200, 201):
            try:
                payload = response.json()
                message = payload.get("message") or payload.get("error", {}).get("message") or response.text
            except Exception:
                message = response.text
            return {"success": False, "message": f"Repository import HTTP {response.status_code}: {message}"}
        result = response.json().get("data") or {}
        if result.get("analysisStatus") == "READY":
            analysis_sync = {"status": "uploaded", "run_id": result.get("analysisRunId")}
        elif analysis_sync.get("status") == "ready":
            analysis_sync = {"status": "failed", "message": "Repository did not accept the analysis payload."}
        return {"success": True, "data": result, "analysis_sync": analysis_sync}
    except Exception as exc:
        return {"success": False, "message": str(exc)}


def _repository_api_headers(api_key):
    return {"X-API-Key": api_key, "Accept": "application/json"}


def _repository_get_work(base_url, api_key, work_id):
    response = requests.get(f"{base_url}/api/public/v1/repository/works/{work_id}",
                            headers=_repository_api_headers(api_key), timeout=60)
    response.raise_for_status()
    return response.json().get("data") or {}


def _repository_apply_openalex_classification(base_url, api_key, work_id, metadata, doi):
    """Look up OpenAlex topics and save their canonical IDs on an existing Work."""
    from automatic_sources import fetch_openalex_classification

    fields = fetch_openalex_classification(doi, metadata.get("openAlexId"))
    classification = fields.get("classification") if isinstance(fields, dict) else None
    if not isinstance(classification, dict) or not classification.get("topicIds"):
        return {"matched": False, "status": (fields or {}).get("status", "NOT_FOUND")}
    response = requests.patch(
        f"{base_url}/api/public/v1/repository/works/{work_id}/classification",
        headers={**_repository_api_headers(api_key), "Content-Type": "application/json"},
        json=classification,
        timeout=60,
    )
    response.raise_for_status()
    return {"matched": True, "status": "MATCHED"}


@app.post("/api/slr/repository/taxonomy-sync")
async def start_slr_repository_taxonomy_sync():
    settings.refresh_api_credentials()
    if not settings.SLR_API_KEY:
        return JSONResponse({"success": False, "error": "Configure an SLR Repository API key first."}, status_code=400)
    try:
        response = await asyncio.to_thread(
            requests.post,
            f"{settings.SLR_API_BASE_URL}/api/public/v1/repository/taxonomy/sync",
            headers=_repository_api_headers(settings.SLR_API_KEY), timeout=30,
        )
        payload = response.json()
        if not response.ok:
            errors = payload.get("errors")
            error = (errors[0].get("message") if isinstance(errors, list) and errors and isinstance(errors[0], dict)
                     else errors.get("message") if isinstance(errors, dict) else None)
            error = error or payload.get("message") or response.text
            return JSONResponse({"success": False, "error": str(error)[:500], "state": (payload.get("data") or {}).get("state")}, status_code=response.status_code)
        return {"success": True, "state": (payload.get("data") or {}).get("state")}
    except (requests.RequestException, ValueError) as exc:
        detail = getattr(getattr(exc, "response", None), "text", "") or str(exc)
        return JSONResponse({"success": False, "error": f"Taxonomy sync request failed: {detail[:500]}"}, status_code=502)


@app.get("/api/slr/repository/taxonomy-sync")
async def slr_repository_taxonomy_sync_status():
    settings.refresh_api_credentials()
    if not settings.SLR_API_KEY:
        return JSONResponse({"success": False, "error": "Configure an SLR Repository API key first."}, status_code=400)
    try:
        response = await asyncio.to_thread(
            requests.get,
            f"{settings.SLR_API_BASE_URL}/api/public/v1/repository/taxonomy/sync",
            headers=_repository_api_headers(settings.SLR_API_KEY), timeout=30,
        )
        payload = response.json()
        if not response.ok:
            errors = payload.get("errors")
            error = (errors[0].get("message") if isinstance(errors, list) and errors and isinstance(errors[0], dict)
                     else errors.get("message") if isinstance(errors, dict) else None)
            error = error or payload.get("message") or response.text
            return JSONResponse({"success": False, "error": str(error)[:500]}, status_code=response.status_code)
        return {"success": True, "state": (payload.get("data") or {}).get("state")}
    except (requests.RequestException, ValueError) as exc:
        detail = getattr(getattr(exc, "response", None), "text", "") or str(exc)
        return JSONResponse({"success": False, "error": f"Taxonomy sync status request failed: {detail[:500]}"}, status_code=502)


@app.get("/api/slr/repository/inbox")
async def slr_repository_inbox(cursor: str = "", limit: int = 50):
    base_url, api_key = settings.SLR_API_BASE_URL, settings.SLR_API_KEY
    if not api_key:
        return JSONResponse({"success": False, "error": "Configure an SLR Repository API key first."}, status_code=400)
    params = {"needsFetcherProcessing": "true", "limit": max(1, min(int(limit), 100))}
    if cursor:
        params["cursor"] = cursor
    try:
        response = await asyncio.to_thread(requests.get, f"{base_url}/api/public/v1/repository/works",
                                           headers=_repository_api_headers(api_key), params=params, timeout=60)
        response.raise_for_status()
        return {"success": True, **(response.json().get("data") or {})}
    except requests.RequestException as exc:
        detail = getattr(getattr(exc, "response", None), "text", "") or str(exc)
        return JSONResponse({"success": False, "error": f"SLR repository inbox request failed: {detail[:500]}"}, status_code=502)


@app.post("/api/slr/repository/works/{work_id}/process")
async def process_slr_repository_work(work_id: str):
    if not re.fullmatch(r"work_[A-Za-z0-9_-]{8,100}", work_id):
        return JSONResponse({"success": False, "error": "Invalid Work ID."}, status_code=400)
    base_url, api_key = settings.SLR_API_BASE_URL, settings.SLR_API_KEY
    if not api_key:
        return JSONResponse({"success": False, "error": "Configure an SLR Repository API key first."}, status_code=400)
    try:
        work = await asyncio.to_thread(_repository_get_work, base_url, api_key, work_id)
        artifacts_response = await asyncio.to_thread(
            requests.get, f"{base_url}/api/public/v1/repository/works/{work_id}/artifacts",
            headers=_repository_api_headers(api_key), params={"limit": 100}, timeout=60)
        artifacts_response.raise_for_status()
        artifacts = artifacts_response.json().get("data") or []
        has_analysis = any(item.get("kind") == "PAPER_ANALYSIS_JSON" and item.get("status") == "READY" for item in artifacts)
        classification = work.get("classification") or {}
        has_classification = bool(classification.get("topicIds")) and all(
            classification.get(key)
            for key in ("subfieldIds", "fieldIds", "domainIds")
        )
        doi = (work.get("identifiers") or {}).get("doi") or (work.get("metadata") or {}).get("doi")
        if has_analysis:
            if not has_classification:
                metadata = work.get("metadata") or {}
                identifiers = work.get("identifiers") or {}
                metadata = {**metadata, "openAlexId": identifiers.get("openAlexId") or metadata.get("openAlexId")}
                classification_result = await asyncio.to_thread(
                    _repository_apply_openalex_classification, base_url, api_key, work_id, metadata, doi
                )
                if classification_result.get("matched"):
                    return {"success": True, "work_id": work_id, "status": "complete",
                            "analysis": "already_complete", "taxonomy": "matched", "doi": doi}
                return {"success": True, "work_id": work_id, "status": "unclassified",
                        "analysis": "already_complete", "taxonomy": classification_result.get("status"), "doi": doi}
            return {"success": True, "work_id": work_id, "status": "complete",
                    "analysis": "already_complete", "doi": doi}

        source = next((item for item in artifacts if item.get("kind") == "SOURCE_PDF" and item.get("status") == "READY"), None)
        if not source:
            source = next((item for item in artifacts if item.get("kind") == "FULLTEXT_MARKDOWN" and item.get("status") == "READY"), None)
        if not source:
            return JSONResponse({"success": False, "work_id": work_id, "status": "unsupported_source",
                                 "error": "No ready PDF or Markdown source is available."}, status_code=422)
        source_is_markdown = source.get("kind") == "FULLTEXT_MARKDOWN"
        extension = ".md" if source_is_markdown else ".pdf"
        safe_id = re.sub(r"[^A-Za-z0-9_-]", "_", work_id)
        directory = settings.DOWNLOAD_FOLDER / "repository_inbox"
        directory.mkdir(parents=True, exist_ok=True)
        target_path = (directory / f"{safe_id}{extension}").resolve()
        download_url = f"{base_url}/api/public/v1/repository/works/{work_id}/artifacts/{source['artifactId']}/download"
        download_response = await asyncio.to_thread(requests.get, download_url, headers=_repository_api_headers(api_key), timeout=180)
        download_response.raise_for_status()
        if not source_is_markdown and not valid_pdf_bytes(download_response.content):
            return JSONResponse({"success": False, "work_id": work_id, "error": "The repository source artifact is not a valid PDF."}, status_code=422)
        if source_is_markdown:
            try:
                download_response.content.decode("utf-8")
            except UnicodeDecodeError:
                return JSONResponse({"success": False, "work_id": work_id, "error": "The Markdown source is not valid UTF-8."}, status_code=422)
        target_path.write_bytes(download_response.content)
        metadata = work.get("metadata") or {}
        record_key = normalize_doi(str(doi or "")) or f"slrwork_{work_id}"
        authors = metadata.get("authors") or []
        if isinstance(authors, list):
            authors = ", ".join(item if isinstance(item, str) else str(item.get("name") or "") for item in authors)
        local_metadata = {
            "title": metadata.get("title") or source.get("fileName") or record_key,
            "doi": normalize_doi(str(doi or "")) or None,
            "authors": authors, "abstract": metadata.get("abstract") or "",
            "year": metadata.get("publicationYear") or "", "journal": metadata.get("journal") or metadata.get("venue") or "",
            "openAlexId": (work.get("identifiers") or {}).get("openAlexId") or metadata.get("openAlexId"),
            "slr_repository_work_id": work_id,
            "slr_repository_source_artifact_id": source.get("artifactId"),
            "slr_repository_source_kind": source.get("kind"),
        }
        store = get_store()
        store.update(record_key, "DOWNLOADED", filename=target_path.name, file_path=str(target_path), source="SLR_REPOSITORY",
                     metadata=local_metadata, message="Imported from the shared SLR repository for analysis.")
        provider = settings.AI_DEFAULT_PROVIDER if settings.AI_DEFAULT_PROVIDER in {"ollama", "gemini"} else "ollama"
        accepted = await asyncio.to_thread(store.try_queue_analysis, record_key, provider)
        if accepted:
            _ANALYSIS_QUEUE.put_nowait((record_key, provider))
        return {"success": True, "work_id": work_id, "doi": normalize_doi(str(doi or "")) or None,
                "record_key": record_key, "status": "queued" if accepted else "already_queued", "title": local_metadata["title"]}
    except requests.RequestException as exc:
        detail = getattr(getattr(exc, "response", None), "text", "") or str(exc)
        return JSONResponse({"success": False, "work_id": work_id, "error": f"SLR repository processing failed: {detail[:500]}"}, status_code=502)
    except Exception as exc:
        return JSONResponse({"success": False, "work_id": work_id, "error": str(exc)[:500]}, status_code=500)


@app.post("/api/slr/push-papers")
async def push_papers_to_slr(request: Request):
    """Đẩy các file PDF đã chọn lên SLR Project qua Public API với streaming tiến trình thời gian thực (NDJSON)."""
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"success": False, "error": "Dữ liệu JSON không hợp lệ."}, status_code=400)

    project_id = str(data.get("project_id") or "").strip()
    destination = str(data.get("destination") or "project").strip().lower()
    dois = data.get("dois", [])

    if destination not in {"project", "repository"}:
        return JSONResponse({"success": False, "error": "destination must be project or repository."}, status_code=400)
    if destination == "project" and not project_id:
        return JSONResponse({"success": False, "error": "Vui lòng chọn hoặc nhập Mã Dự Án (Project ID)."}, status_code=400)
    if not isinstance(dois, list) or not dois:
        return JSONResponse({"success": False, "error": "Chưa chọn bài báo nào để tải lên."}, status_code=400)

    settings.refresh_api_credentials()
    base_url = settings.SLR_API_BASE_URL or "http://127.0.0.1:5000"
    api_key = settings.SLR_API_KEY
    if not api_key:
        return JSONResponse({"success": False, "error": "Configure an SLR API key first."}, status_code=400)
    upload_url = f"{base_url}/api/public/papers/upload-pdf"

    store = get_store()
    from pathlib import Path
    import json
    from datetime import datetime, timezone

    async def stream_upload():
        total = len(dois)
        success_count = 0
        fail_count = 0

        yield json.dumps({"type": "start", "total": total, "project_id": project_id or None, "destination": destination}) + "\n"

        for idx, doi in enumerate(dois):
            record = await asyncio.to_thread(store.get, doi)
            if not record:
                fail_count += 1
                yield json.dumps({
                    "type": "item_progress",
                    "index": idx,
                    "doi": doi,
                    "filename": "Unknown",
                    "success": False,
                    "message": "Không tìm thấy thông tin bài báo trong thư viện nội bộ.",
                    "completed": idx + 1,
                    "total": total,
                    "success_count": success_count,
                    "fail_count": fail_count
                }, ensure_ascii=False) + "\n"
                continue

            filename = record.get("filename") or f"{doi.replace('/', '_')}.pdf"
            file_path = record.get("file_path")
            target_path = Path(file_path) if file_path else (settings.DOWNLOAD_FOLDER / filename)

            if not target_path.exists() or not valid_pdf_file(target_path):
                fail_count += 1
                yield json.dumps({
                    "type": "item_progress",
                    "index": idx,
                    "doi": doi,
                    "filename": filename,
                    "success": False,
                    "message": "File PDF không tồn tại hoặc bị lỗi định dạng trên ổ đĩa.",
                    "completed": idx + 1,
                    "total": total,
                    "success_count": success_count,
                    "fail_count": fail_count
                }, ensure_ascii=False) + "\n"
                continue

            try:
                if destination == "repository":
                    result = await asyncio.to_thread(_push_paper_to_repository, store, doi, record, target_path, base_url, api_key)
                    if not result.get("success"):
                        fail_count += 1
                        yield json.dumps({"type": "item_progress", "index": idx, "doi": doi, "filename": target_path.name, "success": False, "message": result.get("message"), "completed": idx + 1, "total": total, "success_count": success_count, "fail_count": fail_count}, ensure_ascii=False) + "\n"
                        continue
                    imported = result.get("data") or {}
                    analysis_sync = result.get("analysis_sync") or {"status": "not_available"}
                    partial_failure = analysis_sync.get("status") == "failed"
                    message = f"Imported into shared repository (Work: {imported.get('workId')})."
                    if analysis_sync.get("status") == "uploaded":
                        success_count += 1
                        message += " Analysis and full-text mapping uploaded."
                    elif partial_failure:
                        fail_count += 1
                        message += " PDF/metadata uploaded; analysis sync failed: " + str(analysis_sync.get("message"))
                    else:
                        success_count += 1
                    try:
                        raw = record.get("metadata")
                        meta = json.loads(raw) if isinstance(raw, str) and raw.strip() else (raw if isinstance(raw, dict) else {})
                        meta["last_uploaded_repository_work_id"] = imported.get("workId")
                        meta["uploaded_at"] = datetime.now(timezone.utc).isoformat()
                        store.update(doi, record["status"], metadata=meta, message="Uploaded to shared Research Repository")
                    except Exception as exc:
                        print(f"[STORE UPDATE] Error: {exc}")
                    yield json.dumps({"type": "item_progress", "index": idx, "doi": doi, "filename": target_path.name, "success": not partial_failure, "outcome": "partial" if partial_failure else "success", "message": message, "work_id": imported.get("workId"), "analysis_sync": analysis_sync, "completed": idx + 1, "total": total, "success_count": success_count, "fail_count": fail_count}, ensure_ascii=False) + "\n"
                    continue

                def upload_one_file():
                    # Parse metadata safely if present
                    meta_dict = {}
                    try:
                        raw_meta = record.get("metadata")
                        if isinstance(raw_meta, str) and raw_meta.strip():
                            parsed = json.loads(raw_meta)
                            if isinstance(parsed, str):
                                parsed = json.loads(parsed)
                            if isinstance(parsed, dict):
                                meta_dict = parsed
                        elif isinstance(raw_meta, dict):
                            meta_dict = raw_meta
                    except Exception:
                        meta_dict = {}

                    # 1. Attempt Direct-to-Cloud Upload (Cloudinary signed upload)
                    try:
                        sig_url = f"{base_url}/api/public/papers/upload-signature"
                        sig_resp = requests.post(
                            sig_url,
                            json={"projectId": project_id, "fileName": target_path.name},
                            headers={"X-API-Key": api_key},
                            timeout=15,
                        )
                        if sig_resp.status_code in (200, 201):
                            sig_payload = sig_resp.json()
                            sig_data = sig_payload.get("data", {})
                            cld_upload_url = sig_data.get("uploadUrl")
                            api_key_cld = sig_data.get("apiKey")
                            timestamp = sig_data.get("timestamp")
                            signature = sig_data.get("signature")
                            folder = sig_data.get("folder")
                            public_id = sig_data.get("publicId")
                            base_name = sig_data.get("baseName")

                            if cld_upload_url and signature and api_key_cld:
                                with open(target_path, "rb") as f:
                                    cld_payload = {
                                        "api_key": api_key_cld,
                                        "timestamp": str(timestamp),
                                        "signature": signature,
                                        "folder": folder,
                                        "public_id": public_id,
                                    }
                                    cld_files = {"file": (target_path.name, f, "application/pdf")}
                                    cld_resp = requests.post(cld_upload_url, data=cld_payload, files=cld_files, timeout=120)

                                if cld_resp.status_code in (200, 201):
                                    cld_json = cld_resp.json()
                                    cld_public_id = cld_json.get("public_id")
                                    cld_secure_url = cld_json.get("secure_url")
                                    cld_bytes = cld_json.get("bytes", target_path.stat().st_size)

                                    authors_val = meta_dict.get("authors")
                                    authors_list = []
                                    if isinstance(authors_val, str) and authors_val.strip():
                                        authors_list = [{"name": a.strip()} for a in authors_val.replace(";", ",").split(",") if a.strip()]
                                    elif isinstance(authors_val, list):
                                        authors_list = [{"name": a if isinstance(a, str) else a.get("name", "")} for a in authors_val]

                                    year_val = None
                                    if meta_dict.get("year"):
                                        try:
                                            year_val = int(str(meta_dict.get("year")).strip()[:4])
                                        except Exception:
                                            year_val = None

                                    fin_payload = {
                                        "projectId": project_id,
                                        "baseName": base_name,
                                        "publicId": cld_public_id,
                                        "secureUrl": cld_secure_url,
                                        "fileName": target_path.name,
                                        "bytes": cld_bytes,
                                        "metadata": {
                                            "title": meta_dict.get("title") or record.get("title"),
                                            "doi": doi,
                                            "abstract": meta_dict.get("abstract"),
                                            "authors": authors_list if authors_list else None,
                                            "year": year_val,
                                            "journal": meta_dict.get("journal") or meta_dict.get("venue"),
                                        },
                                    }

                                    fin_url = f"{base_url}/api/public/papers/finalize-upload"
                                    fin_resp = requests.post(
                                        fin_url,
                                        json=fin_payload,
                                        headers={"X-API-Key": api_key},
                                        timeout=60,
                                    )
                                    if fin_resp.status_code in (200, 201):
                                        return fin_resp
                                    print(f"[DIRECT UPLOAD] Finalize returned {fin_resp.status_code}. Falling back to proxy upload.")
                                else:
                                    print(f"[DIRECT UPLOAD] Cloudinary upload returned {cld_resp.status_code}. Falling back to proxy upload.")
                            else:
                                print("[DIRECT UPLOAD] Incomplete signature payload. Falling back to proxy upload.")
                        else:
                            print(f"[DIRECT UPLOAD] Signature endpoint returned {sig_resp.status_code}. Falling back to proxy upload.")
                    except Exception as direct_err:
                        print(f"[DIRECT UPLOAD] Exception occurred: {direct_err}. Falling back to proxy upload.")

                    # 2. Fallback: Legacy proxy upload directly to backend
                    with open(target_path, "rb") as f:
                        files = {"file": (target_path.name, f, "application/pdf")}
                        data_fields = {"projectId": project_id}
                        headers = {"X-API-Key": api_key}
                        return requests.post(upload_url, files=files, data=data_fields, headers=headers, timeout=120)

                resp = await asyncio.to_thread(upload_one_file)

                if resp.status_code in (200, 201):
                    res_json = resp.json()
                    imported_ids = res_json.get("data", {}).get("importedPaperIds", [])
                    msg = f"Đã upload & import thành công (Mã Paper: {', '.join(imported_ids) if imported_ids else 'OK'})"
                    analysis_sync = await asyncio.to_thread(
                        _push_analysis_run_to_slr, store, doi, record, target_path, base_url, api_key, project_id
                    )
                    if not analysis_sync.get("success"):
                        fail_count += 1
                        msg += "; PDF upload succeeded but analysis sync failed: " + str(analysis_sync.get("message"))
                    else:
                        success_count += 1
                        if analysis_sync.get("status") == "uploaded":
                            msg += " and the analysis run/full-text mapping were synced"

                    try:
                        raw_meta = record.get("metadata")
                        meta = {}
                        if isinstance(raw_meta, str) and raw_meta.strip():
                            parsed = json.loads(raw_meta)
                            if isinstance(parsed, str):
                                parsed = json.loads(parsed)
                            if isinstance(parsed, dict):
                                meta = parsed
                        elif isinstance(raw_meta, dict):
                            meta = raw_meta
                        meta["last_uploaded_project"] = project_id
                        meta["uploaded_at"] = datetime.now(timezone.utc).isoformat()
                        store.update(doi, record["status"], metadata=meta, message=f"Đã đẩy lên dự án {project_id}")
                    except Exception as meta_err:
                        print(f"[STORE UPDATE] Error: {meta_err}")

                    yield json.dumps({
                        "type": "item_progress",
                        "index": idx,
                        "doi": doi,
                        "filename": target_path.name,
                        "success": bool(analysis_sync.get("success")),
                        "outcome": "success" if analysis_sync.get("success") else "partial",
                        "message": msg,
                        "paper_ids": imported_ids,
                        "analysis_sync": analysis_sync,
                        "completed": idx + 1,
                        "total": total,
                        "success_count": success_count,
                        "fail_count": fail_count
                    }, ensure_ascii=False) + "\n"
                else:
                    fail_count += 1
                    error_msg = f"HTTP {resp.status_code}: {resp.text}"
                    try:
                        err_json = resp.json()
                        if err_json.get("message"):
                            error_msg = err_json["message"]
                        elif err_json.get("error", {}).get("message"):
                            error_msg = err_json["error"]["message"]
                    except Exception:
                        pass
                    yield json.dumps({
                        "type": "item_progress",
                        "index": idx,
                        "doi": doi,
                        "filename": target_path.name,
                        "success": False,
                        "message": error_msg,
                        "completed": idx + 1,
                        "total": total,
                        "success_count": success_count,
                        "fail_count": fail_count
                    }, ensure_ascii=False) + "\n"

            except requests.exceptions.Timeout:
                fail_count += 1
                yield json.dumps({
                    "type": "item_progress",
                    "index": idx,
                    "doi": doi,
                    "filename": target_path.name,
                    "success": False,
                    "message": "Quá thời gian phản hồi từ server (Timeout 120s).",
                    "completed": idx + 1,
                    "total": total,
                    "success_count": success_count,
                    "fail_count": fail_count
                }, ensure_ascii=False) + "\n"
            except requests.exceptions.ConnectionError:
                fail_count += 1
                yield json.dumps({
                    "type": "item_progress",
                    "index": idx,
                    "doi": doi,
                    "filename": target_path.name,
                    "success": False,
                    "message": f"Mất kết nối tới SLR Backend ({base_url}).",
                    "completed": idx + 1,
                    "total": total,
                    "success_count": success_count,
                    "fail_count": fail_count
                }, ensure_ascii=False) + "\n"
            except Exception as e:
                fail_count += 1
                yield json.dumps({
                    "type": "item_progress",
                    "index": idx,
                    "doi": doi,
                    "filename": target_path.name,
                    "success": False,
                    "message": f"Lỗi không xác định: {str(e)}",
                    "completed": idx + 1,
                    "total": total,
                    "success_count": success_count,
                    "fail_count": fail_count
                }, ensure_ascii=False) + "\n"

        yield json.dumps({
            "type": "done",
            "total": total,
            "success_count": success_count,
            "fail_count": fail_count,
            "project_id": project_id or None,
            "destination": destination
        }, ensure_ascii=False) + "\n"

    return StreamingResponse(
        stream_upload(),
        media_type="application/x-ndjson",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )

def run_server():
    # Let shutdown reach lifespan even when a stream is awaiting a human.
    uvicorn.run("app:app", host=settings.APP_HOST, port=settings.APP_PORT, log_level="warning",
                timeout_graceful_shutdown=10, reload=True, reload_dirs=[str(BASE_DIR)],
                reload_includes=["*.py", "*.html", "*.css", "*.js"])

def open_existing_server():
    """Reuse the live local server instead of starting a competing reload process."""
    url = f"http://{settings.APP_HOST}:{settings.APP_PORT}"
    try:
        response = requests.get(f"{url}/api/health", timeout=1)
        if response.status_code != 200:
            return False
    except requests.RequestException:
        return False
    print(f"SLR Paper Fetcher is already running at {url}; opening the existing server.")
    webbrowser.open(url)
    return True

if __name__ == "__main__":
    url = f"http://{settings.APP_HOST}:{settings.APP_PORT}"
    if open_existing_server():
        sys.exit(0)
    print(f"Starting backend server at {url}")
    # The UI is now opened directly inside the Playwright browser's anchor tab
    run_server()
