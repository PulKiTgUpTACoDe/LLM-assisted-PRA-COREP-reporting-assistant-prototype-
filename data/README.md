# Document Placement Guide

Please place your downloaded documents in the following locations:

## 1. CRR Own Funds PDF

**File**: Full PDF of Own Funds CRR (all articles)  
**Location**: `data/pra_rulebook/CRR_Own_Funds.pdf`

Example:

```
data/
└── pra_rulebook/
    └── CRR_Own_Funds.pdf
```

## 2. Annex 1 Solvency Excel Sheet

**File**: Annex 1 Solvency Excel with CA1 template  
**Location**: `data/corep_templates/Annex_1_Solvency.xlsx`

Example:

```
data/
└── corep_templates/
    └── Annex_1_Solvency.xlsx
```

## 3. ITS Supervisory Reporting PDF

**File**: Final draft ITS on Supervisory Reporting (EBA-ITS-2017-01)  
**Location**: `data/corep_templates/EBA_ITS_2017_01_Supervisory_Reporting.pdf`

Example:

```
data/
└── corep_templates/
    └── EBA_ITS_2017_01_Supervisory_Reporting.pdf
```

---

## Quick Commands

After placing the files, run:

```bash
cd backend
venv\Scripts\activate
python scripts/ingest_documents.py
```

This will:

- Parse all PDFs and extract text
- Chunk documents into searchable segments
- Generate embeddings using Gemini
- Store in ChromaDB vector database
- Parse Excel template structure

---

## File Structure Summary

```
data/
├── pra_rulebook/
│   └── CRR_Own_Funds.pdf
└── corep_templates/
    ├── Annex_1_Solvency.xlsx
    └── EBA_ITS_2017_01_Supervisory_Reporting.pdf
```
