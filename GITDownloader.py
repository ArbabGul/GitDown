import requests
import os
from progress.bar import IncrementalBar

RED = "\033[0;31m"
GREEN = "\033[0;32m"
BLUE = "\033[0;34m"
BOLD = "\033[1m"
END = "\033[0m"

def banner():
    print(fr'''{GREEN}
    ██████╗ ██╗████████╗    ██████╗  ██████╗ ██╗    ██╗███╗   ██╗██╗      ██████╗  █████╗ ██████╗ ███████╗██████╗ 
    ██╔════╝ ██║╚══██╔══╝    ██╔══██╗██╔═══██╗██║    ██║████╗  ██║██║     ██╔═══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗
    ██║  ███╗██║   ██║       ██║  ██║██║   ██║██║ █╗ ██║██╔██╗ ██║██║     ██║   ██║███████║██║  ██║█████╗  ██████╔╝
    ██║   ██║██║   ██║       ██║  ██║██║   ██║██║███╗██║██║╚██╗██║██║     ██║   ██║██╔══██║██║  ██║██╔══╝  ██╔══██╗
    ╚██████╔╝██║   ██║       ██████╔╝╚██████╔╝╚███╔███╔╝██║ ╚████║███████╗╚██████╔╝██║  ██║██████╔╝███████╗██║  ██║
    ╚═════╝ ╚═╝   ╚═╝       ╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝
                        This script allows users to download files or folders from GitHub repositories.
                                            Auther: Arbab Gul
                                                Version: v3.0{END}''')
    
class GitDownloader:
    
    @staticmethod
    def github_url_parser(url):
        path_parts = url.split('/')

        if len(path_parts) < 3:
            print(f"❌{RED} Invalid URL format{END}")
            exit(1)
        
        owner = path_parts[3]
        repo = path_parts[4]

        if 'blob' in path_parts:
            branch_index = path_parts.index('blob') + 1
            branch = path_parts[branch_index]
            file_path = '/'.join(path_parts[branch_index+1:])
            return {
                'type': 'file',
                'owner': owner,
                'repo': repo,
                'branch': branch,
                'path': file_path
            }
        elif 'tree' in path_parts:
            branch_index = path_parts.index('tree') + 1
            branch = path_parts[branch_index]
            folder_path = '/'.join(path_parts[branch_index+1:])
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

    @staticmethod
    def FileDownload(url,path):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            file_size = int(response.headers.get('content-length', 0))

            # Create progress bar
            bar = IncrementalBar(f'{GREEN}📥 Downloading..', max=file_size, suffix='%(percent)d%% [%(elapsed_td)s / %(eta_td)s]')
            
            with open(path, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        bar.next(len(chunk))
                bar.finish()

            print(f"✅{END}{GREEN} File saved to: {os.path.abspath(path)}{END}")
        except Exception as e:
            print(f"❌{END}{RED} Download failed: {e}{END}")
            exit()

    @staticmethod
    def FolderDownload(owner, repo, branch, folder_path, path):
        try:
            api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{folder_path}?ref={branch}"
            response = requests.get(api_url,stream=True)
            response.raise_for_status()

            items = response.json()
            if not isinstance(items, list):
                print("❌{RED} Path is not a directory{END}")
                exit()

            os.makedirs(path,exist_ok=True)
            for item in items:
                item_path = os.path.join(path, item['name'])
                if item['type'] == 'file':
                    GitDownloader.FileDownload(item['download_url'],item_path)
                elif item['type'] == 'dir':
                    GitDownloader.FolderDownload(owner, repo, branch, f"{folder_path}/{item['name']}", os.path.join(path, item['name']))

        except Exception as e:
            print(f"❌{RED} Error downloading folder: {e}{END}")
            exit()
            
def main():
    banner()
    github_url = input(f"{BLUE}🔗 Enter Github URL: {END}")
    if not github_url.startswith(('https://github.com/','http://github.com/')):
        print(f"📌{RED} Please enter a valid GitHub URL{END}")
        exit()

    url_info = GitDownloader.github_url_parser(github_url)
    if not url_info:
        print(f"❌{RED} Could not parse GitHub URL..{END}")
        exit()


    # File handlings
    default_dir = os.path.join(os.getcwd(), "GitDownloads")
    new_dir = input(f"📂{BLUE} Enter destination directory (leave blank for {default_dir}): {END}").strip()
    destination_path = os.path.join(os.getcwd(),new_dir) if new_dir else default_dir
    os.makedirs(destination_path, exist_ok=True)

    if url_info['type'] == 'file':
        print(f"📄{BOLD} Downloading file: {url_info['path']} from {url_info['owner']}/{url_info['repo']} at branch {url_info['branch']}{END}")
        file_name = os.path.basename(url_info['path'])
        save_path = os.path.join(destination_path, file_name)
        raw_url = f"https://raw.githubusercontent.com/{url_info['owner']}/{url_info['repo']}/{url_info['branch']}/{url_info['path']}"

        GitDownloader.FileDownload(raw_url, save_path)
    else:
        # Download folder
        folder_name = os.path.basename(url_info['path']) if url_info['path'] else url_info['repo']
        save_path = os.path.join(destination_path, folder_name)
        
        GitDownloader.FolderDownload(url_info['owner'], url_info['repo'], url_info['branch'], url_info['path'], save_path)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"{BOLD}\n Program Close. GoodBye..{END}")
        exit()