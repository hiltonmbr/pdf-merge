import os
import io
import logging
from typing import List, Tuple,  Dict
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from config import *


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive.file'
]


def google_auth():
    """
    Authenticates with Google Drive API using OAuth2.

    Returns:
        Resource: Authenticated Google Drive service

    Raises:
        FileNotFoundError: If credentials.json is not found

    Note:
        On first run, this will open a browser for authentication.
        Make sure you're added as a test user in Google Cloud Console:
        https://console.cloud.google.com/apis/credentials/consent
    """
    creds = None

    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            logger.info("Credentials loaded from token.json")
        except Exception as e:
            logger.warning(f"Error loading token.json: {e}")
            logger.info("Will re-authenticate...")
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                logger.info("Refreshing expired token...")
                creds.refresh(Request())
                logger.info("✓ Token refreshed successfully")
            except Exception as e:
                logger.error(f"Error refreshing token: {e}")
                logger.info("Will obtain new credentials...")
                creds = None

        if not creds:
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError(
                    "\n" + "="*60 + "\n"
                    "ERROR: 'credentials.json' file not found!\n"
                    "="*60 + "\n"
                    "Please follow these steps:\n\n"
                    "1. Go to: https://console.cloud.google.com/apis/credentials\n"
                    "2. Click 'CREATE CREDENTIALS' → 'OAuth client ID'\n"
                    "3. Application type: 'Desktop app'\n"
                    "4. Download the JSON file\n"
                    "5. Rename it to 'credentials.json'\n"
                    "6. Place it in the project root directory\n\n"
                    "Also make sure you're added as a test user at:\n"
                    "https://console.cloud.google.com/apis/credentials/consent\n"
                    "="*60
                )

            logger.info("Starting OAuth authentication flow...")
            logger.info("A browser window will open for authentication")
            logger.info(
                "If you see 'This app isn't verified', click 'Advanced' → 'Go to [app name] (unsafe)'")

            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
                logger.info("✓ Authentication completed successfully")
            except Exception as e:
                logger.error(f"Authentication failed: {e}")
                logger.error("\nCommon issues:")
                logger.error("1. Make sure you're added as a test user")
                logger.error("2. Check OAuth consent screen is configured")
                logger.error(
                    "3. Verify scopes are added: drive.file, drive.readonly")
                raise

        try:
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
            logger.info("✓ Token saved to token.json")
        except Exception as e:
            logger.warning(f"Could not save token: {e}")

    return build('drive', 'v3', credentials=creds)


def get_subfolders(service, parent_folder_id: str) -> List[Dict[str, str]]:
    """
    Gets all subfolders from a parent folder.

    Args:
        service: Authenticated Google Drive service
        parent_folder_id: Parent folder ID

    Returns:
        List of dictionaries with 'id' and 'name' keys
    """
    try:
        query = f"'{parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = service.files().list(
            q=query,
            fields="files(id, name)",
            orderBy="name"
        ).execute()

        subfolders = results.get('files', [])
        logger.info(f"Found {len(subfolders)} subfolders")

        return subfolders

    except HttpError as e:
        logger.error(f"Error listing subfolders: {e}")
        raise


