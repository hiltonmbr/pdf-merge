import pytest

from main import resolve_cv_path, resolve_output_dir


def test_resolve_cv_path_with_explicit_cli_path(tmp_path):
    result = resolve_cv_path(str(tmp_path))

    assert result == tmp_path.resolve()


def test_resolve_cv_path_missing_dir_exits(tmp_path):
    missing = tmp_path / 'does-not-exist'

    with pytest.raises(SystemExit):
        resolve_cv_path(str(missing))


def test_resolve_output_dir_relative_resolves_against_cv_path(tmp_path):
    result = resolve_output_dir('Output Folder', tmp_path)

    assert result == (tmp_path / 'Output Folder').resolve()


def test_resolve_output_dir_absolute_returned_as_is(tmp_path):
    absolute = tmp_path / 'Somewhere Else'

    result = resolve_output_dir(str(absolute), tmp_path)

    assert result == absolute
