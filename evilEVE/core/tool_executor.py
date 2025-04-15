# -------------- core/tool_executor.py --------------
# Executes external CLI tools and returns output
from subprocess import run, PIPE

def execute_tool(tool, args):
    try:
        result = run([tool] + args, stdout=PIPE, stderr=PIPE, timeout=20)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.decode(),
            "stderr": result.stderr.decode(),
            "exit_code": result.returncode
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "exit_code": -1
        }