def download_files_from_folder(service, folder_id: str, folder_name: str = "") -> List[Tuple[str, io.BytesIO]]:
    """
    Downloads all PDF files from a specific folder.

    Args:
        service: Authenticated Google Drive service
        folder_id: Google Drive folder ID
        folder_name: Optional folder name for logging

    Returns:
        List of tuples (filename, bytes_content) sorted by name
    """
    files = []
    log_prefix = f"[{folder_name}] " if folder_name else ""

    try:
        query = f"'{folder_id}' in parents and mimeType='application/pdf' and trashed=false"
        results = service.files().list(
            q=query,
            fields="files(id, name, size)",
            orderBy="name"
        ).execute()

        items = results.get('files', [])

        if not items:
            logger.warning(f"{log_prefix}No PDF files found")
            return files

        logger.info(f"{log_prefix}Found {len(items)} PDF files")

        for item in items:
            try:
                size_mb = int(item.get('size', 0)) / (1024 * 1024)
                logger.info(
                    f"{log_prefix}Downloading: {item['name']} ({size_mb:.2f} MB)")

                request = service.files().get_media(fileId=item['id'])
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)

                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        progress = int(status.progress() * 100)
                        logger.debug(f"{log_prefix}  Progress: {progress}%")

                fh.seek(0)
                files.append((item['name'], fh))
                logger.info(f"{log_prefix}  ✓ Downloaded successfully")

            except HttpError as e:
                logger.error(
                    f"{log_prefix}Error downloading {item['name']}: {e}")
            except Exception as e:
                logger.error(
                    f"{log_prefix}Unexpected error downloading {item['name']}: {e}")

    except HttpError as e:
        logger.error(f"{log_prefix}Error listing files: {e}")
        raise

    return sorted(files, key=lambda x: x[0])


def download_files_with_subfolders(service, parent_folder_id: str) -> List[Tuple[str, List[Tuple[str, io.BytesIO]]]]:
    """
    Downloads PDFs from parent folder and all subfolders.
    Each subfolder becomes a section with its own title page.

    Args:
        service: Authenticated Google Drive service
        parent_folder_id: Parent folder ID

    Returns:
        List of tuples (section_title, list_of_pdfs)
    """
    sections = []

    try:
        subfolders = get_subfolders(service, parent_folder_id)

        if not subfolders:
            logger.warning(
                "No subfolders found. Downloading from parent folder only.")
            pdfs = download_files_from_folder(
                service, parent_folder_id, "Root")
            if pdfs:
                sections.append(("DOCUMENTS", pdfs))
            return sections

        for subfolder in subfolders:
            folder_id = subfolder['id']
            folder_name = subfolder['name']

            logger.info(f"\n{'='*60}")
            logger.info(f"Processing subfolder: {folder_name}")
            logger.info(f"{'='*60}")

            pdfs = download_files_from_folder(service, folder_id, folder_name)

            if pdfs:
                section_title = folder_name.upper()
                sections.append((section_title, pdfs))
                logger.info(
                    f"✓ Section '{section_title}' ready with {len(pdfs)} PDFs")
            else:
                logger.warning(f"Skipping empty folder: {folder_name}")

        return sections

    except Exception as e:
        logger.error(f"Error processing subfolders: {e}")
        raise


def download_files(service, folder_id: str) -> List[Tuple[str, io.BytesIO]]:
    """
    Downloads all PDF files from a Google Drive folder (legacy function for backward compatibility).

    Args:
        service: Authenticated Google Drive service
        folder_id: Google Drive folder ID

    Returns:
        List of tuples (filename, bytes_content) sorted by name
    """
    return download_files_from_folder(service, folder_id)


def create_page(title: str) -> PdfReader:
    """
    Creates a cover page with centered title.

    Args:
        title: Title text

    Returns:
        PdfReader with the created page
    """
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    width, height = A4

    # Style configuration
    styles = getSampleStyleSheet()
    style = styles['Title']
    style.fontSize = 24
    style.leading = 30
    style.textColor = colors.HexColor("#1a1a1a")
    style.alignment = 1  # Centered

    # Create and draw paragraph
    p = Paragraph(title, style)
    _, h = p.wrap(width - 100, height)
    p.drawOn(can, 50, height - h - 150)

    can.showPage()
    can.save()
    packet.seek(0)

    return PdfReader(packet)


