import os
import subprocess
import pathlib
import platform
import sys
import time
import shutil
from pathlib import Path

def run():

    project_name = pathlib.Path.cwd().name
    
    if platform.system() == "Windows":
        base = pathlib.Path(os.environ.get("LOCALAPPDATA", "C:/Temp")) / "uv_envs"
    else:
        base = pathlib.Path.home() / ".cache" / "uv_envs"
    
    safe_path = base / f"{project_name}_env"

    # 2. Validate/Heal the Global Environment folder (`safe_path`)
    global_env_exists = safe_path.exists() and (safe_path / "pyvenv.cfg").exists()
    
    if global_env_exists:
        print(f"Using existing global venv at: {safe_path}")
    else:
        if safe_path.exists():
            print(f"Cleaning up invalid global environment at {safe_path}")
            # Try aggressive removal with retries for Windows file locks
            for attempt in range(3):
                try:
                    shutil.rmtree(safe_path)
                    break
                except OSError:
                    time.sleep(0.5)
            
            # If Python's shutil still failed due to a lock, force it via Windows command prompt
            if safe_path.exists() and platform.system() == "Windows":
                try:
                    subprocess.run(["cmd", "/c", "rmdir", "/s", "/q", str(safe_path)], check=True, capture_output=True)
                except subprocess.CalledProcessError:
                    print("⚠️ Warning: Could not clear environment folder because a process is locking it.")
                    print("Please close any open terminals or Python processes using this environment and try again.")
                    sys.exit(1)

        print(f"Creating new venv at: {safe_path}")
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["uv", "venv", "--force", str(safe_path)], check=True)

    # 4. Set Environment Variables & Sync
    env = os.environ.copy()
    env["UV_PROJECT_ENVIRONMENT"] = str(safe_path)
    env["UV_LINK_MODE"] = "copy"

    local_cache = pathlib.Path(os.environ.get("LOCALAPPDATA", "C:/Temp")) / "uv/cache"
    local_cache.mkdir(parents=True, exist_ok=True)
    env["UV_CACHE_DIR"] = str(local_cache)

    print("Syncing dependencies...")    
    # Run uv sync using the target environment explicitly
    subprocess.run(["uv", "sync", "--project", str(pathlib.Path.cwd())], env=env, check=True)
    
    if platform.system() == "Windows":
        new_python_path = safe_path.joinpath(Path("Scripts")).joinpath(Path("python.exe"))
        new_activate_path = safe_path.joinpath(Path("Scripts")).joinpath(Path("activate"))
    else:
        new_python_path = safe_path.joinpath(Path("bin")).joinpath(Path("python"))
        new_activate_path = safe_path.joinpath(Path("bin")).joinpath(Path("activate"))

    print(f"\nEnvironment files stored at {safe_path}")
    print("Setup complete.")
    print(f"Select Python Interpreter: {new_python_path}")
    print(f"Activate in terminal: {new_activate_path.joinpath(Path("activate"))}")
    print(f"If on Mac or Linux may need to chmod +x to enable permissions for activation")


if __name__ == '__main__':
    run()