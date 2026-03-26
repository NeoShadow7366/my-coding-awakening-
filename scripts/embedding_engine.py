import time
import json
import sqlite3
import requests
import os
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DATA_DIR / "model_metadata.db"
CONFIG_PATH = DATA_DIR / "service_config.json"
OLLAMA_API = "http://127.0.0.1:11434"

def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

def is_ollama_ready() -> bool:
    try:
        resp = requests.get(OLLAMA_API, timeout=3)
        return resp.status_code == 200
    except requests.RequestException:
        return False

def generate_embedding(text: str) -> list[float]:
    """Generate embedding using nomic-embed-text via Ollama."""
    try:
        resp = requests.post(
            f"{OLLAMA_API}/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": text},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json().get("embedding") or []
    except Exception as exc:
        print(f"Embedding request failed: {exc}")
        return []

def run_worker_pass():
    if not DB_PATH.exists() or not is_ollama_ready():
        return

    # Check for missing embeddings
    missing = []
    with sqlite3.connect(DB_PATH) as conn:
        try:
            # Join metadata and embeddings to find rows in metadata that are missing from embeddings
            rows = conn.execute("""
                SELECT m.metadata_key, m.payload_json
                FROM model_metadata m
                LEFT JOIN model_embeddings e ON m.metadata_key = e.metadata_key
                WHERE e.vector_json IS NULL
            """).fetchall()
        except sqlite3.OperationalError:
            return  # Table not ready yet
            
        for key, payload_json in rows:
            try:
                payload = json.loads(payload_json)
                
                # Construct synthetic document
                file_name = payload.get("file_name", "")
                model_name = payload.get("model_name", "")
                model_type = payload.get("model_type", "")
                base_model = payload.get("base_model", "")
                user_tags = payload.get("user_tags", [])
                
                # Weight tags higher by repeating them, include filename and properties
                doc = f"File: {file_name}. "
                if model_name: 
                    doc += f"Name: {model_name}. "
                if model_type or base_model:
                    doc += f"Type: {model_type} {base_model}. "
                if user_tags:
                    tags_str = ", ".join(user_tags)
                    doc += f"Tags: {tags_str}. "
                
                missing.append((key, doc.strip()))
            except Exception as e:
                print(f"Error parsing payload for {key}: {e}")

    for key, doc in missing:
        print(f"Computing embedding for {key}...")
        vector = generate_embedding(doc)
        if vector:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO model_embeddings (metadata_key, vector_json, updated_at) VALUES (?, ?, ?)",
                    (str(key), json.dumps(vector), int(time.time())),
                )
                conn.commit()
            print(f"Cached embedding for {key}")
        # brief sleep to yield
        time.sleep(0.5)

def main():
    print("Embedding background engine started.")
    while True:
        try:
            run_worker_pass()
        except Exception as e:
            print(f"Worker pass error: {e}")
        time.sleep(15)  # Poll every 15 seconds

if __name__ == "__main__":
    main()
