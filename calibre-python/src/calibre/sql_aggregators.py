# Just to avoid a crash
def title_sort(title, order=None, lang=None):
    return title


class Concatenate:
    """String concatenation aggregator for sqlite"""

    def __init__(self, sep=","):
        self.sep = sep
        self.ans = []

    def step(self, value):
        if value is not None:
            self.ans.append(value)

    def finalize(self):
        try:
            if not self.ans:
                return None
            return self.sep.join(self.ans)
        except Exception:
            import traceback

            traceback.print_exc()
            raise


class SortedConcatenate:
    """String concatenation aggregator for sqlite, sorted by supplied index"""

    sep = " & "

    def __init__(self):
        self.ans = {}

    def step(self, ndx, value):
        if value is not None:
            self.ans[ndx] = value

    def finalize(self):
        try:
            if len(self.ans) == 0:
                return None
            return self.sep.join(map(self.ans.get, sorted(self.ans.keys())))
        except Exception:
            import traceback

            traceback.print_exc()
            raise
