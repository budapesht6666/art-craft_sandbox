"""Лист выражений Флюка крупным планом: blender -b -P sheet.py -- --expr cute:cam,half:cam,... --out DIR"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import fluk_rig as R  # noqa: E402


class Sheet(R.Episode):
    LAST = 100

    def camera(self, f):
        return (1.15, 1.55, 3.4)


R.run(Sheet(), __file__)
