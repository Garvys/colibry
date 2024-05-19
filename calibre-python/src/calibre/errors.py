class CalibreRuntimeError(Exception):
    """Raise when calibredb command line execution returns a non-zero exit code."""

    def __init__(self, cmd: str, exit_code: int, stdout: str, stderr: str):
        self.cmd = cmd
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr

        message = f"{cmd} exited with status {str(exit_code)}.\n\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"
        super().__init__(message)
