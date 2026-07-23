import json
import os
import pathlib
import platform
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path


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

    GREEN = "\033[32m"
    RESET = "\033[0m"

    print(
        f"{GREEN} Success! All packages ({', '.join(packages)}) imported correctly.{RESET}"
    )


def register_jupyter_kernel(python_exe: pathlib.Path, kernel_name: str) -> None:
    """Registers the environment as a Jupyter kernel assuming ipykernel is installed via uv sync."""
    print("Registering Jupyter kernel...")

    # Register kernel specification globally for the user
    subprocess.run(
        [
            str(python_exe),
            "-m",
            "ipykernel",
            "install",
            "--user",
            "--name",
            kernel_name,
            "--display-name",
            f"Python ({kernel_name})",
        ],
        check=True,
        capture_output=True,
    )


def upsert_setting(json_str: str, key: str, value: object) -> str:
    """Safely updates or injects a key into a JSON string without breaking comments or formatting."""
    val_str = json.dumps(value)
    pattern = re.compile(
        r'("' + re.escape(key) + r'"\s*:\s*)(true|false|null|-?\d+(?:\.\d+)?|"(?:\\.|[^"\\])*")',
        re.IGNORECASE,
    )

    if pattern.search(json_str):
        val_str_escaped = val_str.replace("\\", "\\\\")
        return pattern.sub(r"\g<1>" + val_str_escaped, json_str, count=1)

    last_brace_idx = json_str.rfind("}")
    if last_brace_idx != -1:
        before = json_str[:last_brace_idx].rstrip()
        if not before.endswith(",") and not before.endswith("{"):
            before += ","
        return before + f'\n  "{key}": {val_str}\n}}\n'

    return json_str


def configure_vscode_settings(new_python_path: pathlib.Path, kernel_name: str) -> None:
    """Safely updates .vscode/settings.json without removing existing comments or settings."""
    vscode_dir = pathlib.Path.cwd() / ".vscode"
    vscode_dir.mkdir(exist_ok=True)
    settings_path = vscode_dir / "settings.json"

    if settings_path.exists():
        with open(settings_path, "r", encoding="utf-8") as f:
            settings_content = f.read()
    else:
        settings_content = "{\n}"

    settings_content = upsert_setting(
        settings_content, "python.defaultInterpreterPath", new_python_path.as_posix()
    )
    settings_content = upsert_setting(
        settings_content, "terminal.integrated.defaultProfile.windows", "Command Prompt"
    )
    settings_content = upsert_setting(
        settings_content, "jupyter.preferredJupyterKernel", kernel_name
    )

    with open(settings_path, "w", encoding="utf-8") as f:
        f.write(settings_content)

def launch_vscode() -> None:
    """Launches VS Code in the current working directory."""
    print("\nOpening workspace in VS Code...")
    if platform.system() == "Windows":
        subprocess.run(["cmd", "/c", "code", "."], check=False)
    else:
        subprocess.run(["code", "."], check=False)

def run():
    project_name = pathlib.Path.cwd().name

    if platform.system() == "Windows":
        base = pathlib.Path(os.environ.get("LOCALAPPDATA", "C:/Temp")) / "uv_envs"
    else:
        base = pathlib.Path.home() / ".cache" / "uv_envs"

    env_name = f"{project_name}_env"
    safe_path = base / env_name

    # Validate/Heal the Global Environment folder
    global_env_exists = safe_path.exists() and (safe_path / "pyvenv.cfg").exists()

    if global_env_exists:
        print(f"Using existing global venv at: {safe_path}")
    else:
        if safe_path.exists():
            print(f"Cleaning up invalid global environment at {safe_path}")
            for attempt in range(3):
                try:
                    shutil.rmtree(safe_path)
                    break
                except OSError:
                    time.sleep(0.5)

            if safe_path.exists() and platform.system() == "Windows":
                try:
                    subprocess.run(
                        ["cmd", "/c", "rmdir", "/s", "/q", str(safe_path)],
                        check=True,
                        capture_output=True,
                    )
                except subprocess.CalledProcessError:
                    print("⚠️ Warning: Could not clear environment folder because a process is locking it.")
                    print("Please close any open terminals or Python processes using this environment and try again.")
                    sys.exit(1)

        print(f"Creating new venv at: {safe_path}")
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["uv", "venv", "--allow-existing", str(safe_path)], check=True)

    # Set Environment Variables & Sync
    env = os.environ.copy()
    env["UV_PROJECT_ENVIRONMENT"] = str(safe_path)
    env["UV_LINK_MODE"] = "copy"

    local_cache = pathlib.Path(os.environ.get("LOCALAPPDATA", "C:/Temp")) / "uv/cache"
    local_cache.mkdir(parents=True, exist_ok=True)
    env["UV_CACHE_DIR"] = str(local_cache)

    print("Syncing dependencies...")
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

    print("\n Automating Jupyter & VS Code workspace configuration...\n")
    register_jupyter_kernel(new_python_path, env_name)
    configure_vscode_settings(new_python_path, env_name)

    print(f"\n==========================================================\n")
    print(f" Setup Complete!\n")
    print(f" Target Environment: {new_python_path.as_posix()}")
    print(f" Terminal Activation: {new_activate_path.as_posix()}\n")
    print(f" Next step in VS Code:")
    print(f"  - When opening a notebook, click 'Select Kernel' -> 'Jupyter Kernel...'")
    print(f"  - Pick 'Python ({env_name})' from the top of the list.")
    print(f"\n==========================================================\n")

    input("Press Enter to launch VS Code...")
    launch_vscode()

if __name__ == "__main__":
    run()
