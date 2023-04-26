import subprocess


def getDependencies(name: str) -> dict:
    a = subprocess.run(
        ["npm-remote-ls", "-e", name],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    dep = str(a.stdout).strip().replace("\\n", " ").split(" ")
    dependencies = {}
    if "loading:" in dep:
        for i in range(2, len(dep)):
            if i != 2 and dep[i - 1] != "loading:" and dep[i] != "loading:":
                break
            if dep[i] != "loading:":
                tmp = dep[i].split("@")
                dependencies[tmp[0]] = tmp[1]
    return dependencies
