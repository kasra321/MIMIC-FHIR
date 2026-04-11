"""
Build Document Vector Store
===========================
Convert a raw text documents of patient information into searchable
ChromaDB vector store.

Components:
- 
"""
import os
import duckdb
import numpy as np
from duckdb import DuckDBPyConnection
from typing import List, Literal
from pathlib import Path
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

load_dotenv()
base = Path(__file__).resolve().parent.parent.parent
DUCKDB_PATH = base / os.environ.get("DUCKDB_PATH")
EMBED_MODEL = os.environ.get("EMBED_MODEL")
VECSTORE_PATH = base / os.environ.get("VECSTORE_PATH")
SOURCE_CONFIG = {
  "mimic": [("mi_patient", "mi_condition", "mimic")],
  "synthea": [("syn_patient", "syn_condition", "synthea")],
  "all": [
          ("mi_patient", "mi_condition", "mimic"),
          ("syn_patient", "syn_condition", "synthea")
         ]
}

# ========================================
# DOCUMENT CREATION
# ========================================
def get_relevant_ids(
  con: DuckDBPyConnection,
  table1: str = "mi_patient",
  table2: str = "mi_condition"
) -> np.ndarray:
  """
  Generates a list of ids from tables for patients whose ids have
  patient details

  Args:
    con (DuckDBPyConnection): Connection to DuckDB
    table1 (str): Patient table. Defaults to "mi_patient"
    table2 (str): Any other table with patient information. Defaults to "mi_condition"

  Returns:
    np.ndarray: Array of patient_ids
  """
  return con.sql(
  f"""
SELECT resource_id FROM recommend.{table1}
INTERSECT
SELECT patient_id FROM recommend.{table2};
  """
  ).fetchnumpy()['resource_id']


def create_mimic_patient_document(
  patient_dict: dict,
  conditions_dict: dict,
  procedures_dict: dict,
  medication_dict: dict,
  vitals_dict: dict
) -> str:
  """
  Creates a text document from the MIMIC patient information

  Args:
    patient_dict (dict): Fields from patient table 
    conditions_dict (dict): Fields from conditions table
    procedures_dict (dict): Fields from procedures table
    medication_dict (dict): Fields from medication table
    vitals_dict (dict): Fields from vitals table
  
  Returns
    str: Formatted MIMIC patient document
  """
  # Initial patient info
  page_content = f"""
Patient Information:
- Name: {patient_dict.get('name', '')}
- Gender: {patient_dict.get('gender', '')}
- DOB: {patient_dict.get('birth_date', '')}
- Race: {patient_dict.get('race', '')}
- Ethnicity: {patient_dict.get('ethnicity', '')}
- Marital Status: {patient_dict.get('marital_status', '')}
  """

  # Conditions info
  base_conditions = """
Conditions
ONSET DATE, DIAGNOSIS DATE, CODE, CONDITION
"""
  for i in range(len(conditions_dict['patient_id'])):
    start_time = conditions_dict['start_timestamp'][i].astype('datetime64[s]').item().strftime('%m-%d-%Y %H:%M:%S')
    end_time = conditions_dict['end_timestamp'][i].astype('datetime64[s]').item().strftime('%m-%d-%Y %H:%M:%S')
    base_conditions += f"{i+1}. {start_time}, {end_time}, {conditions_dict['icd_code'][i]}, {conditions_dict['icd_name'][i]}\n"
  page_content += f"\n{base_conditions}"

  # Procedures info
  base_procedures = """
Procedures
PERFORMED DATE, CODE, PROCEDURE
"""
  for i in range(len(procedures_dict['patient_id'])):
    procedure_time = procedures_dict['performed_datetime'][i].astype('datetime64[s]').item().strftime('%m-%d-%Y %H:%M:%S')
    base_procedures += f"{i+1}. {procedure_time}, {procedures_dict['snomed_ct_id'][i]}, {procedures_dict['snomed_ct_procedure'][i]}\n"
  page_content += f"\n{base_procedures}"

  # Medication Dispense
  base_medications = """
Medication Dispensed
ADMINISTERED DATE, CODE, MEDICATION
"""
  for i in range(len(medication_dict['patient_id'])):
    administered_date = medication_dict['administered_date'][i].astype('datetime64[s]').item().strftime('%m-%d-%Y %H:%M:%S')
    base_medications += f"{i+1}. {administered_date}, {medication_dict['medication_code'][i]}, {medication_dict['medication'][i]}\n"
  page_content += f"\n{base_medications}"

  # Vitals
  base_vitals = """
Vitals
OBSERVATION DATE, VITALS
  """
  obs_vitals = ""
  curr_date = ""
  for i in range(len(vitals_dict['patient_id'])):
    observation_date = vitals_dict['observation_date'][i].astype('datetime64[s]').item().strftime('%m-%d-%Y %H:%M:%S')
    if curr_date == observation_date:
      obs_vitals += f" | {vitals_dict['obs_code'][i]}: {vitals_dict['value'][i]}{vitals_dict['unit'][i]} "
      if i == len(vitals_dict['patient_id'])-1:
        base_vitals += obs_vitals
    else:
      curr_date = observation_date
      base_vitals += obs_vitals
      if i == 0:
        obs_vitals = f"{observation_date}, {vitals_dict['obs_code'][i]}: {vitals_dict['value'][i]}{vitals_dict['unit'][i]}"
      else:
        obs_vitals = f"\n{observation_date}, {vitals_dict['obs_code'][i]}: {vitals_dict['value'][i]}{vitals_dict['unit'][i]}"
  page_content += f"\n{base_vitals}"

  return page_content


