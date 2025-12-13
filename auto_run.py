import subprocess
import datetime
import sys
import os
from git import Repo, GitCommandError
from git.exc import InvalidGitRepositoryError

def run_command(command, description):
    print(f"\n[+] {description}...")
    try:
        if command.startswith("python "):
            command = command.replace("python ", f"{sys.executable} ", 1)
            
        result = subprocess.run(command, shell=True, check=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[-] Error during '{description}': {e}")
        return False

def git_push_changes():
    print("\n[+] Starting Git operations...")
    try:
        try:
            repo = Repo(os.getcwd())
        except InvalidGitRepositoryError:
            print("[!] Not a git repository. Initializing new repository...")
            repo = Repo.init(os.getcwd())

        # Ensure Git user is configured (Critical for servers)
        with repo.config_writer() as git_config:
            git_config.set_value('user', 'name', 'nestorchurin')
            git_config.set_value('user', 'email', 'pavlonimetrons@gmail.com')
            
        # Ensure Remote 'origin' is configured
        remote_url = "https://github.com/nestorchurin/proxy-list"
        if 'origin' not in repo.remotes:
            print(f"[+] Setting remote 'origin' to {remote_url}")
            repo.create_remote('origin', remote_url)
            
        # Check if there are changes
        if not repo.is_dirty(untracked_files=True):
            print("[-] No changes detected. Skipping commit.")
            return True
            
        # Add specific paths
        print("[+] Staging changes...")
        repo.index.add(['proxies/', 'README.md'])
        
        # Commit
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        commit_msg = f"Auto-update proxy list [{timestamp}]"
        print(f"[+] Committing: {commit_msg}")
        repo.index.commit(commit_msg)
        
        # Push
        print("[+] Pushing to GitHub...")
        origin = repo.remote(name='origin')
        origin.push()
        
        print(f"[+] Successfully pushed updates to GitHub at {timestamp}")
        return True
        
    except GitCommandError as e:
        print(f"[-] Git Error: {e}")
        return False
    except Exception as e:
        print(f"[-] Error ({type(e).__name__}): {e}")
        return False

def main():
    print("=== Starting Automated Proxy Update ===")
    
    # 1. Run Proxy Manager (Fetch, Clean, Check)
    if not run_command("python proxy_manager.py", "Running Proxy Manager"):
        sys.exit(1)
    
    # 2. Update README
    if not run_command("python update_readme.py", "Updating README statistics"):
        sys.exit(1)
    
    # 3. Git Operations
    if not git_push_changes():
        sys.exit(1)

    print("\n=== Automation Complete ===")

if __name__ == "__main__":
    main()
