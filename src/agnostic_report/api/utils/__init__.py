import os
import typing

from fastapi.staticfiles import StaticFiles


class SPA(StaticFiles):

    def lookup_path(
        self, path: str
    ) -> typing.Tuple[str, typing.Optional[os.stat_result]]:
        for directory in self.all_directories:
            full_path = os.path.realpath(os.path.join(directory, path))
            directory = os.path.realpath(directory)
            if os.path.commonprefix([full_path, directory]) != directory:
                continue
            try:
                return full_path, os.stat(full_path)
            except (FileNotFoundError, NotADirectoryError):
                full_path = os.path.realpath(os.path.join(directory, 'index.html'))
                return full_path, os.stat(full_path)
        return "", None
