# GitHub Downloader Script Description:
# This script allows users to download files or folders from GitHub repositories.
# It parses the provided GitHub URL to determine if it points to a file
# or a folder, and then downloads the specified file to a local directory.
# Dependencies:
# requests: For making HTTP requests to download files.
# tqdm: For displaying a progress bar during the download process.
# os: For handling file paths and directories.
# Developer: Arbab Gul
# Date: 01/06/2025
# Thanks for using this script! If you have any issues or suggestions, feel free to reach out.

from urllib.parse import urlparse
import os
import requests
from tqdm import tqdm

def parse_github_url(url):
    parsed = urlparse(url)
    path_parts = parsed.path.strip('/').split('/')

    if len(path_parts) < 3:
        print("❌ Invalid URL format")
        return None
    
    owner = path_parts[0]
    repo = path_parts[1]
    
    if 'blob' in path_parts:
        branch_idx = path_parts.index('blob') + 1
        branch = path_parts[branch_idx]
        file_path = '/'.join(path_parts[branch_idx+1:])
        return {
            'type': 'file',
            'owner': owner,
            'repo': repo,
            'branch': branch,
            'path': file_path
        }
    elif 'tree' in path_parts:
        branch_idx = path_parts.index('tree') + 1
        branch = path_parts[branch_idx]
        folder_path = '/'.join(path_parts[branch_idx+1:])
        return {
            'type': 'folder',
            'owner': owner,
            'repo': repo,
            'branch': branch,
            'path': folder_path
        }
    else:  
        return {
            'type': 'folder',
            'owner': owner, 
            'repo': repo, 
            'branch': 'main', 
            'path': ''
        }

def FileDown(url,path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(path, 'wb') as f, tqdm(
            desc=path,
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                bar.update(len(chunk))
                downloaded += len(chunk)
                if total_size > 0:
                    progress = (downloaded / total_size) * 100
                    print(f"Downloading ↓↓↓ : {progress:.1f}%", end='\r')
        print("\n✅ File downloaded successfully")
        if total_size <= 0 and bar.n != total_size:
            print("⚠️ Download incomplete - file size mismatch")
        else:
            return True
    
    except Exception as e:
        print(f"\n❌ Error downloading file: {e}")
        return False


def FolderDown(owner, repo, branch, folder_path, path):
    try:
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{folder_path}?ref={branch}"
        response = requests.get(api_url)
        response.raise_for_status()

        items = response.json()
        if not isinstance(items, list):
            print("❌ Path is not a directory")
            return False
        os.makedirs(path, exist_ok=True)
        for item in items:
            item_path = os.path.join(path, item['name'])
            if item['type'] == 'file':
                print(f"Downloading file: {item['name']}")
                if not FileDown(item['download_url'], item_path):
                    return False
            elif item['type'] == 'dir':
                print(f"Processing subfolder: {item['name']}")
                if not FolderDown(owner, repo, branch, f"{folder_path}/{item['name']}", os.path.join(path, item['name'])):
                    return False
        print("✅ Folder downloaded successfully")
        return True
    except Exception as e:
        print(f"❌ Error downloading folder: {e}")
        return False

def main():
    print("\n                                          GitHub Downloader ")
    print("                      ---------  Download files or folders from GitHub  ---------")
    print("                                 ------- Developed by: Arbab Gul ------- ")
    
    # Get GitHub URL
    while True:
        github_url = input("\nEnter GitHub URL: ").strip()
        if github_url.startswith(('https://github.com/', 'http://github.com/')):
            break
        print("📌 Please enter a valid GitHub URL")

    # parse URL
    url_info = parse_github_url(github_url)
    if not url_info:
        print("❌ Could not parse GitHub URL..")
        return
    
    
    # Download Path name
    default_dir = os.path.join(os.getcwd(), "GitDownloads")
    new_dir = input(f"📂 Enter destination directory (leave blank for {default_dir}): ").strip()
    destination_path = os.path.abspath(new_dir) if new_dir else default_dir
    os.makedirs(destination_path, exist_ok=True)
    print(f"Destination directory: {destination_path}")

    if url_info['type'] == 'file':
        print(f"📄 Downloading file: {url_info['path']} from {url_info['owner']}/{url_info['repo']} at branch {url_info['branch']}")
        file_name = os.path.basename(url_info['path'])
        save_path = os.path.join(destination_path, file_name)
        raw_url = f"https://raw.githubusercontent.com/{url_info['owner']}/{url_info['repo']}/{url_info['branch']}/{url_info['path']}"
        print(f"Downloading file from: {raw_url}")

        if FileDown(raw_url, save_path):
            print(f"✅ Successfully downloaded to {save_path}")
        else:
            print("❌ Failed to download file")
    else:
        # Download folder
        print(f"\nDownloading folder: {url_info['path'] or 'root'}")
        folder_name = os.path.basename(url_info['path']) if url_info['path'] else url_info['repo']
        save_path = os.path.join(destination_path, folder_name)
        
        if FolderDown(url_info['owner'], url_info['repo'], 
                         url_info['branch'], url_info['path'], save_path):
            print(f"✅ Folder saved to: {save_path}")
        else:
            print("❌ Failed to download folder")

if __name__ == "__main__":
    while True:
        try:
            main()
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")