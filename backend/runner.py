"""Bounded subprocess execution and output comparison for a personal OJ."""

import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time

from .models import Problem, SubmissionRequest

LAUNCHER = Path(__file__).with_name("launcher.py")
OUTPUT_LIMIT = 1024 * 1024


def compilers():
    return {
        "c": shutil.which("clang") or shutil.which("gcc"),
        "cpp": shutil.which("clang++") or shutil.which("g++"),
        "python": sys.executable,
    }


def outputs_match(actual, expected, comparator="tokens"):
    if comparator == "tokens":
        return actual.split() == expected.split()
    return actual.replace("\r\n", "\n").rstrip("\n") == expected.replace("\r\n", "\n").rstrip("\n")


def kill_group(process):
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def execute(command, stdin, directory, timeout, memory_mb=256):
    """Use files instead of pipes to bound RAM consumed by hostile output loops."""
    input_path = directory / "stdin.txt"
    output_path = directory / "stdout.txt"
    error_path = directory / "stderr.txt"
    input_path.write_text(stdin, encoding="utf-8")
    environment = {"PATH": os.defpath, "LANG": "en_US.UTF-8", "PYTHONIOENCODING": "utf-8", "TMPDIR": str(directory), "HOME": str(directory)}
    start = time.monotonic()
    reason = None
    with input_path.open("rb") as source, output_path.open("wb") as output, error_path.open("wb") as error:
        guarded = [sys.executable, str(LAUNCHER), str(timeout), str(memory_mb), *map(str, command)]
        process = subprocess.Popen(guarded, stdin=source, stdout=output, stderr=error, cwd=directory, env=environment, start_new_session=True)
        try:
            while process.poll() is None:
                if time.monotonic() - start > timeout:
                    reason = "TLE"
                    break
                if output_path.stat().st_size >= OUTPUT_LIMIT or error_path.stat().st_size >= OUTPUT_LIMIT:
                    reason = "OLE"
                    break
                time.sleep(0.008)
        finally:
            # Also reap subprocesses left alive after their original parent exited.
            kill_group(process)
            process.wait()
    elapsed = round((time.monotonic() - start) * 1000)
    stdout = output_path.read_bytes()[:OUTPUT_LIMIT].decode("utf-8", errors="replace")
    stderr = error_path.read_bytes()[:OUTPUT_LIMIT].decode("utf-8", errors="replace")
    if reason is None:
        if process.returncode == -signal.SIGXCPU:
            reason = "TLE"
        elif process.returncode == -signal.SIGXFSZ or output_path.stat().st_size >= OUTPUT_LIMIT or error_path.stat().st_size >= OUTPUT_LIMIT:
            reason = "OLE"
        elif process.returncode != 0:
            reason = "RE"
    return {"verdict": reason or "OK", "time_ms": elapsed, "stdout": stdout, "stderr": stderr[:6000], "exit_code": process.returncode}


def judge(problem: Problem, submission: SubmissionRequest):
    compiler = compilers()[submission.language]
    if not compiler:
        return {"verdict": "SE", "score": 0, "message": "没有找到对应编译器，请安装 Xcode Command Line Tools。", "cases": []}
    with tempfile.TemporaryDirectory(prefix="ayaya-oj-") as temporary:
        directory = Path(temporary)
        extension = {"c": "c", "cpp": "cpp", "python": "py"}[submission.language]
        source_path = directory / f"main.{extension}"
        source_path.write_text(submission.code, encoding="utf-8")
        if submission.language == "python":
            command = [compiler, "-I", "-B", str(source_path)]
        else:
            executable = directory / "main"
            standard = "c11" if submission.language == "c" else "c++17"
            compiled = execute([compiler, f"-std={standard}", "-O2", str(source_path), "-o", str(executable), *(["-lm"] if submission.language == "c" else [])], "", directory, 20, 1024)
            if compiled["verdict"] != "OK":
                return {"verdict": "CE", "score": 0, "message": compiled["stderr"] or "编译超时或输出超限", "cases": []}
            command = [str(executable)]
        if submission.mode == "custom":
            result = execute(command, submission.stdin, directory, problem.time_limit_ms / 1000, problem.memory_limit_mb)
            return {"verdict": "RUN" if result["verdict"] == "OK" else result["verdict"], "score": None, "time_ms": result["time_ms"], "cases": [result | {"index": 1}], "message": "自定义运行不计入通过状态"}
        tests = problem.samples if submission.mode == "sample" else problem.tests
        results = []
        for index, test in enumerate(tests, 1):
            result = execute(command, test.input, directory, problem.time_limit_ms / 1000, problem.memory_limit_mb)
            verdict = result["verdict"]
            if verdict == "OK":
                verdict = "AC" if outputs_match(result["stdout"], test.output, problem.comparator) else "WA"
            results.append(result | {"index": index, "verdict": verdict, "stdout": result["stdout"][:6000], "input": test.input[:6000], "expected": test.output[:6000]})
        passed = sum(case["verdict"] == "AC" for case in results)
        verdict = next((case["verdict"] for case in results if case["verdict"] != "AC"), "AC")
        return {"verdict": verdict, "score": math.floor(problem.score * passed / len(results)), "passed": passed, "total": len(results), "time_ms": max(case["time_ms"] for case in results), "cases": results, "message": "样例运行不计入通过状态" if submission.mode == "sample" else "本地测试数据评测"}
