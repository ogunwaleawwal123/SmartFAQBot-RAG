from datetime import datetime


def _time():
    return datetime.now().strftime("%H:%M:%S")


def info(module: str, message: str):
    print(f"[{_time()}] [INFO] [{module}] {message}")


def success(module: str, message: str):
    print(f"[{_time()}] [SUCCESS] [{module}] {message}")


def warning(module: str, message: str):
    print(f"[{_time()}] [WARNING] [{module}] {message}")


def error(module: str, message: str):
    print(f"[{_time()}] [ERROR] [{module}] {message}")


def timing(module: str, seconds: float):
    print(f"[{_time()}] [TIME] [{module}] {seconds:.2f}s")