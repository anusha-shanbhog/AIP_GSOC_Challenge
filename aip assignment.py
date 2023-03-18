import os
import urllib.request
import datetime
import json
from urllib.parse import urlparse
from bs4 import BeautifulSoup


def download_blocklists():
    # Load the source URLs and offline folders from the JSON file
    try:
        with open('sources.json', 'r') as f:
            data = json.load(f)
            sources = data['sources']
            offline_folders = data['offline_folders']
    except Exception as e:
        print('Error retrieving sources:', e)
        return

    # Folder to store the blocklists
    blocklists_folder = 'blocklists_downloaded'

    # Create folder if it doesn't exist
    if not os.path.exists(blocklists_folder):
        os.mkdir(blocklists_folder)

    # Retrieve and store the latest blocklists for each source URL
    for source_url in sources:
        try:
            # Retrieve the source HTML
            response = urllib.request.urlopen(source_url)
            soup = BeautifulSoup(response, 'html.parser')

            # Define the sublinks array
            sublinks = []

            # Find all links with a CSV extension and add them to the sublinks array
            for link in soup.find_all('a'):
                href = link.get('href')
                if href.endswith('.csv'):
                    sublinks.append(href)

            # Retrieve and store the blocklists
            for sublink in sublinks:
                try:
                    # Generate the full URL for the sublink
                    source = urlparse(source_url + sublink).geturl()

                    # Retrieve the blocklist
                    response = urllib.request.urlopen(source)
                    data = response.read()

                    # Store the blocklist if it doesn't already exist
                    filename = datetime.datetime.now().strftime('%Y-%m-%d') + '-' + sublink
                    filepath = os.path.join(blocklists_folder, filename)
                    if not os.path.exists(filepath):
                        with open(filepath, 'wb') as f:
                            f.write(data)
                            print('Stored', filename)
                    else:
                        print('Skipping', sublink, 'as file already exists.')
                except Exception as e:
                    print('Error retrieving', source, ':', e)

        except Exception as e:
            print('Error retrieving', source_url, ':', e)

    # Retrieve and store any offline blocklists
    for offline_folder in offline_folders:
        if os.path.exists(offline_folder):
            for file in os.listdir(offline_folder):
                if file.endswith('.csv'):
                    try:
                        # Add the timestamp to the filename
                        timestamp = datetime.datetime.now().strftime('%Y-%m-%d')
                        filename = f"{timestamp}-{file}"

                        # Check if the file already exists in the blocklists folder
                        target_path = os.path.join(blocklists_folder, filename)
                        if os.path.exists(target_path):
                            print(f"Skipping {file} as file already exists.")
                        else:
                            # Copy the offline blocklist to the blocklists folder
                            source_path = os.path.join(offline_folder, file)
                            with open(source_path, 'rb') as source_file, open(target_path, 'wb') as target_file:
                                target_file.write(source_file.read())
                                print(f"Stored {filename}")
                    except Exception as e:
                        print(f"Error retrieving {source_path}: {e}")


if __name__ == '__main__':
    download_blocklists()
