import subprocess
def lookup(host):
    subprocess.run(["nslookup", host], check=True)
