"""Small HTTP boundary around the documented SAFFRON CLI."""

import hashlib
import json
import os
import re
import socket
import subprocess
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


SAFFRON_HOME = Path(os.getenv("SAFFRON_HOME", "/opt/saffron"))
DEFAULT_CONFIG = SAFFRON_HOME / "examples" / "config.json"
MAX_TEXT_CHARACTERS = int(os.getenv("SAFFRON_MAX_TEXT_CHARACTERS", "25000000"))
RUN_TIMEOUT_SECONDS = int(os.getenv("SAFFRON_RUN_TIMEOUT_SECONDS", "900"))
TAXONOMY_MODEL_PATH = Path(os.getenv("SAFFRON_TAXONOMY_MODEL_PATH", str(SAFFRON_HOME / "models" / "default.json")))
TERM_EXTRACTION_URL = "http://127.0.0.1:9001/api/v1/term-extraction"
TERM_EXTRACTION_JAR = SAFFRON_HOME / "term" / "target" / "term-exec.jar"
POS_MODEL_URL = "https://nightlies.apache.org/opennlp/models-1.5/en-pos-maxent.bin"
LEMMATIZER_URL = "https://raw.githubusercontent.com/apache/incubator-nlpcraft/v0.8.0/external/opennlp/en-lemmatizer.dict"
JOB_LOCK = threading.Lock()
TERM_PROCESS = None
TERM_LOG = None
app = FastAPI(title="Fetcher SAFFRON Runner", version="1.0")


class PaperRequest(BaseModel):
    run_id: str = Field(min_length=1, max_length=120)
    doi: str = Field(default="", max_length=1000)
    title: str = Field(default="", max_length=4000)
    text: str = Field(min_length=500, max_length=MAX_TEXT_CHARACTERS)
    language: str = Field(default="und", max_length=100)


def _read_json(path: Path, optional=False):
    if optional and not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=502, detail=f"SAFFRON output {path.name} is missing or invalid JSON.") from exc


def _prepare_config(target: Path):
    config = _read_json(DEFAULT_CONFIG)
    if not isinstance(config, dict):
        raise HTTPException(status_code=500, detail="SAFFRON default configuration must be a JSON object.")
    term_config = config.setdefault("termExtraction", {})
    if not isinstance(term_config, dict):
        raise HTTPException(status_code=500, detail="SAFFRON termExtraction config is not an object.")
    # A single-paper run must allow terms that occur once; the upstream default is 2.
    term_config["minTermFreq"] = 1
    term_config["maxTerms"] = 200
    # Weirdness compares a target corpus with a reference corpus. A one-paper
    # analysis has no defensible reference corpus, and SAFFRON dereferences a
    # missing reference index when this feature is enabled. Retain the
    # document-local features and make that boundary explicit in the config.
    features = term_config.get("features", [])
    if isinstance(features, list):
        term_config["features"] = [feature for feature in features if feature != "weirdness"]
    term_config["corpus"] = None
    taxonomy_config = config.setdefault("taxonomy", {})
    if isinstance(taxonomy_config, dict):
        taxonomy_config["returnRDF"] = False
        taxonomy_config["modelFile"] = str(TAXONOMY_MODEL_PATH)
    target.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    return config, digest


def _ensure_model(path: Path, url: str, validator, minimum_size: int):
    if path.is_file() and path.stat().st_size >= minimum_size:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".download")
    try:
        digest = hashlib.sha256()
        size = 0
        head = bytearray()
        with urllib.request.urlopen(url, timeout=120) as response, temporary.open("wb") as target:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                target.write(chunk)
                digest.update(chunk)
                size += len(chunk)
                if len(head) < 4096:
                    head.extend(chunk[:4096 - len(head)])
        if size < minimum_size or not validator(bytes(head)):
            raise ValueError(f"Downloaded model is invalid or unexpectedly small ({size} bytes).")
        temporary.replace(path)
        return digest.hexdigest()
    except (OSError, urllib.error.URLError, ValueError) as exc:
        temporary.unlink(missing_ok=True)
        raise HTTPException(status_code=503, detail=f"Could not prepare SAFFRON model {path.name}: {exc}") from exc


