uv run perceptra ingest-dataset datasets/GHIM-10K --workers 6
2026-11-23 15:58:42,551 [INFO] [src.app]: Flask application initialized successfully.
2026-11-23 15:58:42,568 [INFO] [src.app]: Flask application initialized successfully.

╔══════════════════════════════════════════════════════════════════╗
║ PERCEPTRA DATASET INGESTION: GHIM-10K                           ║
╚══════════════════════════════════════════════════════════════════╝
  • Source Folder      : /home/regisx001/Perceptra/datasets/GHIM-10K
  • Target Storage     : /home/regisx001/Perceptra/storage
  • Compute Features   : Yes (5 CBIR Descriptors)
  • Skip Existing      : True
  • Batch Commit Size  : 50
  • Worker Threads     : 6

Discovered 10,000 images across 20 categories:
  - aircraft: 500 images
  - buildings: 500 images
  - butterfly: 500 images
  - cars: 500 images
  - dragon fly: 500 images
  - fireworks: 500 images
  - flowers: 500 images
  - hen: 500 images
  - horses: 500 images
  - insects: 500 images
  - motorcycles: 500 images
  - mountains: 500 images
  - sea shores: 500 images
  - ships: 500 images
  - sunset: 500 images
  - temples: 500 images
  - trees: 500 images
  - valleys: 500 images
  - walls: 500 images
  - yacht: 500 images

Ingesting & Extracting Descriptors  [####################################]  100%  [yacht/15_8000.jpg]                

✓ Ingestion Completed Successfully!
  • Duration            : 707.09 seconds
  • Throughput          : 14.0 images/sec
  • Images Ingested     : 9,928
  • Images Skipped      : 72
  • Images Failed       : 0
  • Descriptors Indexed : 69,496
