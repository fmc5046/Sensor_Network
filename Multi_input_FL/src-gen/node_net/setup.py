import sys
assert (sys.version_info.major >= 3 and sys.version_info.minor >= 6),     "The Python target requires Python version >= 3.6."

from setuptools import setup, Extension

linguafrancanode_netmodule = Extension("LinguaFrancanode_net",
                                            sources = ["lib/schedule.c", "lib/util.c", "lib/tag.c", "lib/time.c", "core/mixed_radix.c", "core/platform/lf_linux_support.c", "node_net.c"],
                                            define_macros=[("MODULE_NAME", "LinguaFrancanode_net"), ("LF_REACTION_GRAPH_BREADTH", "6"), ("LOG_LEVEL", "2")])

setup(name="LinguaFrancanode_net", version="1.0",
        ext_modules = [linguafrancanode_netmodule],
        install_requires=["LinguaFrancaBase"])