"""Execute the five analytical notebooks using the same Python as this command."""

import sys
import os
import tempfile
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from jupyter_client.kernelspec import KernelSpecManager
from jupyter_client import KernelManager

ROOT = Path(__file__).resolve().parents[1]


class CurrentPythonKernel(KernelSpecManager):
    """Avoid depending on a machine-global Jupyter kernel registration."""

    def get_kernel_spec(self, kernel_name):
        spec = super().get_kernel_spec(kernel_name)
        spec.argv = [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"]
        return spec


if __name__ == "__main__":
    for file in sorted((ROOT / "notebooks").glob("*.ipynb")):
        notebook = nbformat.read(file, as_version=4)
        manager = KernelManager(kernel_name="python3", kernel_spec_manager=CurrentPythonKernel())
        client = NotebookClient(
            notebook, km=manager, timeout=180, resources={"metadata": {"path": str(ROOT)}}
        )
        with tempfile.TemporaryDirectory(prefix="meridian-notebook-") as runtime:
            environment = {**os.environ, "IPYTHONDIR": runtime, "JUPYTER_RUNTIME_DIR": runtime}
            try:
                client.execute(env=environment)
            finally:
                if manager.has_kernel:
                    manager.shutdown_kernel(now=True)
        nbformat.write(notebook, file)
        print(f"Executed {file.name}")
