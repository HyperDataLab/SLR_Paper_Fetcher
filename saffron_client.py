"""HTTP adapter for the isolated SAFFRON CLI runner."""

import hashlib
import re
import subprocess
import threading
import time
from pathlib import Path

import requests

from config import BASE_DIR, settings


SCHEMA_VERSION = "1.0"
_START_LOCK = threading.Lock()


class SaffronError(RuntimeError):
    """A dependency, input, or SAFFRON run failure with a safe message."""


def _safe_json(response):
    try:
        value = response.json()
    except ValueError as exc:
        raise SaffronError("SAFFRON returned a response that was not valid JSON.") from exc
    if not isinstance(value, (dict, list)):
        raise SaffronError("SAFFRON returned an unexpected response shape.")
    return value


def _stable_term_id(label):
    normalized = " ".join(str(label or "").split()).casefold()
    return "saffron-term-" + hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:24]


def _text_evidence(term, text, sections, limit=20):
    label = " ".join(str(term or "").split()).strip()
    if not label or len(label) > 300:
        return []
    pattern = r"(?<!\w)" + r"\s+".join(re.escape(part) for part in label.split()) + r"(?!\w)"
    try:
        matches = list(re.finditer(pattern, text, flags=re.IGNORECASE | re.UNICODE))[:limit]
    except re.error:
        return []
    evidence = []
    for match in matches:
        start, end = match.span()
        section = next((item for item in sections
                        if isinstance(item, dict)
                        and isinstance(item.get("start_offset"), int)
                        and isinstance(item.get("end_offset"), int)
                        and item["start_offset"] <= start < item["end_offset"]), None)
        if not section or end > int(section.get("end_offset", -1)):
            continue
        evidence.append({
            "section_id": section.get("section_id"), "start_offset": start,
            "end_offset": end, "page": section.get("page"), "quote": text[start:end],
        })
    return evidence


def _flatten_taxonomy(value):
    if isinstance(value, dict) and isinstance(value.get("taxonomy"), (dict, list)):
        value = value["taxonomy"]
    if isinstance(value, list):
        roots = value
    elif isinstance(value, dict):
        root = value.get("root")
        roots = root if isinstance(root, list) else [root if isinstance(root, dict) else value]
    else:
        roots = []
    nodes, edges, seen = [], [], set()

    def visit(node, parent_id=None):
        if not isinstance(node, dict):
            return
        label = node.get("root") or node.get("term_string") or node.get("label") or node.get("term")
        if not isinstance(label, str) or not label.strip() or label == "HEAD_TERM":
            for child in node.get("children") or []:
                visit(child, parent_id)
            return
        label = " ".join(label.split())
        node_id = _stable_term_id(label)
        if node_id in seen:
            return
        seen.add(node_id)
        nodes.append({"term_id": node_id, "label": label, "score": node.get("score"),
                      "link_score": node.get("linkScore")})
        if parent_id:
            edges.append({"parent_term_id": parent_id, "child_term_id": node_id,
                          "relation_type": "parent_child", "link_score": node.get("linkScore"),
                          "review_status": "candidate"})
        for child in node.get("children") or []:
            visit(child, node_id)

    for root in roots:
        visit(root)
    return {"nodes": nodes, "edges": edges}


def _language_info(metadata):
    language = str((metadata or {}).get("language") or "").strip()
    if not language:
        return "und", "unknown"
    language = language.replace("_", "-")
    return language, "supported" if language.split("-", 1)[0].lower() == "en" else "unsupported"


