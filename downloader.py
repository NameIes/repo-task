import requests, urllib, asyncio, hashlib
from tqdm import tqdm
from pathlib import Path
from bs4 import BeautifulSoup as bs


def is_folder(dom_object):
    if dom_object.find('svg', class_='octicon-file-directory-fill') is not None:
        return True
    return False


def parse_file_urls(url):
    page = requests.get(url)
    soup = bs(page.text, "html.parser")
    base_url = 'https://' + urllib.parse.urlparse(url).netloc

    result = []
    files = soup.find_all('tr', class_='ready entry')
    for file in tqdm(files):
        if not is_folder(file):
            result.append(
                base_url + file.find('a')['href']
            )
        else:
            result += parse_file_urls(base_url + file.find('a')['href'])
    return result


def parse_path(url):
    splitted = url.split('/')
    return splitted[splitted.index('master') + 1:]


def download_file(url):
    download_url = url.replace('src', 'raw', 1)
    parsed_path = parse_path(url)
    download_path = '/'.join(['temp_repo'] + parsed_path[:-1])

    Path(download_path).mkdir(parents=True, exist_ok=True)

    filename = parsed_path[-1]
    urllib.request.urlretrieve(download_url, download_path + '/' + filename)


def split_list(lst, n=3):
    k, m = divmod(len(lst), n)
    return (lst[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))


async def start_downloading(urls):
    pbar = tqdm(total=len(urls))
    for url in urls:
        download_file(url)
        pbar.update()
        await asyncio.sleep(.1)


async def main():
    REPO_URL = 'https://gitea.radium.group/radium/project-configuration/'
    print('Parsing file urls of repository...')
    urls = parse_file_urls(REPO_URL)

    print('Downloading files..')
    tasks = []
    for urls_part in split_list(urls):
        tasks.append(
            start_downloading(urls_part)
        )
    await asyncio.gather(*tasks)

    print('Files downloaded. Calculating hashes...')
    print('{:<32} {:<64}'.format('File', 'SHA256 Hash'))
    paths = ['/'.join(parse_path(url)) for url in urls]
    for path in paths:
        with open('temp_repo/' + path, 'rb') as file:
            file_hash = hashlib.sha256(file.read()).hexdigest()
        print(f'{path:<32} {file_hash:<64}')


if __name__ == "__main__":
    asyncio.run(main())