def create_synthea_patient_document(
  patient_dict: dict,
  conditions_dict: dict,
  procedures_dict: dict,
  medication_dict: dict,
  vitals_dict: dict
) -> Document:
  """
  Creates a text document from the synthea patient information

  Args:
    patient_dict (dict): Fields from patient table 
    conditions_dict (dict): Fields from conditions table
    procedures_dict (dict): Fields from procedures table
    medication_dict (dict): Fields from medication table
    vitals_dict (dict): Fields from vitals table
  
  Returns
    str: Formatted synthea patient document
  """
  # Initial patient info
  page_content = f"""
Patient Information:
- Name: {patient_dict.get('name', '')}
- Gender: {patient_dict.get('gender', '')}
- DOB: {patient_dict.get('birth_date', '')}
- Race: {patient_dict.get('race', '')}
- Ethnicity: {patient_dict.get('ethnicity', '')}
- Marital Status: {patient_dict.get('marital_status', '')}
  """

  # Conditions info
  base_conditions = """
Conditions
ONSET DATE, DIAGNOSIS DATE, CODE, CONDITION
"""
  for i in range(len(conditions_dict['patient_id'])):
    start_time = conditions_dict['onset_timestamp'][i].astype('datetime64[s]').item().strftime('%m-%d-%Y %H:%M:%S')
    end_time = conditions_dict['diagnosis_timestamp'][i].astype('datetime64[s]').item().strftime('%m-%d-%Y %H:%M:%S')
    base_conditions += f"{i+1}. {start_time}, {end_time}, {conditions_dict['condition_code'][i]}, {conditions_dict['condition'][i]}\n"
  page_content += f"\n{base_conditions}"

  # Procedures info
  base_procedures = """
Procedures
PERFORMED DATE, CODE, PROCEDURE
"""
  for i in range(len(procedures_dict['patient_id'])):
    procedure_time = procedures_dict['performed_date'][i].astype('datetime64[s]').item().strftime('%m-%d-%Y %H:%M:%S')
    base_procedures += f"{i+1}. {procedure_time}, {procedures_dict['procedure_code'][i]}, {procedures_dict['procedure'][i]}\n"
  page_content += f"\n{base_procedures}"

  # Medication Dispense
  base_medications = """
Medication Dispensed
ADMINISTERED DATE, CODE, MEDICATION
"""
  for i in range(len(medication_dict['patient_id'])):
    administered_date = medication_dict['administered_date'][i].astype('datetime64[s]').item().strftime('%m-%d-%Y %H:%M:%S')
    base_medications += f"{i+1}. {administered_date}, {medication_dict['medication_code'][i]}, {medication_dict['medication'][i]}\n"
  page_content += f"\n{base_medications}"

  # Vitals
  base_vitals = """
Vitals
OBSERVATION DATE, VITALS
  """
  obs_vitals = ""
  curr_date = ""
  for i in range(len(vitals_dict['patient_id'])):
    observation_date = vitals_dict['effective_timestamp'][i].astype('datetime64[s]').item().strftime('%m-%d-%Y %H:%M:%S')
    if curr_date == observation_date:
      obs_vitals += f" | {vitals_dict['vitals_code'][i]}: {vitals_dict['value'][i]}{vitals_dict['unit'][i]} "
      if i == len(vitals_dict['patient_id'])-1:
        base_vitals += obs_vitals
    else:
      curr_date = observation_date
      base_vitals += obs_vitals
      if i == 0:
        obs_vitals = f"{observation_date}, {vitals_dict['vitals_code'][i]}: {vitals_dict['value'][i]}{vitals_dict['unit'][i]}"
      else:
        obs_vitals = f"\n{observation_date}, {vitals_dict['vitals_code'][i]}: {vitals_dict['value'][i]}{vitals_dict['unit'][i]}"
  page_content += f"\n{base_vitals}"

  return page_content


