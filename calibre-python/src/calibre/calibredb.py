from __future__ import annotations

import json
import logging
import subprocess
import threading
from pathlib import Path
from typing import List, Union

from pydantic import TypeAdapter

from calibre.calibre_library import AbstractCalibreLibrary
from calibre.errors import CalibreRuntimeError
from calibre.objects import ExternalBookMetadata

logger = logging.getLogger(__name__)


def run_shell(cmd):
    res = subprocess.run(cmd, check=True, encoding="utf-8", capture_output=True)
    if res.returncode != 0:
        raise ValueError(f"Error while running cmd {cmd}: {res.stdout}")
    if res.stderr:
        logger.warning(res.stderr)
    return res.stdout


class CalibreDB(AbstractCalibreLibrary):
    def __init__(self, library_path: Union[Path, str]):
        super().__init__(library_path=library_path)

        # Concurrent access to calibre are forbidden by the calibredb CLI
        self.mutex = threading.Lock()

    def _run_calibredb(self, params: List[str]):
        cmd = ["calibredb", "--with-library", str(self.library_path), *params]

        logger.debug("Running cmd : %s", cmd)

        self.mutex.acquire()

        try:
            res = run_shell(cmd)
        except subprocess.CalledProcessError as e:
            raise CalibreRuntimeError(e.cmd, e.returncode, e.stdout, e.stderr) from e

        self.mutex.release()

        return res

    def add_books(self, ebooks: List[Path]):
        self._run_calibredb(["add", *[str(p) for p in ebooks]])

        return self

    def list_books(self) -> List[ExternalBookMetadata]:
        fields = [
            "id",
            "title",
            "authors",
            "series",
            "series_index",
            "isbn",
            "author_sort",
            "timestamp",
            "pubdate",
            "cover",
            "formats",
            "last_modified",
            "size",
        ]

        cmd = ["list", "--for-machine", "--fields", ",".join(fields)]

        res = self._run_calibredb(cmd)

        return TypeAdapter(List[ExternalBookMetadata]).validate_python(json.loads(res))
