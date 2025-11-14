import functools
import inspect
import json
import types
from datetime import datetime
from pathlib import Path
import importlib
import sys
import os

from forgeoagent.config import (
    MCP_TOOLS_LOG_DIR
)
DEFAULT_LOG_NAME = f"{MCP_TOOLS_LOG_DIR}/../../logs/mcp_tools/{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

def _repo_logs_dir():
    # locate repository root (two parents up from this file: mcp/tools -> mcp -> repo)
    repo_root = Path(__file__).resolve().parents[2]
    logs_dir = repo_root / "logs"
    try:
        logs_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    return logs_dir


def _append_log(entry: dict, log_file: Path = None):
    if log_file is None:
        log_file = _repo_logs_dir() / DEFAULT_LOG_NAME

    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")
    except Exception:
        # best-effort logging; don't raise
        pass


def _limited_repr(obj, max_len: int = 300):
    try:
        r = repr(obj)
    except Exception:
        r = "<unreprable>"
    if len(r) > max_len:
        return r[: max_len - 3] + "..."
    return r


def _make_wrapper(func, module_name: str, qualname: str, log_file: Path = None):
    @functools.wraps(func)
    def _wrapped(*args, **kwargs):
        try:
            caller = None
            stack = inspect.stack()
            # find first stack frame outside this module and the wrapped function
            for frame_info in stack[1:6]:
                fn_mod = frame_info.frame.f_globals.get("__name__")
                if fn_mod and fn_mod != module_name:
                    caller = fn_mod
                    break

            entry = {
                "timestamp": datetime.now(),
                "module": module_name,
                "function": qualname,
                "caller_module": caller,
                "args": _limited_repr(args),
                "kwargs": _limited_repr(kwargs),
            }
            _append_log(entry, log_file=log_file)
        except Exception:
            # swallow any instrumentation error
            pass

        return func(*args, **kwargs)

    # mark as instrumented to avoid double wrapping
    try:
        _wrapped._instrumented = True
    except Exception:
        pass
    return _wrapped


def InstrumentModule(module_or_name, include_private: bool = False, log_file: str = DEFAULT_LOG_NAME):
    """Instrument top-level functions and class methods in a module.

    Args:
        module_or_name: module object or importable module name (str).
        include_private: if True, also instrument names starting with '_'.
        log_file: optional path to a log file (string or Path).
    """
    if isinstance(module_or_name, str):
        module_name = module_or_name
        module = sys.modules.get(module_name)
        if module is None:
            try:
                module = importlib.import_module(module_name)
            except Exception:
                return
    else:
        module = module_or_name
        module_name = getattr(module, "__name__", None)

    if module is None or module_name is None:
        return

    log_path = Path(log_file) if log_file else None

    for name, obj in list(vars(module).items()):
        if name.startswith("_") and not include_private:
            continue

        # instrument plain functions
        if isinstance(obj, types.FunctionType):
            if getattr(obj, "_instrumented", False):
                continue
            try:
                wrapped = _make_wrapper(obj, module_name, f"{module_name}.{obj.__qualname__}", log_file=log_path)
                setattr(module, name, wrapped)
            except Exception:
                continue

        # instrument classes: wrap their methods
        elif isinstance(obj, type):
            cls = obj
            # avoid re-instrumenting the same class
            if getattr(cls, "_instrumented_class", False):
                continue

            for attr_name, attr_val in list(vars(cls).items()):
                if attr_name.startswith("_") and not include_private:
                    continue

                # bound/instance methods are functions on the class
                try:
                    # handle staticmethod and classmethod
                    if isinstance(attr_val, staticmethod):
                        fn = attr_val.__func__
                        if not getattr(fn, "_instrumented", False):
                            wrapped_fn = _make_wrapper(fn, module_name, f"{module_name}.{cls.__name__}.{fn.__name__}", log_file=log_path)
                            setattr(cls, attr_name, staticmethod(wrapped_fn))
                    elif isinstance(attr_val, classmethod):
                        fn = attr_val.__func__
                        if not getattr(fn, "_instrumented", False):
                            wrapped_fn = _make_wrapper(fn, module_name, f"{module_name}.{cls.__name__}.{fn.__name__}", log_file=log_path)
                            setattr(cls, attr_name, classmethod(wrapped_fn))
                    elif isinstance(attr_val, types.FunctionType):
                        fn = attr_val
                        if not getattr(fn, "_instrumented", False):
                            wrapped_fn = _make_wrapper(fn, module_name, f"{module_name}.{cls.__name__}.{fn.__name__}", log_file=log_path)
                            setattr(cls, attr_name, wrapped_fn)
                except Exception:
                    # skip attributes we can't wrap
                    continue

            try:
                setattr(cls, "_instrumented_class", True)
            except Exception:
                pass


__all__ = ["InstrumentModule"]
