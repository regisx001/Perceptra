 perceptra ingest-dataset datasets/GHIM-10K --workers 6
2026-11-20 19:11:59,065 [INFO] [src.app]: Flask application initialized successfully.
2026-11-20 19:11:59,079 [INFO] [src.app]: Flask application initialized successfully.

╔══════════════════════════════════════════════════════════════════╗
║ PERCEPTRA DATASET INGESTION: GHIM-10K                           ║
╚══════════════════════════════════════════════════════════════════╝
  • Source Folder      : /home/regisx001/Perceptra/datasets/GHIM-10K
  • Target Storage     : /home/regisx001/Perceptra/storage
  • Compute Features   : Yes (5 CBIR Descriptors)
  • Skip Existing      : True
  • Batch Commit Size  : 50
  • Worker Threads     : 6

Discovered 3,125 images across 7 categories:
  - ships: 125 images
  - sunset: 500 images
  - temples: 500 images
  - trees: 500 images
  - valleys: 500 images
  - walls: 500 images
  - yacht: 500 images

Ingesting & Extracting Descriptors  [####################################]  100%  [yacht/15_8000.jpg]            

✓ Ingestion Completed Successfully!
  • Duration            : 91.69 seconds
  • Throughput          : 33.5 images/sec
  • Images Ingested     : 3,075
  • Images Skipped      : 50
  • Images Failed       : 0
  • Descriptors Indexed : 15,375