class SaffronClient:
    def __init__(self):
        self.base_url = settings.SAFFRON_API_URL.rstrip("/")
        self.session = requests.Session()

    def health(self):
        response = self.session.get(f"{self.base_url}/health", timeout=(3, 8))
        if response.status_code != 200:
            return False
        payload = _safe_json(response)
        return isinstance(payload, dict) and payload.get("status") == "ok"

    def _start_compose_service(self):
        if settings.SAFFRON_MANAGED_BY_COMPOSE or not settings.SAFFRON_AUTO_START:
            return
        compose_file = Path(BASE_DIR) / "compose.yaml"
        command = ["docker", "compose", "-f", str(compose_file), "up", "-d", "saffron"]
        try:
            engine = subprocess.run(
                ["docker", "info", "--format", "{{.ServerVersion}}"],
                cwd=str(BASE_DIR), capture_output=True, text=True, timeout=8, check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise SaffronError("Docker Engine did not respond within 8 seconds; start Docker Desktop and retry.") from exc
        except OSError as exc:
            raise SaffronError("Docker CLI is unavailable; install Docker Desktop or disable SAFFRON auto-start.") from exc
        if engine.returncode != 0:
            detail = (engine.stderr or engine.stdout or "").strip().splitlines()
            message = detail[-1][:300] if detail else "Docker Engine is not running."
            raise SaffronError(f"Docker Engine is unavailable: {message}")
        try:
            completed = subprocess.run(command, cwd=str(BASE_DIR), capture_output=True,
                                       text=True, timeout=1200, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise SaffronError("Không khởi động được SAFFRON qua Docker Compose. Hãy kiểm tra Docker Desktop/Engine.") from exc
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or "").strip().splitlines()
            message = detail[-1][:300] if detail else "Docker Compose exited with an error."
            raise SaffronError(f"Không khởi động được SAFFRON qua Docker Compose: {message}")

    def ensure_ready(self):
        with _START_LOCK:
            try:
                if self.health():
                    return True
            except requests.RequestException:
                pass
            self._start_compose_service()
            deadline = time.monotonic() + settings.SAFFRON_STARTUP_TIMEOUT_SECONDS
            while time.monotonic() < deadline:
                try:
                    if self.health():
                        return True
                except requests.RequestException:
                    pass
                time.sleep(2)
            raise SaffronError("SAFFRON chưa sẵn sàng. Kiểm tra trạng thái container và log của service saffron.")

    def analyze_paper(self, *, doi, title, mapping, paper_metadata=None):
        if not isinstance(mapping, dict):
            raise SaffronError("Full-text mapping không hợp lệ.")
        text = mapping.get("full_text")
        sections = mapping.get("sections")
        if not isinstance(text, str) or not text.strip() or not isinstance(sections, list):
            raise SaffronError("Bài báo chưa có full-text mapping hợp lệ để trích xuất term.")
        if len(text) < 500:
            return {"schema_version": SCHEMA_VERSION, "status": "INSUFFICIENT_TEXT",
                    "error": "Full-text mapping is shorter than the minimum extraction threshold."}

        language, language_status = _language_info(paper_metadata or {})
        pdf_sha256 = str(mapping.get("source_pdf_sha256") or "")
        text_sha256 = hashlib.sha256(text.encode("utf-8")).hexdigest()
        identity = "\0".join((str(doi or "").strip().casefold(), pdf_sha256, text_sha256))
        run_id = "fetcher-" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:32]
        base = {
            "schema_version": SCHEMA_VERSION,
            "status": "PENDING",
            "run_id": run_id,
            "paper": {"doi": doi, "title": title or "", "source_pdf_sha256": pdf_sha256,
                      "full_text_sha256": text_sha256, "mapping_schema_version": mapping.get("schema_version"),
                      "language": language, "language_status": language_status},
            "extractor": {"name": "SAFFRON", "version": settings.SAFFRON_GIT_REF,
                          "config": "per-paper config: minTermFreq=1; maxTerms=200; taxonomy=enabled",
                          "method": "Term Extraction + Taxonomy"},
            "terms": [], "taxonomy": {"status": "PENDING", "nodes": [], "edges": []},
        }
        if language_status == "unsupported":
            return {**base, "status": "UNSUPPORTED_LANGUAGE",
                    "taxonomy": {"status": "SKIPPED", "nodes": [], "edges": []}}

        try:
            self.ensure_ready()
            response = self.session.post(
                f"{self.base_url}/analyze",
                json={"run_id": run_id, "doi": doi or "", "title": title or "",
                      "text": text, "language": language},
                timeout=(10, settings.SAFFRON_RUN_TIMEOUT_SECONDS + 30),
            )
            if response.status_code != 200:
                detail = response.text.strip().replace("\n", " ")[:500]
                raise SaffronError(f"SAFFRON extraction failed (HTTP {response.status_code}): {detail}")
            payload = _safe_json(response)
            raw_terms = payload.get("terms") if isinstance(payload, dict) else None
            raw_doc_terms = payload.get("doc_terms") if isinstance(payload, dict) else None
            raw_taxonomy = payload.get("taxonomy") if isinstance(payload, dict) else None
            if not isinstance(raw_terms, list) or not isinstance(raw_doc_terms, list):
                raise SaffronError("SAFFRON runner returned an invalid term output shape.")

            doc_term_counts = {}
            for item in raw_doc_terms:
                if not isinstance(item, dict):
                    continue
                label = item.get("term_string") or item.get("term") or item.get("label") or item.get("string")
                if label:
                    try:
                        doc_term_counts[" ".join(str(label).split()).casefold()] = int(item.get("occurrences") or item.get("count") or 0)
                    except (TypeError, ValueError):
                        pass
            terms = []
            for item in raw_terms:
                if not isinstance(item, dict):
                    continue
                label = item.get("term_string") or item.get("term") or item.get("label") or item.get("string")
                if not isinstance(label, str) or not label.strip():
                    continue
                label = " ".join(label.split())
                evidence = _text_evidence(label, text, sections)
                terms.append({
                    "term_id": _stable_term_id(label), "label": label, "surface_form": label,
                    "language": language, "rank": len(terms) + 1,
                    "raw_score": item.get("score"), "score_method": "SAFFRON configured Term Extraction",
                    "occurrences": doc_term_counts.get(label.casefold(), 0),
                    "evidence": evidence,
                    "review_status": "candidate" if evidence else "needs_evidence",
                    "provenance": "SAFFRON",
                })
            graph = _flatten_taxonomy(raw_taxonomy)
            evidence_resolved = sum(bool(term["evidence"]) for term in terms)
            return {
                **base,
                "status": (payload.get("status") if payload.get("status") in {"DONE", "PARTIAL"}
                           else "DONE" if terms else "NO_TERMS"),
                "extractor": {**base["extractor"], "version": payload.get("saffron_ref") or settings.SAFFRON_GIT_REF,
                              "config_sha256": payload.get("config_sha256"),
                              "model_sha256": payload.get("model_sha256"),
                              "taxonomy_model_sha256": payload.get("taxonomy_model_sha256")},
                "terms": terms,
                "taxonomy": {**graph, "status": payload.get("taxonomy_status") or
                             ("AVAILABLE" if graph["nodes"] else "EMPTY")},
                "error": payload.get("taxonomy_error"),
                "quality": {"term_count": len(terms), "evidence_resolved_count": evidence_resolved,
                            "needs_evidence_count": len(terms) - evidence_resolved,
                            "evidence_coverage": round(evidence_resolved / len(terms), 4) if terms else 0.0,
                            "acceptance_policy": "candidates require human review; terms without exact source spans need evidence review"},
                "raw_output": {"terms": raw_terms, "doc_terms": raw_doc_terms, "taxonomy": raw_taxonomy},
            }
        except (requests.RequestException, ValueError, SaffronError) as exc:
            return {**base, "status": "FAILED", "error": str(exc)[:500],
                    "taxonomy": {"status": "FAILED", "nodes": [], "edges": []}}
