import io
import logging
import re
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

logger = logging.getLogger(__name__)


def _natural_sort_key(path: Path) -> tuple:
    return tuple(
        int(chunk) if chunk.isdigit() else chunk.lower() for chunk in re.split(r'(\d+)', path.name)
    )


def collect_pdfs(
    base_path: str | Path, exclude_dir: str | Path | None = None
) -> list[tuple[str, list[tuple[str, io.BytesIO]]]]:
    base = Path(base_path)
    sections = []

    resolved_exclude = Path(exclude_dir).resolve() if exclude_dir else None

    entries = sorted(
        (
            e
            for e in base.iterdir()
            if e.is_dir()
            and not e.name.startswith('.')
            and (resolved_exclude is None or e.resolve() != resolved_exclude)
        ),
        key=_natural_sort_key,
    )

    if not entries:
        logger.warning('Nenhuma subpasta encontrada em %s', base)
        return sections

    for folder in entries:
        logger.info(f'\n{"=" * 60}')
        logger.info(f'📂 {folder.name}')
        logger.info(f'{"=" * 60}')

        pdfs = sorted(folder.glob('*.pdf'))
        if not pdfs:
            logger.warning(f'  ⚠️  Nenhum PDF em {folder.name}')
            continue

        pdf_data: list[tuple[str, io.BytesIO]] = []
        for pdf_path in pdfs:
            size_kb = pdf_path.stat().st_size / 1024
            logger.info(f'  📄 {pdf_path.name} ({size_kb:.0f} KB)')
            pdf_data.append((pdf_path.name, io.BytesIO(pdf_path.read_bytes())))

        sections.append((folder.name.upper(), pdf_data))
        logger.info(f'  ✓ {len(pdf_data)} PDF(s) coletados')

    return sections


def create_page(title: str) -> PdfReader:
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    width, height = A4

    styles = getSampleStyleSheet()
    style = styles['Title']
    style.fontSize = 24
    style.leading = 30
    style.textColor = colors.HexColor('#1a1a1a')
    style.alignment = 1

    p = Paragraph(title, style)
    _, h = p.wrap(width - 100, height)
    p.drawOn(can, 50, height - h - 150)

    can.showPage()
    can.save()
    packet.seek(0)

    return PdfReader(packet)


def merge_files(sections: list[tuple[str, list[tuple[str, io.BytesIO]]]]) -> io.BytesIO:
    writer = PdfWriter()
    total_pages = 0

    logger.info(f'\n{"=" * 60}')
    logger.info('🔗 Iniciando merge')
    logger.info(f'Total de seções: {len(sections)}')
    logger.info(f'{"=" * 60}\n')

    for idx, (title, pdfs) in enumerate(sections, 1):
        logger.info(f'[{idx}/{len(sections)}] {title}')

        try:
            cover_page_index = total_pages
            cover = create_page(title)
            writer.add_page(cover.pages[0])
            total_pages += 1
            writer.add_outline_item(title, cover_page_index)
        except Exception as e:
            logger.error(f'  ✗ Erro ao criar capa para "{title}": {e}')

        section_pages = 0
        for name, pdf_io in pdfs:
            pdf_io.seek(0)
            try:
                reader = PdfReader(pdf_io)
                for page in reader.pages:
                    writer.add_page(page)
                    total_pages += 1
                    section_pages += 1
            except Exception as e:
                logger.error(f'  ✗ Erro ao processar {name}: {e}')

        logger.info(f'  ✓ {section_pages} página(s) adicionadas')
        logger.info('')

        if idx < len(sections):
            writer.add_blank_page()
            total_pages += 1

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)

    logger.info(f'{"=" * 60}')
    logger.info(f'✅ Merge concluído — {total_pages} páginas no total')
    logger.info(f'{"=" * 60}\n')

    return output


def save_pdf(pdf_stream: io.BytesIO, output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf_stream.seek(0)
    output_path.write_bytes(pdf_stream.getvalue())
    size_mb = output_path.stat().st_size / (1024 * 1024)
    logger.info(f'💾 Salvo em: {output_path} ({size_mb:.2f} MB)')
    return output_path
