import os
import signal
import subprocess
from collections.abc import Sequence


def run_command(
    args: Sequence[str],
    timeout: int,
) -> subprocess.CompletedProcess[str]:
    process_group_options = (
        {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
        if os.name == "nt"
        else {"start_new_session": True}
    )
    process = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        shell=False,
        **process_group_options,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            if os.name == "nt":
                system_root = os.environ.get("SystemRoot")
                if not system_root:
                    raise RuntimeError("SystemRoot is unavailable for process-tree cleanup")
                taskkill = os.path.join(system_root, "System32", "taskkill.exe")
                result = subprocess.run(
                    [taskkill, "/PID", str(process.pid), "/T", "/F"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    timeout=10,
                    shell=False,
                    check=False,
                )
                if result.returncode != 0 and process.poll() is None:
                    raise RuntimeError(
                        f"taskkill failed to terminate process tree: {result.stderr.strip()}"
                    )
            else:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        except Exception as cleanup_error:
            if process.poll() is None:
                process.kill()
            process.communicate()
            raise RuntimeError("Failed to terminate timed-out process tree") from cleanup_error

        process.communicate()
        raise

    return subprocess.CompletedProcess(args, process.returncode, stdout, stderr)
