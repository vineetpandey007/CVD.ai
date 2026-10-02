import os
import site
import shutil
import signal
import subprocess
import sys
import sysconfig
from collections.abc import Mapping, Sequence


def _script_directories() -> list[str]:
    user_scripts = os.path.join(
        os.path.dirname(site.getusersitepackages()), "Scripts"
    )
    directories = [
        sysconfig.get_path("scripts"),
        os.path.join(os.path.dirname(sys.executable), "Scripts"),
        os.path.join(site.getuserbase(), "Scripts"),
        user_scripts,
    ]
    return list(dict.fromkeys(path for path in directories if path and os.path.isdir(path)))


def _resolve_command(args: Sequence[str], env: Mapping[str, str] | None) -> list[str]:
    if not args:
        return list(args)

    executable = args[0]
    if os.path.dirname(executable) or (os.path.altsep and os.path.altsep in executable):
        return list(args)

    effective_env = os.environ.copy() if env is None else dict(env)
    search_paths = []
    for key in ("PATH", "Path"):
        value = effective_env.get(key)
        if value:
            search_paths.extend(value.split(os.pathsep))
    for candidate in _script_directories():
        if candidate and candidate not in search_paths:
            search_paths.append(candidate)

    for path in search_paths:
        if not path or not os.path.isdir(path):
            continue
        try:
            resolved = shutil.which(executable, path=path)
        except Exception:
            resolved = None
        if resolved:
            return [resolved, *args[1:]]

        candidate = os.path.join(path, executable)
        if os.path.exists(candidate):
            return [candidate, *args[1:]]
        for extension in (".exe", ".cmd", ".bat", ".ps1"):
            with_extension = f"{candidate}{extension}"
            if os.path.exists(with_extension):
                return [with_extension, *args[1:]]

    return list(args)


def command_exists(command: str) -> bool:
    resolved = _resolve_command([command], os.environ.copy())[0]
    return resolved != command


def run_command(
    args: Sequence[str],
    timeout: int,
    env: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    effective_env = os.environ.copy() if env is None else dict(env)
    script_dirs = _script_directories()
    for key in ("PATH", "Path"):
        current = effective_env.get(key)
        if current:
            combined = current.split(os.pathsep) + script_dirs
            effective_env[key] = os.pathsep.join(dict.fromkeys(combined))
        else:
            effective_env[key] = os.pathsep.join(script_dirs)
    resolved_args = _resolve_command(args, effective_env)
    process_group_options = (
        {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
        if os.name == "nt"
        else {"start_new_session": True}
    )
    process = subprocess.Popen(
        resolved_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        shell=False,
        env=effective_env,
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

    return subprocess.CompletedProcess(resolved_args, process.returncode, stdout, stderr)
