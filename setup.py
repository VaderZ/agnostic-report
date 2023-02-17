import os
from pathlib import Path
from subprocess import check_call
import platform


from setuptools import setup


base_dir = Path(__file__).parent
ui_dir = base_dir / 'src' / 'agnostic_report' / 'ui'
ui_dist = ui_dir / 'dist'


def make_cmd(cmd):
    if platform.system() == 'Windows':
        return f'cmd /c "{cmd}"'
    return cmd


if not ui_dist.is_dir():
    print('Building web UI')
    check_call(make_cmd(f'cd {ui_dir} && npm install'))
    check_call(make_cmd(f'cd {ui_dir} && npm run build'))
    print(f'UI distribution created at {ui_dist}')


setup()
