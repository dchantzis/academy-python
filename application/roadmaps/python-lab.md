Python Lab — 30 Small Projects

A reference roadmap for exploring Python beyond FastAPI and backend web
development.

The goal is breadth: use small, practical projects to experience the
major areas where Python is commonly used. These projects can run in
parallel with the main JamesDoe V6 / FastAPI learning track whenever
a change of pace is useful.

How to use this roadmap

• Keep JamesDoe V6 as the main deep-learning track for application
architecture, SQLAlchemy, FastAPI, authentication, testing, and
deployment.
• Treat Python Lab as the breadth track.
• Projects can be short: roughly 30 minutes to a few hours for an
initial version.
• Prefer learning by building rather than studying a library in
isolation.
• Reuse earlier projects where possible: a script can later gain a
CLI, tests, charts, scheduling, packaging, or an API.
• The order generally moves from core Python and automation toward
specialised areas.

The 30 projects

1. File Organiser

Build: Scan a messy directory and organise files by extension/date.
Tools: pathlib, shutil
Learn: Filesystems, loops, dictionaries, functions, moving/renaming
files.
Extension: Add a dry-run mode.

2. CSV Analyser

Build: Read CSV data and calculate totals, averages, groupings and
statistics.
Tools: csv, then pandas
Learn: Structured files, data conversion, aggregation.

3. Excel Report Generator

Build: Read an .xlsx, analyse it, and create a formatted report
workbook.
Tools: openpyxl, pandas
Learn: Workbooks, worksheets, cells, formulas, formatting.

4. Spreadsheet Merger

Build: Combine several slightly inconsistent spreadsheets into one
clean dataset.
Tools: pandas, openpyxl
Learn: Cleaning, missing values, joins, normalisation.

5. Artwork Batch Processor

Build: Batch-process artwork scans: inspect, resize, convert, rename
and create web versions.
Tools: Pillow, pathlib
Learn: Image formats, dimensions, colour modes, DPI, batch
processing.
Personal use: Coffee & Sketch scans.

6. Image Metadata Inspector

Build: Report TIFF/JPEG/PNG dimensions, DPI, size, format and colour
mode.
Tools: Pillow, pathlib, optionally pandas
Learn: Metadata extraction and structured reporting.
Output: CSV/Excel artwork inventory.

7. Log Analyser

Build: Parse nginx/application logs and report endpoints, status
codes, IPs, errors and traffic by hour.
Tools: stdlib, collections.Counter, regex
Learn: Parsing, regular expressions, datetime, aggregation.

8. Website Scraper

Build: Crawl a website and extract titles, links, images and
metadata.
Tools: httpx, BeautifulSoup
Learn: HTTP, HTML/DOM parsing, URL handling.

9. Broken-Link Checker

Build: Crawl a website and identify broken internal/external links.
Tools: httpx, BeautifulSoup
Learn: Status codes, sets, URL normalisation, concurrency.
Personal use: Check JamesDoe after deployment.

10. API Data Collector

Build: Consume a public JSON API, validate responses and produce a
report.
Tools: httpx, Pydantic
Learn: HTTP clients, JSON, validation, typed external data.

11. CLI Application

Build: Turn an earlier script into a proper terminal application.
Tools: Typer
Learn: Commands, arguments, options, help output, exit codes.
Personal use: Preparation for JamesDoe admin commands.

12. PDF Report Generator

Build: Turn analysed data into a structured PDF report.
Tools: ReportLab
Learn: Document generation, page layout, tables and typography.

13. Charts and Data Visualisation

Build: Analyse a dataset and produce useful charts.
Tools: pandas, Matplotlib
Learn: Data series, grouping and visual communication.

14. SQLite Data Tool

Build: Import CSV/Excel into SQLite and query it.
Tools: sqlite3, optionally SQLAlchemy
Learn: Embedded databases, import pipelines, direct SQL vs ORM.

15. Background Job Processor

Build: Queue jobs such as image processing and execute them with
workers.
Tools: Redis + Celery/RQ/Dramatiq
Learn: Queues, workers, retries, long-running/background work.

16. Scheduled Automation

Build: Automatically run a report, import, backup or processing
task.
Tools: Python + cron/APScheduler
Learn: Scheduling, idempotency, logging, operations.

17. Browser Automation

Build: Control a browser, interact with pages/forms and extract
results.
Tools: Playwright
Learn: Selectors, dynamic pages, forms, browser events.

18. Testing Project

Build: Add a proper automated test suite to an earlier tool.
Tools: pytest
Learn: Unit tests, fixtures, parameterisation, temporary files,
integration tests.

19. Data Science Notebook

Build: Explore a real dataset interactively and answer questions.
Tools: Jupyter, pandas, NumPy
Learn: EDA, arrays, DataFrames and statistics.

