"""Tests for downloader."""

import downloader
from hashlib import sha256
from asyncio import run

import pytest
from bs4 import BeautifulSoup


pytest_plugins = ('pytest_asyncio', )

def test_is_folder():
    """Test is_folder function."""
    dom_object_folder = BeautifulSoup("""
        <td class="name four wide">
            <span class="truncate">
                <svg class="svg octicon-file-directory-fill"></svg>
            </span>
        </td>
    """, 'html.parser')

    dom_object_file = BeautifulSoup("""
        <td class="name four wide">
            <span class="truncate"></span>
        </td>
    """, 'html.parser')

    assert downloader.is_folder(dom_object_folder) == True
    assert downloader.is_folder(dom_object_file) == False


def test_parse_urls():
    """Test parse_file_urls function."""
    repo_url = 'https://gitea.radium.group/radium/project-configuration/'
    urls = downloader.parse_file_urls(repo_url)

    good_result = [
        'https://gitea.radium.group/radium/project-configuration/src/branch/master/nitpick/all.toml',
        'https://gitea.radium.group/radium/project-configuration/src/branch/master/nitpick/darglint.toml',
        'https://gitea.radium.group/radium/project-configuration/src/branch/master/nitpick/editorconfig.toml',
        'https://gitea.radium.group/radium/project-configuration/src/branch/master/nitpick/file-structure.toml',
        'https://gitea.radium.group/radium/project-configuration/src/branch/master/nitpick/flake8.toml',
        'https://gitea.radium.group/radium/project-configuration/src/branch/master/nitpick/isort.toml',
        'https://gitea.radium.group/radium/project-configuration/src/branch/master/nitpick/pytest.toml',
        'https://gitea.radium.group/radium/project-configuration/src/branch/master/nitpick/styleguide.toml',
        'https://gitea.radium.group/radium/project-configuration/src/branch/master/LICENSE',
        'https://gitea.radium.group/radium/project-configuration/src/branch/master/README.md']

    assert urls != []
    assert urls == good_result


def test_parse_path():
    """Test parse_path function."""
    good_url = 'https://gitea.radium.group/master/README.md'
    wrong_url = 'https://google.com/'

    assert downloader.parse_path(good_url) == ['README.md']
    with pytest.raises(ValueError):
        downloader.parse_path(wrong_url)


def test_dowload_file():
    """Test download_file function."""
    downloader.download_file(
        'https://gitea.radium.group/radium/project-configuration/src/branch/master/README.md',
    )

    good_readme_hash = '8cf77a685a9b2b729f3b3ff4941e5efdbd07888ccfa96923fd1036dffe25314f'
    with open('temp_repo/README.md', 'rb') as readme_file:
        readme_hash = sha256(readme_file.read()).hexdigest()

    assert good_readme_hash == readme_hash
    with pytest.raises(ValueError):
        downloader.download_file(
            'https://gitea.radium.group/radium/project-configuration/src/branch/master/RME.md',
        )


@pytest.mark.asyncio
async def test_start_downloading():
    """Test start_downloading function."""
    good_urls = [
        'https://gitea.radium.group/radium/project-configuration/src/branch/master/LICENSE',
        'https://gitea.radium.group/radium/project-configuration/src/branch/master/README.md',]

    wrong_urls = [
        'https://this.site.is.not.exist',
        'https://this.site.is.not.exist.too',
    ]

    await downloader.start_downloading(good_urls)

    with pytest.raises(ValueError):
        await downloader.start_downloading(wrong_urls)


def test_print_hashes():
    """Test print_hashes function."""
    wrong_urls = [
        'https://this.site.is.not.exist',
        'https://this.site.is.not.exist.too',
    ]

    wrong_urls_2 = [
        'https://gitea.radium.group/master/qwe',
        'https://gitea.radium.group/master/asd',
    ]

    with pytest.raises(ValueError):
        downloader.print_hashes(wrong_urls)

    with pytest.raises(OSError):
        downloader.print_hashes(wrong_urls_2)


@pytest.mark.asyncio
async def test_main():
    """Test main function."""
    good_hashes = [
        '700f111c1037259067f406c063c3286d1a32e76b9106931bd931ead61975c100',
        'e9d9941a4f06cacbfb2df1c9ede98db32177ef2a1c641324a46f573a8953ff64',
        '7e94c7f4bdfb46be0781c3d734da8389b921254b8fbaad261297cf09d4120383',
        '92441118662c296b3a385be8950681bbf0a6795ccd7d854106f3c69dd39c6234',
        '3f9995629450d6c4d40abd79c5be785cf6a665de48b7688994f17135e03562ae',
        'ef2258e7bbbbf51e3bd1012c23a0006233babca23d5c6bf38bad689d8f2f92e1',
        '3830c00d8141fa6b3409abffd357a9caaab54953f0dbacafc3a9fc9b9ceaae98',
        'c6c1eaf9d2a84a02474221969810f8485278eaef4653e9db2f1220f0989d556d',
        'f2ec607f67bb0dd3053b49835b02110d5cd0f8eb6da3aac4dc0b142a6b299be9',
        '8cf77a685a9b2b729f3b3ff4941e5efdbd07888ccfa96923fd1036dffe25314f',
    ]

    paths = [
        'temp_repo/nitpick/all.toml',
        'temp_repo/nitpick/darglint.toml',
        'temp_repo/nitpick/editorconfig.toml',
        'temp_repo/nitpick/file-structure.toml',
        'temp_repo/nitpick/flake8.toml',
        'temp_repo/nitpick/isort.toml',
        'temp_repo/nitpick/pytest.toml',
        'temp_repo/nitpick/styleguide.toml',
        'temp_repo/LICENSE',
        'temp_repo/README.md',
    ]

    await downloader.main()

    for index, path in enumerate(paths):
        with open(path, 'rb') as repo_file:
            file_hash = sha256(repo_file.read()).hexdigest()

        assert good_hashes[index] == file_hash
