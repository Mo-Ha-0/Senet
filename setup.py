from setuptools import setup, Extension
from pybind11.setup_helpers import Pybind11Extension, build_ext
import sys

ext_modules = [
    Pybind11Extension(
        "ai_cpp",
        ["ai_engine.cpp"],
        cxx_std=17,
        extra_compile_args=['-O3'] if sys.platform != 'win32' else ['/O2'],
    ),
]

setup(
    name="ai_cpp",
    version="1.0.0",
    author="Mohammad",
    description="C++algorithm for Senet AI using Expectiminimax",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)