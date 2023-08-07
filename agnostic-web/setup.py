import os
import platform
from pathlib import Path
from subprocess import check_call
import shutil

from setuptools import setup


base_dir = Path(__file__).parent
ui_dir = base_dir / '..' / 'agnostic-web-ui'
ui_dist = ui_dir / 'dist'
package_dist = base_dir / 'src' / 'agnostic' / 'web' / 'ui'


def make_cmd(cmd):
    if platform.system() == 'Windows':
        return f'cmd /c "{cmd}"'
    return cmd


if not ui_dist.is_dir() and not package_dist.is_dir():
    print('Building web UI')
    check_call(make_cmd(f'cd {ui_dir} && npm install'))
    check_call(make_cmd(f'cd {ui_dir} && npm run build'))
    print(f'UI distribution created at {ui_dist}')
    print(f'Copying UI distribution to {package_dist}')
    shutil.rmtree(package_dist, ignore_errors=True)
    shutil.copytree(ui_dist, package_dist)
    print(f'UI distribution copied')


setup(
    install_requires=[
        f'agnostic-core @ file://{os.path.join(os.path.dirname(__file__), "..", "agnostic-core")}',
        'fastapi>=0.89.1,<0.100.0',
        'uvicorn[standard]>=0.20.0,<1.0',
        'python-multipart>=0.0.5,<1.0'
    ]
)
