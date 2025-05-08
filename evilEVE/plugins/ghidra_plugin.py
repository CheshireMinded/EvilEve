import os
import subprocess
import time

class GhidraHeadlessPlugin:
    def __init__(self, ghidra_path, binary_path, project_path, log_path):
        self.ghidra_path = ghidra_path
        self.binary_path = binary_path
        self.project_path = project_path
        self.log_path = log_path

    def run(self):
        os.makedirs(self.project_path, exist_ok=True)
        cmd = [
            "nohup",
            "./support/analyzeHeadless",
            self.project_path, "evileve_proj",
            "-import", self.binary_path,
            "-deleteProject"
        ]

        with open(self.log_path, "w") as logfile:
            subprocess.Popen(
                cmd,
                cwd=self.ghidra_path,
                stdout=logfile,
                stderr=subprocess.STDOUT
            )

        print(f"[ghidra_plugin] Launched Ghidra analysis for: {self.binary_path}")

