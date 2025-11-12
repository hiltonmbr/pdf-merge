import sys
import logging
from core.utils import *


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('pdf_merger.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


def main():
    """
    Main function that orchestrates the download, merge, and upload of PDFs.

    Workflow:
    1. Authenticates with Google Drive
    2. Scans for subfolders in SOURCE folder
    3. Downloads PDFs from each subfolder
    4. Creates a title page for each subfolder
    5. Merges all PDFs into a single document
    6. Uploads to DESTINATION folder
    """
    try:
        logger.info("=" * 60)
        logger.info("AUTO DOSSIER - PDF Merger with Subfolders")
        logger.info("=" * 60)

        logger.info("\n📝 Step 1: Authenticating with Google Drive...")
        service = google_auth()
        logger.info("✓ Authentication completed\n")

        logger.info("📥 Step 2: Scanning subfolders and downloading PDFs...")
        sections = download_files_with_subfolders(service, SOURCE)

        if not sections:
            logger.error("❌ No sections or files were found.")
            logger.error("Make sure:")
            logger.error("  1. The SOURCE folder ID is correct")
            logger.error("  2. The folder contains subfolders with PDF files")
            logger.error("  3. You have access to the folder")
            return

        total_pdfs = sum(len(pdfs) for _, pdfs in sections)
        logger.info(f"\n✓ Download complete:")
        logger.info(f"  • Sections found: {len(sections)}")
        logger.info(f"  • Total PDFs: {total_pdfs}")
        logger.info(f"  • Section breakdown:")
        for title, pdfs in sections:
            logger.info(f"    - {title}: {len(pdfs)} PDFs")

        logger.info("\n🔄 Step 3: Merging PDFs with title pages...")
        final_pdf = merge_files(sections)
        logger.info("✓ Merge completed\n")

        logger.info("☁️  Step 4: Uploading merged PDF to Google Drive...")
        link = upload_pdf(service, final_pdf, MERGED_PDF_NAME, DESTINATION)

        logger.info("\n" + "=" * 60)
        logger.info("✅ PROCESS COMPLETED SUCCESSFULLY!")
        logger.info("=" * 60)
        logger.info(f"📄 File: {MERGED_PDF_NAME}")
        logger.info(f"📊 Total sections: {len(sections)}")
        logger.info(f"📚 Total PDFs merged: {total_pdfs}")
        logger.info(f"🔗 Public link: {link}")
        logger.info("=" * 60 + "\n")

    except FileNotFoundError as e:
        logger.error(f"\n❌ File not found: {e}")
        logger.error("Make sure you have the required configuration files:")
        logger.error("  • credentials.json - OAuth credentials")
        logger.error("  • .env - Environment variables with folder IDs")
        sys.exit(1)

    except HttpError as e:
        logger.error(f"\n❌ Google Drive API error: {e}")
        logger.error("Check:")
        logger.error("  • Folder IDs are correct in .env file")
        logger.error("  • You have access to the folders")
        logger.error("  • Google Drive API is enabled")
        sys.exit(1)

    except Exception as e:
        logger.error(f"\n❌ Unexpected error: {e}", exc_info=True)
        logger.error(
            "\nFor detailed error information, check 'pdf_merger.log'")
        sys.exit(1)


if __name__ == '__main__':
    main()
