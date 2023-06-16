import sys
assert (sys.version_info.major >= 3 and sys.version_info.minor >= 6),     "The Python target requires Python version >= 3.6."

from setuptools import setup, Extension

linguafrancamimodule = Extension("LinguaFrancami",
                                            sources = ["lib/schedule.c", "lib/util.c", "lib/tag.c", "lib/time.c", "core/mixed_radix.c", "core/platform/lf_linux_support.c", "mi.c"],
                                            define_macros=[("MODULE_NAME", "LinguaFrancami"), ("LF_REACTION_GRAPH_BREADTH", "6"), ("LOG_LEVEL", "2")])

setup(name="LinguaFrancami", version="1.0",
        ext_modules = [linguafrancamimodule],
        install_requires=["LinguaFrancaBase"])