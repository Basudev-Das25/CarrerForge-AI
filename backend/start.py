"""Start the CareerForge AI backend server."""

import sys
import os
import subprocess
import time
import signal


def check_port(port: int) -> bool:
    """Check if a port is already in use."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0


def main():
    port = 8000
    print(f"Starting CareerForge AI backend on port {port}...")

    # Check if already running
    if check_port(port):
        print(f"Backend already running on port {port}")
        return

    # Start uvicorn
    cmd = [
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--host", "127.0.0.1",
        "--port", str(port),
    ]

    try:
        process = subprocess.Popen(
            cmd,
            cwd=str(Path(__file__).parent),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        # Wait for server to start
        for _ in range(30):
            if check_port(port):
                print(f"Backend started on http://127.0.0.1:{port}")
                break
            time.sleep(1)
        else:
            print("Warning: Could not verify backend startup, but process is running")

        # Keep running
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\nShutting down backend...")
            process.terminate()
            process.wait()

    except FileNotFoundError:
        print("Error: Python not found. Please install Python 3.11+")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting backend: {e}")
        sys.exit(1)


if __name__ == "__main__":
    from pathlib import Path
    main()
