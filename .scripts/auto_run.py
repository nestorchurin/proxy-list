import subprocess
import sys
import os

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

def main():
    print("=== Starting Automated Proxy Update ===")
    
    # 1. Run Proxy Manager (Fetch, Clean, Check)
    if not run_command("python proxy_manager.py", "Running Proxy Manager"):
        sys.exit(1)
    
    # 2. Update README
    if not run_command("python update_readme.py", "Updating README statistics"):
        sys.exit(1)

    print("\n=== Automation Complete ===")

if __name__ == "__main__":
    main()
