import argparse
import logging
import sys
from pathlib import Path

from config import CV_PATH, MERGED_PDF_NAME, OUTPUT_DIR
from core.utils import collect_pdfs, merge_files, save_pdf

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('pdf_merger.log', encoding='utf-8'),
    ],
)
logger = logging.getLogger(__name__)


def resolve_cv_path(cli_path: str | None) -> Path:
    if cli_path:
        path = Path(cli_path).expanduser().resolve()
    elif CV_PATH:
        path = Path(CV_PATH).expanduser().resolve()
    else:
        path = Path.cwd()

    if not path.is_dir():
        logger.error('❌ Diretório não encontrado: %s', path)
        logger.error('Forneça um caminho válido com --cv-path ou via .env')
        sys.exit(1)

    return path


def resolve_output_dir(cli_dir: str | None, cv_path: Path) -> Path:
    if cli_dir:
        candidate = Path(cli_dir).expanduser()
    elif OUTPUT_DIR:
        candidate = Path(OUTPUT_DIR).expanduser()
    else:
        candidate = cv_path / 'Curriculum Vitae Compilado'

    if candidate.is_absolute():
        return candidate

    return (cv_path / candidate).resolve()


def main():
    parser = argparse.ArgumentParser(description='Mescla PDFs em um único documento')
    parser.add_argument(
        '--cv-path',
        help='Caminho da pasta com subpastas de PDFs (sobrescreve .env)',
    )
    parser.add_argument(
        '--output-dir',
        help='Subpasta ou caminho absoluto para salvar o PDF (sobrescreve .env)',
    )
    args = parser.parse_args()

    cv_path = resolve_cv_path(args.cv_path)
    output_dir = resolve_output_dir(args.output_dir, cv_path)
    output_path = output_dir / MERGED_PDF_NAME

    try:
        logger.info('=' * 60)
        logger.info('📄 PDF MERGE')
        logger.info('=' * 60)

        logger.info(f'\n📂 Coletando PDFs de: {cv_path}')
        sections = collect_pdfs(cv_path, exclude_dir=output_dir)

        if not sections:
            logger.error('❌ Nenhuma seção encontrada com PDFs.')
            return

        total_pdfs = sum(len(pdfs) for _, pdfs in sections)
        logger.info('\n✅ Coleta concluída:')
        logger.info(f'  • Seções: {len(sections)}')
        logger.info(f'  • PDFs:   {total_pdfs}')

        logger.info('\n🔗 Mesclando PDFs...')
        final_pdf = merge_files(sections)

        logger.info('\n💾 Salvando PDF final...')
        save_pdf(final_pdf, output_path)

        logger.info(f'\n{"=" * 60}')
        logger.info('✅ PROCESSO CONCLUÍDO!')
        logger.info('=' * 60)
        logger.info(f'📄 {output_path.name}')
        logger.info(f'📂 {output_path.parent}')
        logger.info(f'📊 {len(sections)} seções, {total_pdfs} PDFs')
        logger.info('=' * 60)

    except Exception as e:
        logger.error(f'\n❌ Erro inesperado: {e}', exc_info=True)
        logger.error('Consulte pdf_merger.log para detalhes.')
        sys.exit(1)


if __name__ == '__main__':
    main()