def _ensure_models():
    models_dir = SAFFRON_HOME / "models"
    pos_sha256 = _ensure_model(models_dir / "en-pos-maxent.bin", POS_MODEL_URL,
                               lambda head: head.startswith(b"PK"), 1_000_000)
    lemma_sha256 = _ensure_model(models_dir / "en-lemmatizer.dict.txt", LEMMATIZER_URL,
                                 lambda head: b"\t" in head and not head.lstrip().startswith(b"<"), 1_000_000)
    return {"en-pos-maxent.bin": pos_sha256, "en-lemmatizer.dict.txt": lemma_sha256}


def _start_term_service():
    global TERM_PROCESS, TERM_LOG
    if not TERM_EXTRACTION_JAR.is_file():
        raise RuntimeError("SAFFRON term extraction module was not built into the image.")
    TERM_LOG = (Path("/tmp") / "saffron-term-module.log").open("a", encoding="utf-8")
    TERM_PROCESS = subprocess.Popen(
        ["java", "--add-opens=java.base/java.lang=ALL-UNNAMED", "-Xms256m", "-Xmx2g",
         f"-Dsaffron.home={SAFFRON_HOME}",
         "-jar", str(TERM_EXTRACTION_JAR), "--server.port=9001"],
        cwd=str(SAFFRON_HOME), env={**os.environ, "SAFFRON_HOME": str(SAFFRON_HOME)},
        stdout=TERM_LOG, stderr=subprocess.STDOUT,
    )
    deadline = time.monotonic() + 90
    while time.monotonic() < deadline:
        if TERM_PROCESS.poll() is not None:
            raise RuntimeError("SAFFRON term extraction module exited during startup; inspect /tmp/saffron-term-module.log.")
        try:
            with socket.create_connection(("127.0.0.1", 9001), timeout=1):
                return
        except OSError:
            time.sleep(0.5)
    raise RuntimeError("SAFFRON term extraction module did not start within 90 seconds.")


def _stop_term_service():
    global TERM_PROCESS, TERM_LOG
    if TERM_PROCESS and TERM_PROCESS.poll() is None:
        TERM_PROCESS.terminate()
        try:
            TERM_PROCESS.wait(timeout=10)
        except subprocess.TimeoutExpired:
            TERM_PROCESS.kill()
    TERM_PROCESS = None
    if TERM_LOG:
        TERM_LOG.close()
        TERM_LOG = None


def _extract_terms_module(corpus, term_config):
    payload = json.dumps({"config": {"termExtraction": term_config}, "data": corpus},
                         ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(TERM_EXTRACTION_URL, data=payload,
                                     headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=RUN_TIMEOUT_SECONDS) as response:
            result = json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=502, detail=f"SAFFRON term extraction module failed: {exc}") from exc
    terms = result.get("termsMapping") if isinstance(result, dict) else None
    doc_terms = result.get("documentTermMapping") if isinstance(result, dict) else None
    if not isinstance(terms, list) or not isinstance(doc_terms, list):
        raise HTTPException(status_code=502, detail="SAFFRON term module returned an invalid output shape.")
    return terms, doc_terms


