import os

from dotenv import load_dotenv

load_dotenv()

CV_PATH = os.getenv('CV_PATH')
OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'Curriculum Vitae Compilado')
MERGED_PDF_NAME = os.getenv('MERGED_PDF_NAME', 'cv_hilton.pdf')
