import os
import chromadb
from sentence_transformers import SentenceTransformer

RUNBOOKS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "knowledge_base", "runbooks")
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")

# This model turns text into embeddings. Small, fast, runs locally, free.
model = SentenceTransformer("all-MiniLM-L6-v2")

# PersistentClient saves the index to disk, so you don't have to rebuild it every time.
client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client.get_or_create_collection("runbooks")


def main():
    files = [f for f in os.listdir(RUNBOOKS_DIR) if f.endswith(".md")]
    print(f"Found {len(files)} runbook files.")

    for filename in files:
        filepath = os.path.join(RUNBOOKS_DIR, filename)
        with open(filepath, "r") as f:
            text = f.read()

        embedding = model.encode(text).tolist()

        # upsert = insert if new, update if it already exists (safe to re-run)
        collection.upsert(
            ids=[filename],
            embeddings=[embedding],
            documents=[text],
            metadatas=[{"filename": filename}],
        )
        print(f"Indexed: {filename}")

    print("Done. Index saved to", CHROMA_DIR)


if __name__ == "__main__":
    main()