from logging import getLogger
from unittest.mock import Mock, patch

import pytest

from mkdocs_to_pdf.options import Options
from mkdocs_to_pdf.pdf_engines.chromium import ChromiumUtils

logger = getLogger(__name__)


class LocalOptions(Options):
    def __init__(self, local_config, config, logger):
        pass


def default_options():
    options = LocalOptions(None, None, None)
    options._logger = logger
    options.chrome_arguments = None
    options.chrome_extra_arguments = None
    options.headless_chrome_path = 'chromium-browser'
    return options


@pytest.fixture
def default_args_options():
    options = default_options()
    default_args = ChromiumUtils(options).get_args()
    return options, default_args


def test_get_args_overload(default_args_options):
    """
    Complete overload for arguments. None of the hardcoded args are used
    """
    options, default_args = default_args_options
    options.chrome_arguments = '--foo --bar'
    args = ChromiumUtils(options).get_args()
    assert args == '--foo --bar'.split()


def test_get_args_overload_and_extra(default_args_options):
    """
    Complete overload for arguments. None of the hardcoded args are used,
    and chrome_extra_arguments is ignored.
    """
    options, default_args = default_args_options
    options.chrome_arguments = '--foo --bar'
    options.chrome_extra_arguments = '--baz'
    args = ChromiumUtils(options).get_args()
    assert args == '--foo --bar'.split()


def test_get_args_append(default_args_options):
    """
    Additional arguments added after the ones that are hardcoded.
    """
    options, default_args = default_args_options
    options.chrome_extra_arguments = '--foo --bar'
    args = ChromiumUtils(options).get_args()
    assert args == default_args + '--foo --bar'.split()


@pytest.fixture
def get_default_options():
    options = default_options()
    return options


def test_default_browser(get_default_options):
    """
    Default browser
    """
    options = get_default_options

    with patch('subprocess.run') as mock_run:
        mock_run.return_value.stdout = 'Chromium Dummy x.y.z'
        path = ChromiumUtils(options).get_chromium_path()
        assert path == 'chromium-browser'


def test_linux_browser(get_default_options):
    """
    Chrome for Linux(rpm/deb installed)
    """
    options = get_default_options

    with (
        patch('subprocess.run') as mock_run,
        patch('platform.system', return_value='Linux'),
    ):
        mock_run.side_effect = [
            FileNotFoundError,
            Mock(stdout='Google Chrome a.b.c.d', returncode=0),
        ]
        obj = ChromiumUtils(options)
        path = obj.get_chromium_path()
        assert path == '/usr/bin/google-chrome'


def test_mac_browser(get_default_options):
    """
    Chrome for macOS
    """
    options = get_default_options

    with (
        patch('subprocess.run') as mock_run,
        patch('platform.system', return_value='Darwin'),
    ):
        mock_run.side_effect = [
            FileNotFoundError,
            Mock(stdout='Google Chrome a.b.c.d', returncode=0),
        ]
        obj = ChromiumUtils(options)
        path = obj.get_chromium_path()
        assert path == '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
