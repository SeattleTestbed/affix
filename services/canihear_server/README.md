# canihear_server

This directory contains the build configuration for "canihear" servers. 
See https://seattle.poly.edu/wiki/BuildInstructions for instructions 
on how to build.

After running the build scripts, you can `uploaddir` (in seash) the full 
build target directory to a Seattle VM that should run your "canihear" 
server. (The build target dir lacks the RepyV2 runtime, so you cannot 
run the server on your build machine from this dir.)


## Note

We assume that SeattleTestbed/affix has been checked out in full.

