"""
Query Document Vector Store
===========================
Parse in a patients documents or a query to the searchable ChromaDB
vectorestore and retrieve patient documents

Components:
- query_store: Allows user to ask questions about patients to retrieve relevant documents
"""
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
load_dotenv()

VECSTORE_PATH = "data/vectorstore"
EMBED_MODEL="kamalkraj/BioSimCSE-BioLinkBERT-BASE"
COLLECTION_NAME = "patient_info"

def query_store(query: str, n_results: int = 3):
  # ---- Setup --------------------------------
  embeddings = HuggingFaceEmbeddings(
    model_name=EMBED_MODEL,
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
  )

  vectorestore = Chroma(
    persist_directory=VECSTORE_PATH,
    embedding_function=embeddings,
    collection_name=COLLECTION_NAME
  )

  # ---- Query the vectorstore ------------------
  results = vectorestore.similarity_search(
    query,
    k=n_results
  )

  return results

if __name__ == "__main__":
  import argparse
  parser = argparse.ArgumentParser(
    prog="Patient Query",
    description="Query the patient document store for similar patients"
  )

  parser.add_argument('-q', '--query', type=str, required=True, help='Text query for patient documents')
  parser.add_argument('-n', '--n_results', type=int, default=3, help='How many documents to return')
  args = parser.parse_args()

  results = query_store(args.query, args.n_results)

  for i, doc in enumerate(results):
    print(f"==== Document {i+1} =====")
    print("METADATA:")
    print(f"Source: {doc.metadata.get('source')}\n")
    print("DOCUMENT:")
    print(doc.page_content)
