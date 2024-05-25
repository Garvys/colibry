from pathlib import Path
from urllib.parse import quote as urlquote


def ebook_download_link(children, library_path: Path, ebook_path: str):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    p = Path(ebook_path)
    p = p.relative_to(library_path)

    return "/download-from-library/{}".format(urlquote(str(p)))
