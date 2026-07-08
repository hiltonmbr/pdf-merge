import io

import pytest
from reportlab.pdfgen import canvas


def _make_pdf_bytes(text: str) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(100, 750, text)
    c.save()
    return buf.getvalue()


@pytest.fixture
def cv_tree(tmp_path):
    """Builds:
    tmp_path/
      01 - Section A/
        doc_a1.pdf
        doc_a2.pdf
      02 - Section B/
        doc_b1.pdf
      .hidden/
        ignored.pdf
    Returns tmp_path.
    """
    section_a = tmp_path / '01 - Section A'
    section_a.mkdir()
    (section_a / 'doc_a1.pdf').write_bytes(_make_pdf_bytes('a1'))
    (section_a / 'doc_a2.pdf').write_bytes(_make_pdf_bytes('a2'))

    section_b = tmp_path / '02 - Section B'
    section_b.mkdir()
    (section_b / 'doc_b1.pdf').write_bytes(_make_pdf_bytes('b1'))

    hidden = tmp_path / '.hidden'
    hidden.mkdir()
    (hidden / 'ignored.pdf').write_bytes(_make_pdf_bytes('ignored'))

    return tmp_path