def generate_docs(
  con: DuckDBPyConnection,
  ids: np.ndarray,
  doc_type: Literal["mimic", "synthea"]
) -> List[Document]:
  """
  Generates a list of langchain documents from the set of IDs parsed

  Args:
    con (DuckDBPyConnection): Connection to DuckDB
    ids (np.ndarray): List of patient_ids to pull from
    doc_type (str["mimic", "synthea"]): Either "mimic" or "synthea" depending
      on which document type being pulled from
  
  Returns:
    List[Document]: List of langchain formatted patient documents
  """
  prefix = "mi_" if doc_type == "mimic" else "syn_"
  documents = []
  count = 0
  ids = ids[:30] # TODO: Remove this
  print(f"[INGEST] Generating {len(ids)} documents...")
  for id in ids:
    count += 1
    # ---- Create necessary dictionaries for population --------------------
    patient = con.sql(f"SELECT * FROM recommend.{prefix}patient WHERE resource_id='{id}';").fetchnumpy()
    patient = {k: v[0].item() if hasattr(v[0], 'item') else v[0] for k, v in patient.items()}
    condition = con.sql(f"SELECT * FROM recommend.{prefix}condition WHERE patient_id='{id}';").fetchnumpy()
    procedure = con.sql(f"SELECT * FROM recommend.{prefix}procedure WHERE patient_id = '{id}';").fetchnumpy()
    medication = con.sql(f"SELECT * FROM recommend.{prefix}medication_dispense WHERE patient_id = '{id}';").fetchnumpy()
    vitals = con.sql(
      f"SELECT * FROM recommend.{prefix}vitals WHERE patient_id = '{id}'"
      f"{' AND obs_code IS NOT NULL' if doc_type == 'mimic' else ''} "
      f"ORDER BY {'observation_date' if doc_type == 'mimic' else 'effective_timestamp'};"
    ).fetchnumpy()

    if doc_type == "mimic":
      # ---- Create patient docs --------------------
      doc = create_mimic_patient_document(
        patient,
        condition,
        procedure,
        medication,
        vitals
      )
    else:
        doc = create_synthea_patient_document(
        patient,
        condition,
        procedure,
        medication,
        vitals
        )
    
    doc = Document(
      page_content=doc,
      metadata={
        "source": doc_type,
        "name": patient.get('name', ''),
        "gender": patient.get('gender', ''),
        "dob": patient.get('birth_date', ''),
        "race": patient.get('race', ''),
        "ethnicity": patient.get('ethnicity', ''),
        "marital_status": patient.get('marital_status', ''),
      }
    )
    documents.append(doc)

    # TODO: Remove this
    if count % 10 == 0:
      print(f"   {count}/{len(ids)} documents processed")
      print(doc)
  
  print(f"[INGEST] Loaded {len(documents)} patient documents")
  return documents

  
# ========================================
# VECTORSTORE
# ========================================
def build_vectorstore(
  doc_type: Literal["mimic", "synthea", "all"] = "all"
) -> Chroma:
  # ---- Load Components --------------------
  con = duckdb.connect(DUCKDB_PATH)
  splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    add_start_index=True
  )
  embeddings = HuggingFaceEmbeddings(
    model_name=EMBED_MODEL,
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
  )

  # ---- Define Documents --------------------
  config = SOURCE_CONFIG.get(doc_type)
  if config is None:
    raise ValueError(f"Unknown doc_type: '{doc_type}'. Expected one of {list(SOURCE_CONFIG.keys())}")

  print(f"[VECSTORE] Creating vectorstore with {doc_type.upper()} data")
  docs = []
  for tab1, tab2, dtype in config:
    ids = get_relevant_ids(con, tab1, tab2)
    docs += generate_docs(con, ids, dtype)
  
  # ---- Building the components --------------
  chunks = splitter.split_documents(docs)
  print(f"[VECSTORE] Split into {len(chunks)} chunks")

  print(f"[VECSTORE] Creating vectorstore...")
  vectorestore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=VECSTORE_PATH,
    collection_name="patient_info"
  )
  count = vectorestore._collection.count()
  print(f"[VECSTORE] Stored {count} vectors at '{VECSTORE_PATH}'")
  return vectorestore

if __name__ == "__main__":
  import argparse
  parser = argparse.ArgumentParser(
    prog="Patient vectorstore builder",
    description="Takes existing patient documents are creates a vectorstore to query from"
  )

  parser.add_argument(
    '-d',
    '--doctype',
    type=str,
    default='all',
    help='Category of documents to include in vectorstore. ("mimic", "synthea", "all")'
  )
  args = parser.parse_args()

  build_vectorstore(
    doc_type=args.doctype
  )
  