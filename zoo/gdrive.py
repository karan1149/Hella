"""Downloading of large public files from Google Drive.

Reference: https://stackoverflow.com/a/39225039
Adapted for python3: Credit Ethan li
"""
import math
import requests
from tqdm import tqdm


CHUNK_SIZE = 32768
URL = 'https://docs.google.com/uc?export=download'


def download_file_from_google_drive(id, destination):
    """Download a public file using its Google Drive id to the specified destination."""
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value

        return None

    def save_response_content(response, destination):

        total_size = int(response.headers.get('content-length', 0))
        with open(destination, 'wb') as f:
            for chunk in tqdm(
                    response.iter_content(CHUNK_SIZE),
                    total=int(math.ceil(total_size // CHUNK_SIZE)), unit=' MB',
                    unit_scale=True, unit_divisor=(CHUNK_SIZE // 1024)
            ):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)

    session = requests.Session()

    response = session.get(URL, params={'id': id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {'id': id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    save_response_content(response, destination)


if __name__ == '__main__':
    import sys
    if len(sys.argv) is not 3:
        print('Usage: python -m gdrive drive_file_id destination_file_path')
    else:
        # TAKE ID FROM SHAREABLE LINK
        file_id = sys.argv[1]
        # DESTINATION FILE ON YOUR DISK
        destination = sys.argv[2]
        download_file_from_google_drive(file_id, destination)
