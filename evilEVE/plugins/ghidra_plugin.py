import os
import subprocess
import time

class GhidraHeadlessPlugin:
    """
    Runs a headless Ghidra analysis in the background using analyzeHeadless.

    Parameters:
        ghidra_path (str): Path to the Ghidra installation directory.
        binary_path (str): Path to the binary file to analyze.
        project_path (str): Directory to store the Ghidra project.
        log_path (str): File path to redirect stdout/stderr output logs.
    """

    def __init__(self, ghidra_path, binary_path, project_path, log_path):
        self.ghidra_path = ghidra_path
        self.binary_path = binary_path
        self.project_path = project_path
        self.log_path = log_path

    def run(self):
        """
        Launches the Ghidra headless analysis as a background process using nohup.
        """
        os.makedirs(self.project_path, exist_ok=True)
        cmd = [
            "nohup",
            "./support/analyzeHeadless",
            self.project_path, "evileve_proj",
            "-import", self.binary_path,
            "-deleteProject"
        ]

        try:
            with open(self.log_path, "w") as logfile:
                subprocess.Popen(
                    cmd,
                    cwd=self.ghidra_path,
                    stdout=logfile,
                    stderr=subprocess.STDOUT,
                    preexec_fn=os.setpgrp
                )
            print(f"[ghidra_plugin] Launched Ghidra analysis for: {self.binary_path}")
        except Exception as e:
            print(f"[ghidra_plugin] Failed to launch Ghidra: {e}")
            raise RuntimeError(f"Ghidra plugin failed: {e}")
