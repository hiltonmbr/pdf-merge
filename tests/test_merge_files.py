import io

from pypdf import PdfReader

from core.utils import collect_pdfs, merge_files

from .conftest import _make_pdf_bytes


def test_page_count_covers_content_and_blank_separators(cv_tree):
    sections = collect_pdfs(cv_tree)

    result = merge_files(sections)

    reader = PdfReader(result)
    # 2 covers + (2 + 1) content pages + 1 blank separator between sections
    assert len(reader.pages) == 6


def test_empty_sections_list_returns_valid_empty_pdf():
    result = merge_files([])

    reader = PdfReader(result)
    assert len(reader.pages) == 0


def test_corrupt_pdf_in_section_does_not_abort_merge():
    valid = ('valid.pdf', io.BytesIO(_make_pdf_bytes('valid')))
    corrupt = ('corrupt.pdf', io.BytesIO(b'not a pdf'))
    sections = [('SECTION A', [valid, corrupt])]

    result = merge_files(sections)

    reader = PdfReader(result)
    # cover page + the one valid content page; the corrupt entry is skipped
    assert len(reader.pages) == 2


def test_merge_files_adds_one_outline_entry_per_section(cv_tree):
    sections = collect_pdfs(cv_tree)

    result = merge_files(sections)

    reader = PdfReader(result)
    titles = [item.title for item in reader.outline]

    assert titles == [title for title, _ in sections]
