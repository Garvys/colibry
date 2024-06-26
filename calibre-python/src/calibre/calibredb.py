from __future__ import annotations

import json
import logging
import subprocess
import threading
from pathlib import Path
from typing import List, Union

from pydantic import TypeAdapter

from calibre.calibre_library import CalibreLibrary
from calibre.errors import CalibreRuntimeError
from calibre.objects import BookMetadata
from calibre.search_params import SearchParams
from copy import deepcopy

logger = logging.getLogger(__name__)


def run_shell(cmd):
    res = subprocess.run(cmd, check=True, encoding="utf-8", capture_output=True)
    if res.returncode != 0:
        raise ValueError(f"Error while running cmd {cmd}: {res.stdout}")
    if res.stderr:
        logger.warning(res.stderr)
    return res.stdout


class CalibreDB(CalibreLibrary):
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

    def clone(self, new_library_path: Path) -> CalibreDB:
        self._run_calibredb(["clone", str(new_library_path)])

        return CalibreDB(library_path=new_library_path)

    def add(self, ebooks: List[Path]):
        self._run_calibredb(["add", *[str(p) for p in ebooks]])

        return self

    def list_books(self, params: SearchParams = SearchParams()) -> List[BookMetadata]:
        fields = deepcopy(params.fields)
        fields.append("id")
        fields.append("title")

        cmd = ["list", "--for-machine", "--fields", ",".join(fields)]
        if params.filters:
            for filter in params.filters:
                cmd.append("-s")
                cmd.append(filter.to_calibredb_filter())

        res = self._run_calibredb(cmd)

        return TypeAdapter(List[BookMetadata]).validate_python(json.loads(res))

    def list_authors(self) -> List[str]:
        res = self._run_calibredb(["list", "--for-machine", "--fields", "authors"])
        books_metadata = TypeAdapter(List[BookMetadata]).validate_python(
            json.loads(res)
        )
        return [e.authors for e in books_metadata if e.authors]

    def remove_from_ids(self, ids: List[int]) -> CalibreDB:
        self._run_calibredb(["remove", ",".join([str(e) for e in ids])])

        return self

    def remove_books(self, books: List[BookMetadata]):
        return self.remove_from_ids(ids=[e.id for e in books])
