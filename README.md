# Genderize CSV Batch Processor

A powerful, high-performance batch processing tool designed to process full names and determine gender using the [Genderize.io](https://genderize.io/) API. 

This repository provides two complete versions:
1. **Desktop Python Script** (`process_gender.py`): Supports automatic key rotation, auto-resume for interrupted tasks, SSL verification bypass, and native Tkinter file selection.
2. **Web Version** (`index.html`): A lightweight, client-side web application hosted live on **GitHub Pages**.

---

## 🌟 Key Features

- **Full Name Compatibility**: Encodes full names properly to ensure maximum accuracy while keeping original name columns intact in the output CSV.
- **Multi-API Key Rotation**: Automatically switches to the next configured API key when daily limit quota errors (`HTTP 429`) occur.
- **Auto-Resume Capabilities (Python)**: Reads existing output files and skips previously processed phone numbers/records to avoid duplicate API calls.
- **Batch Processing**: Sends data in chunks of 10 requests per batch for fast and efficient execution.
- **Dynamic File Naming**: Generates clean output files appended with `_Processed.csv`.
- **Cross-Platform**: Tested and working smoothly on both **macOS** and **Windows**.

---

## 🌐 Live Web Version (GitHub Pages)

You can run the web-based processor directly in your browser without installing Python:

👉 **[Launch Genderize Batch Processor Web App](https://jobayr87.github.io/genderize-batch-processor/)**

### How to use the Web App:
1. *(Optional)* Enter your **Genderize.io API keys** (comma-separated for key rotation).
2. Click **Select CSV File** and upload your CSV.
3. Click **Process & Download CSV**. The processed file will download automatically once completed.

---

## 🐍 Desktop Version (`process_gender.py`)

### Prerequisites

Make sure you have **Python 3.x** installed on your system.

### Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/jobayr87/genderize-batch-processor.git](https://github.com/jobayr87/genderize-batch-processor.git)
   cd genderize-batch-processor