import subprocess
import os
from pathlib import Path

def _run_git(args: list[str]) -> str:
    """Run a git command and return its stdout, stripping whitespace."""
    cwd = Path(__file__).parent.parent
    try:
        # Use shell=True dynamically on Windows to ensure git resolves properly if it's a batch wrapper
        use_shell = os.name == "nt"
        result = subprocess.run(
            ["git"] + args,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            check=True,
            shell=use_shell
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: git {' '.join(args)}\nError: {e.stderr}")
        raise

def check_for_updates() -> dict:
    """Fetch origin and compare HEAD to origin/main to find updates."""
    try:
        _run_git(["fetch", "origin"])
        
        local_hash = _run_git(["rev-parse", "HEAD"])
        remote_hash = _run_git(["rev-parse", "origin/main"])
        
        if local_hash == remote_hash:
            return {"update_available": False, "commits": [], "error": None}
            
        # Get the commit history between local and remote
        log_output = _run_git(["log", f"{local_hash}..{remote_hash}", "--oneline"])
        commits = [line for line in log_output.split("\n") if line.strip()]
        
        return {
            "update_available": len(commits) > 0,
            "commits": commits,
            "error": None
        }
    except Exception as e:
        return {"update_available": False, "commits": [], "error": str(e)}

def apply_update() -> bool:
    """Apply the latest updates from origin/main. Returns True if successful."""
    try:
        # Stash any local changes to tracked files
        _run_git(["stash"])
        # Fast-forward pull
        _run_git(["pull", "origin", "main", "--ff-only"])
        
        # Try to install any updated requirements
        cwd = Path(__file__).parent.parent
        req_path = cwd / "requirements.txt"
        if req_path.exists():
            print("Installing updated requirements...")
            venv_python = cwd / ".venv" / "Scripts" / "python.exe" if os.name == "nt" else cwd / ".venv" / "bin" / "python"
            if venv_python.exists():
                subprocess.run(
                    [str(venv_python), "-m", "pip", "install", "-r", str(req_path)],
                    cwd=str(cwd),
                    capture_output=True,
                    check=True
                )
        return True
    except Exception as e:
        print(f"Failed to apply update: {e}")
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Check for updates")
    parser.add_argument("--apply", action="store_true", help="Apply updates")
    args = parser.parse_args()
    
    if args.check:
        res = check_for_updates()
        if res.get("error"):
            print(f"Error checking updates: {res['error']}")
        elif res.get("update_available"):
            print("Updates available:")
            for c in res["commits"]:
                print(f"  {c}")
        else:
            print("Up to date.")
    elif args.apply:
        print("Applying updates...")
        success = apply_update()
        if success:
            print("Successfully updated.")
        else:
            print("Update failed.")
