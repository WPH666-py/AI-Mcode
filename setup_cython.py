import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

try:
    from Cython.Build import cythonize
    from Cython.Distutils import build_ext
    HAS_CYTHON = True
except ImportError:
    HAS_CYTHON = False
    print("[WARN] Cython 未安装，跳过 C 扩展编译。运行: pip install cython")

try:
    from setuptools import setup, Extension, find_packages
except ImportError:
    from distutils.core import setup, Extension


def _compile_args():
    return ["/O2", "/GL"] if sys.platform == "win32" else ["-O3", "-march=native", "-ffast-math"]


def _link_args():
    return ["/LTCG"] if sys.platform == "win32" else []


def get_extensions():
    if not HAS_CYTHON:
        return []

    import numpy as np

    extensions = [
        Extension(
            "apps.core.math_utils_cy",
            sources=["apps/core/math_utils.pyx"],
            include_dirs=[np.get_include()],
            extra_compile_args=_compile_args(),
            extra_link_args=_link_args(),
            define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
        ),
        Extension(
            "apps.files.parsers_fast_ext",
            sources=["apps/files/parsers_fast.pyx"],
            include_dirs=[],
            extra_compile_args=["/O2"] if sys.platform == "win32" else ["-O3"],
        ),
        Extension(
            "apps.files.cleaners_fast_ext",
            sources=["apps/files/cleaners_fast.pyx"],
            include_dirs=[np.get_include()],
            extra_compile_args=_compile_args(),
            extra_link_args=_link_args(),
            define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
        ),
    ]
    return extensions


def _module_name(py_file: Path) -> str:
    rel = py_file.relative_to(BASE_DIR).with_suffix("")
    return ".".join(rel.parts)


def get_all_python_extensions():
    if not HAS_CYTHON:
        return []

    import numpy as np

    roots = [BASE_DIR / "apps", BASE_DIR / "config"]
    excluded_parts = {"migrations", "__pycache__"}
    excluded_names = {
        "__init__.py",
        "manage.py",
        "setup_cython.py",
        "asgi.py",
        "wsgi.py",
        "math_numba.py",
    }

    extensions = get_extensions()
    existing_modules = {ext.name for ext in extensions}

    for root in roots:
        if not root.exists():
            continue
        for py_file in root.rglob("*.py"):
            if py_file.name in excluded_names:
                continue
            if any(part in excluded_parts for part in py_file.parts):
                continue

            module = _module_name(py_file)
            if module in existing_modules:
                continue

            extensions.append(
                Extension(
                    module,
                    sources=[str(py_file.relative_to(BASE_DIR)).replace("\\", "/")],
                    include_dirs=[np.get_include()],
                    extra_compile_args=_compile_args(),
                    extra_link_args=_link_args(),
                    define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
                )
            )
            existing_modules.add(module)

    return extensions


def main():
    if not HAS_CYTHON:
        print("=" * 60)
        print("  无法编译 C 扩展：请先安装 Cython 和 C++ 编译器")
        print("  pip install cython")
        print("  项目将以纯 Python 模式运行（兼容模式）")
        print("=" * 60)
        return

    build_all = "--all" in sys.argv
    if build_all:
        sys.argv.remove("--all")

    extensions = get_all_python_extensions() if build_all else get_extensions()

    setup(
        name="math_model_generator_fast",
        version="1.0.0",
        description="数学建模 AI 生成器 - Cython 加速模块",
        packages=find_packages(include=["apps", "apps.*", "config"]),
        ext_modules=cythonize(
            extensions,
            language_level="3",
            compiler_directives={
                "boundscheck": False,
                "wraparound": False,
                "cdivision": True,
                "embedsignature": True,
                "annotation_typing": True,
                "profile": False,
                "linetrace": False,
            },
        ),
        cmdclass={"build_ext": build_ext},
        zip_safe=False,
    )

    print("=" * 60)
    if build_all:
        print("  项目 Python 模块批量 Cython 编译成功！")
    else:
        print("  核心 Cython 扩展编译成功！")
    print("  默认核心编译: py setup_cython.py build_ext --inplace")
    print("  全量模块编译: py setup_cython.py --all build_ext --inplace")
    print("=" * 60)


if __name__ == "__main__":
    os.chdir(str(BASE_DIR))
    main()
