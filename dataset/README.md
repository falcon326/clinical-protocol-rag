# Dataset

## Selected starter source

**Mental Health Gap Action Programme (mhGAP) guideline for mental, neurological and substance use disorders — Third edition (2023)**

- Publisher: World Health Organization (WHO)
- Publication date: 20 November 2023
- Length: 184 pages
- ISBN: 9789240084278
- Official landing page: https://www.who.int/publications/i/item/9789240084278
- Direct PDF endpoint: https://iris.who.int/server/api/core/bitstreams/93e56376-0e64-4a08-bdd0-703313be5354/content

The guideline provides evidence-based recommendations for mental, neurological and substance-use conditions. It is a focused starter corpus, not a comprehensive medical dataset.

## Download and installation

From the repository root, run:

```bash
python dataset/download_dataset.py
```

The PDF will be saved to:

```text
dataset/pdfs/who_mhgap_guideline_2023.pdf
```

The `pdfs/` directory is intentionally not tracked by Git. Keep downloaded source files in this directory on your local machine. The ingestion pipeline reads all `*.pdf` files found there.

You can also download the PDF manually from the official WHO publication page and place it in `dataset/pdfs/`.

## Licence and responsible reuse

WHO's publication page identifies the 2023 publication as CC BY-NC-SA 3.0 IGO. This licence permits non-commercial use subject to attribution and share-alike conditions. Commercial use requires permission from WHO. Always verify the licence on the source page before reuse, adaptation, or redistribution.

This repository does not redistribute the PDF. It provides source metadata and a downloader that retrieves the file from the WHO-hosted endpoint. The PDF's licence is separate from the MIT licence applied to this repository's code.

## Adding more PDFs

1. Prefer primary sources from WHO, national health agencies, or recognized guideline organizations.
2. Verify publication date, edition, update status, and licence.
3. Add a record to `manifest.json` with title, publisher, date, source URL, and licence.
4. Save the PDF under `pdfs/`.
5. Rebuild the index using `python -m src.cli ingest --reset`.

Do not add patient records, personal health information, copyrighted documents without permission, or files whose provenance cannot be established.
