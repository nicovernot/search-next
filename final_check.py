import subprocess

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd="/home/nvernot/projets/search-next")
        return result.stdout + result.stderr
    except Exception as e:
        return str(e)

print("--- GIT STATUS ---")
print(run_command("git status"))
print("\n--- LIST ROOT (ls -F) ---")
print(run_command("ls -F"))
print("\n--- FRONT-NEXT DETAILS (ls -la front-next) ---")
print(run_command("ls -la front-next"))
print("\n--- GIT REMOTES ---")
print(run_command("git remote -v"))
