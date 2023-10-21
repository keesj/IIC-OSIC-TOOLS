#!/usr/bin/env python3
# https://pypi.org/project/dockerfile-parse/
# pip install dockerfile-parse

"""
lxc-create -t download -n iic-test
# ubuntu
# jammy
# amd64

lxc-start -n iic-test
lxc-attach -n iic-test
cd
apt-get install -y git
#git clone --depth=1 https://github.com/iic-jku/iic-osic-tools.git
git clone https://github.com/keesj/IIC-OSIC-TOOLS.git -b keesj
cd IIC-OSIC-TOOLS/_build
pip install dockerfile-parse


cat <<END > .env

export CONTAINER_TAG=unknown
export IIC_OSIC_TOOLS_VERSION=${CONTAINER_TAG}
export DEBIAN_FRONTEND=noninteractive
export TZ=Europe/Vienna
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
export TOOLS=/foss/tools
export PDK_ROOT=/foss/pdks
export DESIGNS=/foss/designs
export EXAMPLES=/foss/examples
END

./docker_to_shell.py  > build.sh
apt-get install moretuils

./build.sh | ts | tee -a build.log

"""
from pprint import pprint
from dockerfile_parse import DockerfileParser
import json
import os.path

#
# Hacked script to convert the IIC-OSIC-TOOLS Dockerfile
# to a shell script. This script will only work on this
# file and nothing else !
#

# magic finds the Dockerfile
dfp = DockerfileParser()

y = json.loads(dfp.json)

#
# while converting from Docker to a shell script
# when we see a FROM we start a new shell until...
# we find either the first comment or a new FROM
in_subshell=0

print("#!/bin/bash")
print(". .env")
print("# debug scripts")
print("set -x")
print("# exit on failure")
print("set -e")

#
# This specific dockerfile uses COPY to copy the scripts to RUN
# and sometimes uses two scripts hence does 2 copies
# we just CD to the target directory but need to take 
# care to not change dirs a second time
changed_dir =0

# A counter to generate the function names
subshell_counter=0

# state variable to help determine when to close the generated function
found_run=0

for y in y:
    key = list(y.keys())[0]
    # ENV are mapped to export statements but.. overall should be in a .env file 
    if key == "ENV":
        print(f"export {y[key]}")
    if key == "COMMENT":
        # For nicer output we want to close the function before the 
        # start of the new comment but sometimes there are comments
        # in the middle of a run hence only closing the subshell 
        # we at least did run something
        if in_subshell == 1 and  found_run :
            print(")}")
            in_subshell =0
            found_run =0
        if y[key] == "Final output container":
            # we are done as we skip the final container
            print(f"# end base build steps")
            break
        print(f"#{y[key]}")
        # Dockker run commands are .. executed
    if key == "RUN":
        print(f" {y[key]}")
        found_run =1
        # From are ignored but we do create a new subshell and function
    if key == "FROM":
        if in_subshell == 1:
            print(")}")
            in_subshell =0
            found_run =0
        changed_dir = 0
        #print(f"# start {y[key]}")
        subshell_counter = subshell_counter +1
        print(f"step_{subshell_counter}(){{(")
        in_subshell=1
    if key == "COPY":
        #print(f"# HMM {y[key]}")
        if changed_dir == 0:
            base =  os.path.dirname(y[key].split(" ")[0])
            changed_dir = 1
            print(f" cd {base}")
    if key == "ARG":
        print(f" export {y[key]}")

print()
print("# Iterate of the the build steps")
print(f"subshell_counter={subshell_counter}")
print("for i in `seq 1 $subshell_counter`")
print("do")
print("  echo STEP $i")
print("  (step_$i)")
print("done")
