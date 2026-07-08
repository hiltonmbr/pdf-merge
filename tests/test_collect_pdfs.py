from core.utils import collect_pdfs

from .conftest import _make_pdf_bytes


def test_happy_path_returns_sections_in_order(cv_tree):
    sections = collect_pdfs(cv_tree)

    assert [title for title, _ in sections] == ['01 - SECTION A', '02 - SECTION B']
    assert len(sections[0][1]) == 2
    assert len(sections[1][1]) == 1


def test_hidden_folders_are_excluded(cv_tree):
    sections = collect_pdfs(cv_tree)

    titles = [title for title, _ in sections]
    assert '.HIDDEN' not in titles
    assert not any('hidden' in title.lower() for title in titles)


def test_empty_base_dir_returns_empty_list(tmp_path):
    assert collect_pdfs(tmp_path) == []


def test_folder_with_no_pdfs_is_skipped(tmp_path):
    empty_section = tmp_path / '01 - Empty'
    empty_section.mkdir()
    (empty_section / 'notes.txt').write_text('not a pdf')

    real_section = tmp_path / '02 - Real'
    real_section.mkdir()
    (real_section / 'doc.pdf').write_bytes(_make_pdf_bytes('a'))

    sections = collect_pdfs(tmp_path)

    titles = [title for title, _ in sections]
    assert '01 - EMPTY' not in titles
    assert '02 - REAL' in titles


def test_exclude_dir_is_skipped_by_path(tmp_path):
    output_folder = tmp_path / 'Curriculum Vitae Compilado'
    output_folder.mkdir()
    # no file inside it yet — this is the first-run case the old
    # file-sniffing heuristic could not handle

    real_section = tmp_path / '01 - Section A'
    real_section.mkdir()
    (real_section / 'doc.pdf').write_bytes(_make_pdf_bytes('a'))

    sections = collect_pdfs(tmp_path, exclude_dir=output_folder)

    titles = [title for title, _ in sections]
    assert 'CURRICULUM VITAE COMPILADO' not in titles
    assert '01 - SECTION A' in titles


def test_no_exclude_dir_includes_everything_with_pdfs(tmp_path):
    section = tmp_path / '01 - Section A'
    section.mkdir()
    (section / 'doc.pdf').write_bytes(_make_pdf_bytes('a'))

    sections = collect_pdfs(tmp_path)  # exclude_dir defaults to None

    assert [title for title, _ in sections] == ['01 - SECTION A']


def test_sections_sorted_numerically_not_lexicographically(tmp_path):
    for name in ['10 - Ten', '2 - Two', '1 - One', '9 - Nine']:
        folder = tmp_path / name
        folder.mkdir()
        (folder / 'doc.pdf').write_bytes(_make_pdf_bytes(name))

    sections = collect_pdfs(tmp_path)

    titles = [title for title, _ in sections]
    assert titles == ['1 - ONE', '2 - TWO', '9 - NINE', '10 - TEN']
