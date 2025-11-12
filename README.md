# 📚 Auto Dossier – PDF Merger with Google Drive

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Google Drive](https://img.shields.io/badge/Google%20Drive-API-green)
[![License: MIT](https://img.shields.io/badge/license-MIT-brightgreen)](https://opensource.org/licenses/MIT)

> 🧠 **Automate your document workflows:** create a **single, elegant PDF dossier** from multiple Google Drive folders — with chapter title pages, automatic upload, and public sharing.

The script **merges PDFs entirely in memory**, without storing or versioning any document locally.  
The final dossier is **uploaded directly to Google Drive** and shared via an **auto-generated public link**.

---

## ✨ Features

- 📁 **Automatic subfolder detection** — organizes PDFs by subfolder structure
- 📥 Downloads PDFs from Google Drive folders and subfolders
- 🖋️ Generates **styled chapter title pages** for each subfolder
- 📄 Merges all PDFs into **one clean, unified document**
- ☁️ Uploads automatically to a **public Drive folder** ("anyone with the link")
- 🔒 **No local storage** or repository versioning of PDFs
- 🔐 **Secure configuration** using environment variables
- ⚙️ Fully automated workflow written in Python
- 📝 Comprehensive logging and error handling

---

## 🗂️ Project Structure

```
/
├── core/
│   └── utils.py          # 🔧 Core functionality (auth, download, merge, upload)
├── main.py               # 🚀 Main script
├── config.py             # ⚙️ Configuration loader (reads from .env)
├── .env                  # 🔑 Your actual folder IDs (NOT committed!)
├── .env.example          # 📝 Template for configuration
├── .gitignore            # 🚫 Excludes sensitive files
├── credentials.json      # 🔑 Google OAuth credentials (NOT committed!)
├── token.json            # 🪪 Generated automatically on first run (NOT committed!)
├── pyproject.toml        # 📦 Poetry project file
├── requirements.txt      # 📋 Dependencies (pip alternative)
└── README.md             # 📘 Project documentation
```

---

## 📂 Google Drive Folder Structure

The script automatically detects and processes subfolders:

```
📁 My Curriculum (SOURCE folder)
├── 📁 Academic Background
│   ├── diploma.pdf
│   ├── transcript.pdf
│   └── certificates.pdf
│
├── 📁 Work Experience
│   ├── resume.pdf
│   ├── recommendation_letter.pdf
│   └── portfolio.pdf
│
├── 📁 Publications
│   ├── paper_2023.pdf
│   └── article_2024.pdf
│
└── 📁 Additional Documents
    ├── id_card.pdf
    └── proof_of_address.pdf
```

**Result:** Each subfolder becomes a section with its own title page in the merged PDF.

---

## 🧩 Prerequisites

- 🐍 **Python 3.11+**
- 🌐 A Google account with access to Google Drive
- 📁 Organized Drive folders:
  - `Source Folder` → parent folder containing subfolders with PDFs
  - `Destination Folder` → where merged PDF will be uploaded

---

## ⚙️ Setup

### 1️⃣ Install Poetry (Dependency Manager)

This project uses **[Poetry](https://python-poetry.org/)** to handle dependencies and virtual environments.  
If you don't have it installed yet, run:

**Linux / macOS:**

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

**Windows (PowerShell):**

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

After installation, verify:

```bash
poetry --version
```

**Alternative:** You can use pip instead: `pip install -r requirements.txt`

---

### 2️⃣ Install dependencies

```bash
poetry install
```

This command will:

- Create a virtual environment automatically
- Install all required packages from `pyproject.toml`

**Or with pip:**

```bash
pip install -r requirements.txt
```

---

### 3️⃣ Configure Google Cloud Project

#### A. Enable Google Drive API

1. Go to **[Google Cloud Console](https://console.cloud.google.com/)**
2. Create a **new project** (or select existing)
3. Enable **Google Drive API**
4. Navigate to **APIs & Services → Library**
5. Search for "Google Drive API" and click **Enable**

#### B. Configure OAuth Consent Screen

1. Go to **[OAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent)**
2. Choose **External** user type
3. Fill in required fields:
   - App name: `Auto Dossier` (or any name)
   - User support email: your email
   - Developer contact: your email
4. Click **Save and Continue**
5. **Add Scopes:**
   - Click "Add or Remove Scopes"
   - Add: `.../auth/drive.file` and `.../auth/drive.readonly`
   - Click **Update** → **Save and Continue**
6. **Add Test Users** (⚠️ CRITICAL):
   - Click **Add Users**
   - Enter your Gmail address
   - Click **Add** → **Save and Continue**

#### C. Create OAuth Credentials

1. Go to **[Credentials](https://console.cloud.google.com/apis/credentials)**
2. Click **Create Credentials → OAuth Client ID**
3. Application type: **Desktop App**
4. Name: `Auto Dossier Client`
5. Click **Create**
6. Download the JSON file
7. Rename it to `credentials.json`
8. Place it in the project root directory

---

### 4️⃣ Configure Environment Variables

**Step 1:** Copy the template file

```bash
cp .env.example .env
```

**Step 2:** Edit `.env` with your actual folder IDs

```bash
nano .env  # or use any text editor
```

**Step 3:** Add your Google Drive folder IDs

```bash
# .env
SOURCE_FOLDER_ID=1aB2cD3eF4gH5iJ6kL7mN8oP9qR
DESTINATION_FOLDER_ID=9sT8uV7wX6yZ5aB4cD3eF2gH1iJ
MERGED_PDF_NAME=Complete_Curriculum_Vitae.pdf
```

#### 📍 How to get folder IDs:

1. Open the folder in Google Drive
2. Copy the ID from the URL:
   ```
   https://drive.google.com/drive/folders/[THIS_IS_THE_FOLDER_ID]
   ```

⚠️ **Security Note:** The `.env` file contains sensitive information and should **NEVER** be committed to version control. It's already listed in `.gitignore`.

---

### 5️⃣ Organize Your Google Drive Folders

Create subfolders in your SOURCE folder for automatic organization:

```
📁 SOURCE folder
  ├── 📁 01 - Education
  ├── 📁 02 - Work Experience
  ├── 📁 03 - Publications
  └── 📁 04 - Certificates
```

**Tips:**

- Use numbered prefixes (01, 02, 03) to control the order
- Subfolder names become section titles (converted to UPPERCASE)
- PDFs within each subfolder are sorted alphabetically

---

## ▶️ Usage

### First Run

```bash
poetry run python main.py
```

🔐 **Authentication flow:**

1. A browser window will open automatically
2. You may see: **"Google hasn't verified this app"**
3. Click **"Advanced"** → **"Go to Auto Dossier (unsafe)"**
   - ✅ This is safe — it's YOUR app!
4. Click **"Allow"** to grant permissions
5. A `token.json` file will be created automatically

### Subsequent Runs

```bash
poetry run python main.py
```

✨ Everything happens automatically:

- Scans for subfolders in SOURCE folder
- Downloads PDFs from each subfolder
- Creates title pages for each section
- Merges all PDFs with proper organization
- Uploads to destination folder
- Generates public sharing link
- No browser interaction needed

---

## 📊 Output

The script provides detailed logging:

```
============================================================
AUTO DOSSIER - PDF Merger with Subfolders
============================================================

📝 Step 1: Authenticating with Google Drive...
✓ Authentication completed

📥 Step 2: Scanning subfolders and downloading PDFs...
Found 4 subfolders

============================================================
Processing subfolder: 01 - Education
============================================================
[01 - Education] Found 3 PDF files
[01 - Education] Downloading: diploma.pdf (2.34 MB)
[01 - Education]   ✓ Downloaded successfully
...

✓ Download complete:
  • Sections found: 4
  • Total PDFs: 12
  • Section breakdown:
    - 01 - EDUCATION: 3 PDFs
    - 02 - WORK EXPERIENCE: 4 PDFs
    - 03 - PUBLICATIONS: 3 PDFs
    - 04 - CERTIFICATES: 2 PDFs

🔄 Step 3: Merging PDFs with title pages...

============================================================
Starting PDF merge process
Total sections: 4
============================================================

[Section 1/4] Processing: 01 - EDUCATION
  ✓ Cover page added
  Adding: diploma.pdf (5 pages)
  Adding: transcript.pdf (3 pages)
  Adding: certificates.pdf (2 pages)
  ✓ Section complete: 10 content pages

...

============================================================
✓ Merged PDF created with 45 total pages
============================================================

☁️  Step 4: Uploading merged PDF to Google Drive...
Uploading Complete_Curriculum_Vitae.pdf (12.34 MB)...
✓ PDF uploaded successfully!
✓ Public link: https://drive.google.com/file/d/...

============================================================
✅ PROCESS COMPLETED SUCCESSFULLY!
============================================================
📄 File: Complete_Curriculum_Vitae.pdf
📊 Total sections: 4
📚 Total PDFs merged: 12
🔗 Public link: https://drive.google.com/file/d/...
============================================================
```

Detailed logs are also saved to `pdf_merger.log`.

---

## 🎨 Customizing Section Titles

### Default Behavior

- Subfolder name: "Academic Background"
- Title page shows: **"ACADEMIC BACKGROUND"**

### Controlling Order

Use numbered prefixes:

```
📁 01 - Education
📁 02 - Work Experience
📁 03 - Skills
```

### Controlling PDF Order Within Sections

Prefix filenames with numbers:

```
01_bachelor_degree.pdf
02_master_degree.pdf
03_phd_certificate.pdf
```

---

## 🔒 Security Best Practices

### Files to NEVER commit:

- ✅ `.env` — Contains your actual folder IDs
- ✅ `credentials.json` — OAuth credentials
- ✅ `token.json` — Authentication token
- ✅ `*.log` — Log files
- ✅ `temp_*.pdf` — Temporary files

These are already in `.gitignore`, but always verify before pushing:

```bash
# Check what will be committed
git status

# Verify sensitive files are ignored
git check-ignore .env credentials.json token.json
```

### Files SAFE to commit:

- ✅ `.env.example` — Template with placeholders
- ✅ `config.py` — Reads from environment variables
- ✅ `.gitignore` — Excludes sensitive files
- ✅ All `.py` source files
- ✅ `README.md`, `pyproject.toml`, `requirements.txt`

---

## 🛠️ Troubleshooting

### Error: "credentials.json not found"

**Solution:** Download OAuth credentials from Google Cloud Console (see Setup Step 3)

### Error: "403 access_denied"

**Solution:** Make sure you added yourself as a test user in OAuth Consent Screen (Setup Step 3B)

### Error: "No subfolders found"

**Solution:**

- Make sure SOURCE folder contains subfolders (not just PDFs)
- Check folder permissions
- Verify SOURCE_FOLDER_ID is correct

### Error: "No files downloaded"

**Solution:**

- Check the SOURCE_FOLDER_ID in `.env`
- Verify you have access to the folder
- Ensure subfolders contain PDF files

### Error: "Token has expired"

**Solution:**

```bash
rm token.json
poetry run python main.py
# Re-authenticate when browser opens
```

### Error: "This app isn't verified"

**Solution:** This is normal for apps in testing mode

- Click "Advanced"
- Click "Go to [app name] (unsafe)"
- It's safe because it's YOUR app

### Issue: Wrong order of sections

**Solution:**

- Subfolders are processed alphabetically
- Prefix folders with numbers: `01 Education`, `02 Experience`, etc.

### Issue: PDFs in wrong order within sections

**Solution:**

- Files are sorted alphabetically within each folder
- Rename files with prefixes: `01_file.pdf`, `02_file.pdf`, etc.

---

## 🤝 Contributing

Pull requests and feature suggestions are welcome!

### To contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

**Note:** Never commit sensitive files (`.env`, `credentials.json`, `token.json`)

---

## 📝 Development Setup

For development with auto-reload:

```bash
poetry shell  # Activate virtual environment
python main.py
```

Install development dependencies:

```bash
poetry install --with dev
```

Run tests:

```bash
poetry run pytest
```

---

## 📋 Environment Variables Reference

| Variable                | Description                                | Example              |
| ----------------------- | ------------------------------------------ | -------------------- |
| `SOURCE_FOLDER_ID`      | Google Drive parent folder with subfolders | `1aB2cD3eF4gH5iJ6kL` |
| `DESTINATION_FOLDER_ID` | Folder where merged PDF will be saved      | `9sT8uV7wX6yZ5aB4cD` |
| `MERGED_PDF_NAME`       | Name of the output file                    | `My_Document.pdf`    |

---

## 📖 Advanced Usage

### Custom Title Mapping

If you want different titles than subfolder names, add to `config.py`:

```python
CUSTOM_TITLES = {
    'Academic Background': 'EDUCATION & QUALIFICATIONS',
    'Work Experience': 'PROFESSIONAL EXPERIENCE',
    'Publications': 'RESEARCH & PUBLICATIONS'
}
```

### Processing Single Folder (Legacy Mode)

If you don't want subfolder processing, use:

```python
# In main.py
docs = download_files(service, SOURCE)
sections = [("MY DOCUMENTS", docs)]
```

---

## 📜 License

This project is licensed under the **[MIT License](/LICENSE)**.  
Feel free to use, modify, and distribute it responsibly. 💡

---

## 🙏 Acknowledgments

- Built with [Google Drive API](https://developers.google.com/drive)
- PDF processing powered by [PyPDF2](https://pypdf2.readthedocs.io/)
- Title pages created with [ReportLab](https://www.reportlab.com/)

---