def merge_files(sections: List[Tuple[str, List[Tuple[str, io.BytesIO]]]]) -> io.BytesIO:
    """
    Merges multiple PDFs into a single file with separator pages.

    Args:
        sections: List of tuples (section_title, pdf_list)

    Returns:
        BytesIO containing the merged PDF
    """
    writer = PdfWriter()
    total_pages = 0

    logger.info(f"\n{'='*60}")
    logger.info(f"Starting PDF merge process")
    logger.info(f"Total sections: {len(sections)}")
    logger.info(f"{'='*60}\n")

    for idx, (title, pdfs) in enumerate(sections, 1):
        logger.info(f"[Section {idx}/{len(sections)}] Processing: {title}")

        try:
            cover = create_page(title)
            writer.add_page(cover.pages[0])
            total_pages += 1
            logger.info(f"  ✓ Cover page added")
        except Exception as e:
            logger.error(f"  ✗ Error creating cover page for '{title}': {e}")
            continue

        section_page_count = 0
        for name, pdf_io in pdfs:
            try:
                pdf_io.seek(0)
                reader = PdfReader(pdf_io)
                num_pages = len(reader.pages)

                logger.info(f"  Adding: {name} ({num_pages} pages)")

                for page in reader.pages:
                    writer.add_page(page)
                    total_pages += 1
                    section_page_count += 1

            except Exception as e:
                logger.error(f"  ✗ Error processing {name}: {e}")
                continue

        if idx < len(sections):
            writer.add_blank_page()
            total_pages += 1
            logger.info(
                f"  ✓ Section complete: {section_page_count} content pages")
            logger.info("")

    logger.info(f"{'='*60}")
    logger.info(f"✓ Merged PDF created with {total_pages} total pages")
    logger.info(f"{'='*60}\n")

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)

    return output


def upload_pdf(service, pdf_stream: io.BytesIO, file_name: str, folder_id: str) -> str:
    """
    Uploads a PDF to Google Drive and makes it public.
    If a file with the same name exists in the folder, it will be updated.

    Args:
        service: Authenticated Google Drive service
        pdf_stream: PDF stream
        file_name: File name
        folder_id: Destination folder ID

    Returns:
        Public URL of the file 
    """
    try:
        # Check if file already exists in the folder
        query = f"name='{file_name}' and '{folder_id}' in parents and trashed=false"
        results = service.files().list(
            q=query,
            fields="files(id, name)",
            spaces='drive'
        ).execute()

        existing_files = results.get('files', [])

        pdf_stream.seek(0)
        size_mb = len(pdf_stream.getvalue()) / (1024 * 1024)

        temp_file = f"temp_{file_name}"
        with open(temp_file, 'wb') as f:
            f.write(pdf_stream.getvalue())

        media = MediaFileUpload(
            temp_file,
            mimetype='application/pdf',
            resumable=True
        )

        if existing_files:
            file_id = existing_files[0]['id']
            logger.info(
                f"File '{file_name}' already exists. Updating... ({size_mb:.2f} MB)")

            file = service.files().update(
                fileId=file_id,
                media_body=media,
                fields='id, webViewLink'
            ).execute()

            logger.info(f"✓ PDF updated successfully!")
        else:
            logger.info(f"Uploading {file_name} ({size_mb:.2f} MB)...")

            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }

            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()

            logger.info(f"✓ PDF uploaded successfully!")

        if os.path.exists(temp_file):
            os.remove(temp_file)

        if PUBLIC_DESTINATION == 'yes':
            logger.info("Setting file permissions to public...")
            service.permissions().create(
                fileId=file['id'],
                body=PUBLIC_ACCESS
            ).execute()

        web_view_link = f"https://drive.google.com/file/d/{file['id']}/view?usp=sharing"
        logger.info(f"✓ File ID: {file['id']}")
        logger.info(f"✓ URL: {web_view_link}")

        return web_view_link

    except HttpError as e:
        logger.error(f"HTTP error during upload: {e}")
        logger.error("Make sure:")
        logger.error("1. The destination folder ID is correct")
        logger.error("2. You have write access to the folder")
        logger.error("3. You have enough storage space in Google Drive")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during upload: {e}")
        raise
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)
