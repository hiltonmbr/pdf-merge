import os
from dotenv import load_dotenv


load_dotenv()

SOURCE = os.getenv('SOURCE_FOLDER_ID')
DESTINATION = os.getenv('DESTINATION_FOLDER_ID')
MERGED_PDF_NAME = os.getenv('MERGED_PDF_NAME', 'Complete_Curriculum_Vitae.pdf')
PUBLIC_DESTINATION = os.getenv('PUBLIC_DESTINATION', 'no')

if not SOURCE or not DESTINATION:
    raise ValueError(
        "Missing required environment variables!\n"
        "Please create a .env file with:\n"
        "  SOURCE_FOLDER_ID=your_folder_id\n"
        "  DESTINATION_FOLDER_ID=your_folder_id"
    )

PUBLIC_ACCESS = {
    'type': 'anyone',
    'role': 'reader'
}
