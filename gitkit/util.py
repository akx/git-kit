import subprocess

def run(command, ignore_errors=False):
	pipe = subprocess.Popen(command, stdout=subprocess.PIPE)
	output = pipe.communicate()[0].strip()
	if not ignore_errors:
		if pipe.returncode != 0:
			raise subprocess.CalledProcessError(pipe.returncode, command)
	return output

def yorn(prompt):
	return raw_input(prompt + " (y/N) > ").lower().startswith("y")