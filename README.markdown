Shapeshifter
============

Shapeshifter is a tool for interacting with remote servers. It
consists of a controller script (`ssc`) and a set of modules which run
on the servers with which you want to interact. There is a small
set of core, bootstrap modules. All modules (including the bootstrap
ones) can be uploaded and replaced at run time.


Quick Demo
----------

1. Clone `git://github.com/mmakowski/shapeshifter.git`
2. Copy the `bootstrap` directory to some temporary place on your
   computer and run `webserver.py` in there.
3. In the root of your clone run:

	ssc.py localhost PUT /ssmodule/hello module=file:modules/hello.py
	ssc.py localhost POST /hello/World

You can play around with modifying `modules/hello.py` and then
running the two `ssc` command above to update and execute it. 