20. First Machine-Learning Project

Build: Train a small understandable classifier or predictor.
Tools: scikit-learn
Learn: Features, targets, train/test data, fitting, prediction,
evaluation, overfitting.

21. Neural Network Project

Build: Create and train a small neural network.
Tools: PyTorch
Learn: Tensors, layers, forward passes, loss, optimisers, training
loops.

22. Text / NLP Tool

Build: Analyse, classify, search or group text.
Tools: scikit-learn and/or Hugging Face Transformers
Learn: Preprocessing, tokenisation, vectors, embeddings, semantic
similarity.

23. Computer Vision Experiment

Build: Detect, measure or analyse visual features in images.
Tools: OpenCV
Learn: Images as arrays, thresholding, edges, contours,
transformations.

24. Audio / Video Utility

Build: Inspect media, extract metadata/frames, create thumbnails or
automate conversions.
Tools: Python + FFmpeg
Learn: External programs, media pipelines, subprocesses.

25. System Monitoring Tool

Build: Monitor CPU, memory, disks, processes and selected Linux
services.
Tools: psutil
Learn: OS information, processes, resources and monitoring.
Personal use: A reporting utility for grendizer.

26. Network Utility

Build: Check hosts/services, response times and availability.
Tools: socket, asyncio, httpx
Learn: Sockets, timeouts, concurrent I/O and health checks.

27. Backup / Sync Utility

Build: A backup tool with manifests and checksum verification.
Tools: pathlib, shutil, hashlib
Learn: Copying, hashing, integrity, incremental processing and
failure handling.

28. Package Our Own Python Library

Build: Extract reusable code from earlier projects into an
installable package.
Tools: pyproject.toml, uv
Learn: Packaging, dependencies, public APIs and versioning.

29. Desktop Application

Build: Put a GUI around one of our existing utilities.
Tools: PySide/PyQt or Tkinter
Learn: GUI events, widgets, state and UI/application separation.

30. Small Game

Build: Pong, Breakout or another small game.
Tools: Pygame
Learn: Game loops, events, state, movement, collision detection and
rendering.

────────

Suggested progression

Stage A — Core Python in the real world

1. File Organiser
2. CSV Analyser
3. Excel Report Generator
4. Spreadsheet Merger
5. Artwork Batch Processor
6. Image Metadata Inspector
7. Log Analyser

Stage B — HTTP, automation and tooling

8. Website Scraper
9. Broken-Link Checker
10. API Data Collector
11. CLI Application
12. PDF Report Generator
13. Charts and Data Visualisation
14. SQLite Data Tool

Stage C — Operational Python

15. Background Job Processor
16. Scheduled Automation
17. Browser Automation
18. Testing Project
19. System Monitoring Tool
20. Network Utility
21. Backup / Sync Utility
22. Package Our Own Python Library

Stage D — Data, AI and specialist areas

19. Data Science Notebook
20. First Machine-Learning Project
21. Neural Network Project
22. Text / NLP Tool
23. Computer Vision Experiment
24. Audio / Video Utility
25. Desktop Application
26. Small Game

────────

Projects that can grow into each other

Spreadsheet pipeline

```text
CSV / Excel files
      ↓
clean and merge data
      ↓
analyse with pandas
      ↓
generate charts
      ↓
generate Excel/PDF report
      ↓
wrap in CLI
      ↓
schedule automatically
      ↓
add tests
      ↓
package reusable code
```

Coffee & Sketch artwork pipeline

```text
800-DPI TIFF scans
      ↓
inspect metadata
      ↓
validate dimensions / DPI
      ↓
rename consistently
      ↓
resize / convert
      ↓
generate thumbnails
      ↓
create CSV / Excel inventory
      ↓
eventually import into JamesDoe
```

Engineering / server tool

```text
logs / system metrics
      ↓
parse and aggregate
      ↓
produce reports
      ↓
add charts
      ↓
CLI interface
      ↓
scheduled execution
      ↓
tests
      ↓
potential FastAPI interface
```

────────

Two complementary learning tracks

JamesDoe V6 — depth

```text
Python
  ↓
SQLAlchemy
  ↓
FastAPI
  ↓
Pydantic
  ↓
Authentication
  ↓
Testing
  ↓
Deployment
  ↓
Django comparison
```

Python Lab — breadth

```text
Filesystem
Spreadsheets
Images
Data analysis
Automation
Scraping
CLI tools
PDFs
Background jobs
Browser automation
Testing
Data science
Machine learning
AI / NLP
Computer vision
Media
Linux / systems
Networking
Packaging
Desktop applications
Games
```

The objective is to finish with both a solid understanding of building
substantial Python applications and practical experience of why
Python is used across so many different technical domains.