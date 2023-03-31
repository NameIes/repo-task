"""Download files from repository and calculate them hashes."""

import asyncio
import hashlib
import urllib
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


def is_folder(dom_object):
    """Check if dom object is folder.

    Args:
        dom_object (soup): beautiful soup finded object.

    Returns:
        bool: True if folder. False if not folder.
    """
    class_ = dom_object.find('svg', class_='octicon-file-directory-fill')
    return class_ is not None


def parse_file_urls(url):
    """Recursive parse all files in repository.

    Args:
        url (str): url to repository.

    Returns:
        list: list with all urls to files.
    """
    soup = BeautifulSoup(requests.get(url, timeout=5).text, 'html.parser')
    base_url = ''.join(['https://', urllib.parse.urlparse(url).netloc])

    urls = []
    files = soup.find_all('tr', class_='ready entry')
    for repo_file in tqdm(files):
        if is_folder(repo_file):
            urls += parse_file_urls(base_url + repo_file.find('a')['href'])
        else:
            urls.append(
                base_url + repo_file.find('a')['href'],
            )
    return urls


def parse_path(url):
    """Make path to file from url.

    Args:
        url (str): url to file.

    Returns:
        list: list of strings with folders and filename.
    """
    splitted = url.split('/')
    return splitted[splitted.index('master') + 1:]


def download_file(url):
    """Download file from url.

    Args:
        url (str): url to file.
    """
    download_url = url.replace('src', 'raw', 1)
    parsed_path = parse_path(url)
    download_path = '/'.join(['temp_repo'] + parsed_path[:-1])

    Path(download_path).mkdir(parents=True, exist_ok=True)

    filename = parsed_path[-1]
    responce = requests.get(download_url, timeout=5)

    if responce.status_code != 200:
        raise ValueError('Wrong url for download file.')

    with open('/'.join([download_path, filename]), 'wb') as repo_file:
        repo_file.write(
            responce.content,
        )


async def start_downloading(urls):
    """Start downloading task.

    Args:
        urls (list): list with urls of files.
    """
    pbar = tqdm(total=len(urls))
    for url in urls:
        download_file(url)
        pbar.update()
        await asyncio.sleep(0.1)


def print_hashes(urls):
    """Print hashes of downloaded files.

    Args:
        urls (list): urls of downloaded files.
    """
    print('{0:<32} {1:<64}'.format('File', 'SHA256 Hash'))
    paths = ['/'.join(parse_path(url)) for url in urls]
    for path in paths:
        with open(Path('temp_repo/', path), 'rb') as repo_file:
            file_hash = hashlib.sha256(repo_file.read()).hexdigest()
        print('{0:<32} {1:<64}'.format(path, file_hash))


async def main():
    """Download files from repo and calculate them hashes."""
    print('Parsing file urls of repository...')
    urls = parse_file_urls(
        'https://gitea.radium.group/radium/project-configuration/',
    )
    print(urls)
    print('Downloading files..')
    splitted_list = []
    for part in range(0, 3):
        splitted_list.append(urls[part::3])

    tasks = []
    for urls_part in splitted_list:
        tasks.append(start_downloading(urls_part))
    await asyncio.gather(*tasks)

    print('Files downloaded. Calculating hashes...')
    print_hashes(urls)


if __name__ == '__main__':
    asyncio.run(main())