def _taxonomy_model_status():
    if not TAXONOMY_MODEL_PATH.is_file():
        return None, ("SAFFRON taxonomy model is missing. Supply a trained model at "
                      f"{TAXONOMY_MODEL_PATH} (or set SAFFRON_TAXONOMY_MODEL_PATH).")
    try:
        model_bytes = TAXONOMY_MODEL_PATH.read_bytes()
        model = json.loads(model_bytes.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, f"SAFFRON taxonomy model is unreadable or invalid JSON: {exc}"
    if not isinstance(model, dict) or not isinstance(model.get("classifierData"), str) or not model["classifierData"].strip():
        return None, "SAFFRON taxonomy model JSON must contain a non-empty classifierData field."
    return hashlib.sha256(model_bytes).hexdigest(), None


@app.on_event("startup")
def start_term_module():
    try:
        _start_term_service()
    except (OSError, RuntimeError) as exc:
        raise RuntimeError(f"Could not start the SAFFRON term extraction module: {exc}") from exc


@app.on_event("shutdown")
def stop_term_module():
    _stop_term_service()


@app.get("/health")
def health():
    ready = TERM_PROCESS is not None and TERM_PROCESS.poll() is None
    if not ready:
        raise HTTPException(status_code=503, detail="SAFFRON term extraction module is unavailable.")
    return {"status": "ok", "service": "fetcher-saffron-runner",
            "term_module": "ready", "saffron_home": str(SAFFRON_HOME)}


@app.post("/analyze")
def analyze(request: PaperRequest):
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,120}", request.run_id):
        raise HTTPException(status_code=400, detail="run_id contains unsupported characters.")
    if not DEFAULT_CONFIG.is_file() or not (SAFFRON_HOME / "saffron.sh").is_file():
        raise HTTPException(status_code=503, detail="SAFFRON CLI or its default configuration is unavailable.")
    if not TERM_PROCESS or TERM_PROCESS.poll() is not None:
        raise HTTPException(status_code=503, detail="SAFFRON term extraction module is unavailable.")
    if not JOB_LOCK.acquire(blocking=False):
        raise HTTPException(status_code=429, detail="SAFFRON is processing another paper; retry this request later.")
    try:
        with tempfile.TemporaryDirectory(prefix=f"{request.run_id[:24]}-", dir="/tmp") as temporary:
            run_dir = Path(temporary)
            corpus_path = run_dir / "paper.json"
            output_dir = run_dir / "output"
            output_dir.mkdir()
            config_path = run_dir / "config.json"
            corpus = {"documents": [{
                "id": request.doi or request.run_id,
                "name": request.title or request.doi or "Paper",
                "mime_type": "text/plain",
                "contents": request.text,
                "metadata": {"doi": request.doi, "language": request.language},
            }]}
            corpus_path.write_text(json.dumps(corpus, ensure_ascii=False), encoding="utf-8")
            config, config_sha256 = _prepare_config(config_path)
            model_checksums = _ensure_models()
            terms, doc_terms = _extract_terms_module(corpus, config["termExtraction"])
            taxonomy_model_sha256, taxonomy_error = _taxonomy_model_status()
            if taxonomy_error:
                return {
                    "run_id": request.run_id,
                    "saffron_ref": os.getenv("SAFFRON_GIT_REF", "unknown"),
                    "config_sha256": config_sha256,
                    "model_sha256": model_checksums,
                    "status": "PARTIAL",
                    "taxonomy_status": "UNAVAILABLE_MODEL",
                    "taxonomy_error": taxonomy_error,
                    "terms": terms,
                    "doc_terms": doc_terms,
                    "taxonomy": None,
                }
            command = ["bash", "./saffron.sh", str(corpus_path), str(output_dir), str(config_path), "-k", "TAXO"]
            try:
                completed = subprocess.run(command, cwd=SAFFRON_HOME, capture_output=True,
                                           text=True, timeout=RUN_TIMEOUT_SECONDS, check=False,
                                           env={**os.environ, "SAFFRON_HOME": str(SAFFRON_HOME)})
            except subprocess.TimeoutExpired as exc:
                raise HTTPException(status_code=504, detail="SAFFRON extraction exceeded its run timeout.") from exc
            if completed.returncode != 0:
                lines = (completed.stderr or completed.stdout or "").strip().splitlines()
                excerpt = lines[:8] + (["... (middle omitted) ..."] if len(lines) > 28 else []) + lines[-20:]
                detail = "\n".join(excerpt)[-6000:] or "SAFFRON CLI exited with a non-zero code."
                raise HTTPException(status_code=502, detail=detail)
            terms = _read_json(output_dir / "terms.json", optional=True) or terms
            doc_terms = _read_json(output_dir / "doc-terms.json", optional=True) or doc_terms
            taxonomy = _read_json(output_dir / "taxonomy.json", optional=True)
            if not isinstance(terms, list):
                raise HTTPException(status_code=502, detail="SAFFRON terms.json must contain an array.")
            if not isinstance(doc_terms, list):
                raise HTTPException(status_code=502, detail="SAFFRON doc-terms.json must contain an array.")
            return {
                "run_id": request.run_id,
                "saffron_ref": os.getenv("SAFFRON_GIT_REF", "unknown"),
                "config_sha256": config_sha256,
                "model_sha256": model_checksums,
                "taxonomy_model_sha256": taxonomy_model_sha256,
                "status": "DONE",
                "taxonomy_status": "AVAILABLE" if taxonomy else "EMPTY",
                "taxonomy_error": None,
                "terms": terms,
                "doc_terms": doc_terms,
                "taxonomy": taxonomy,
            }
    finally:
        JOB_LOCK.release()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
