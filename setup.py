import os
import subprocess
import pathlib
import platform
import sys
import time
import shutil
from pathlib import Path
import importlib



def verify_environment(new_python_path: str | pathlib.Path) -> None:
    """Verifies that key packages import successfully using the specified Python executable.

    Raises RuntimeError if any import fails.
    """
    packages = ["numpy", "pandas", "matplotlib", "scipy"]
    python_exe = pathlib.Path(new_python_path)

    # Python code executed inside the target environment
    code = f"""
        packages = {packages!r}
        for pkg in packages:
            __import__(pkg)
        """

    result = subprocess.run(
        [str(python_exe), "-c", code],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Failed to import required packages using {python_exe}.\n"
            f"Error output:\n{result.stderr.strip()}"
        )

    # ANSI escape codes: \033[32m sets green text, \033[0m resets back to default
    GREEN = "\033[32m"
    RESET = "\033[0m"

    print(
        f"{GREEN} Success! All packages ({', '.join(packages)}) imported correctly.{RESET}"
    )


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
        subprocess.run(["uv", "venv", "--allow-existing", str(safe_path)], check=True)

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

    print("=======================================================================")
    print("\n Performing environment checks...\n")
    verify_environment(new_python_path)

    print(f"\n\n\n==========================================================\n")
    print(f"Setup Instructions:\n")
    print("1. Highlight and copy using ctrl + c the path to your python interpreter below:\n")
    print(f"Select Python Interpreter: {new_python_path.as_posix()}\n")
    print(f"2. Type code . into the terminal to open vscode")
    print(f"3. Type `ctrl + shift + p` and type and select `Python: Select Interpreter")
    print(f"4. Select `Enter Interpreter Path` and paste the path into the box followed by hit Enter")
    print(f"5. When you open a Jupyter Notebook click `Detect Kernel`, `Python Environments` and then select {project_name}_env")
    print(f"If you need these instructions again you can rerun the script. It's ok to close this window")
    print(f"\n==========================================================\n")

if __name__ == '__main__':
    run()
