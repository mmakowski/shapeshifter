Shapeshifter
============

Shapeshifter is a tool for interacting with remote servers. It
consists of a controller script (`ssc`) and a set of modules which run
on the servers with which you want to interact. There is a small
set of core, bootstrap modules. All modules (including the bootstrap
ones) can be uploaded and replaced at run time. Use cases include:
* automatic deployment of applications built in a continuous
  integration environment
* monitoring and management of processes running on servers via a web
  interface


Quick Demo
----------

1. Make sure you have Python 2.7 installed
2. Clone `git://github.com/mmakowski/shapeshifter.git`
3. Copy the `bootstrap` directory to some temporary place on your
   computer and run `webserver.py` in there.
4. In the root of your clone run:
   * `ssc.py localhost PUT /ssmodule/hello module=file:modules/hello.py`
   * `ssc.py localhost POST /hello/World`

You can play around with modifying `modules/hello.py` and then
running the two `ssc` command above to update and execute it. 


How it Works
------------

Let's see what happens in the demo above:

1. `webserver.py` starts a process which listens for HTTP connections
   on port 5457.
2. `ssc.py` sends a `PUT` request to the listening process with URI
   `/ssmodule/hello` and body of type `multipart/form-data` containing
   the contents of `modules/hello.py` file.
3. The listener receives the request; it takes the first part of the
   URI, `ssmodule`, loads a module with this name and calls a `PUT()`
   function (corresponding to the HTTP method used) in it, passing in
   the remainder of the URI (`"hello"`) as an argument.
4. `ssmodule.PUT()` creates a file `hello.py` writing to it the
   content retrieved from the request body.
5. the second invocation of `ssc` sends a POST request with URI
   `/hello/World`.
6. The listener processes the requst by invoking `hello.POST()`
   function (defined in the module created in response to the previous
   request) and passing to it `"World"`.
7. `hello.POST()` prints the greeting on the standard output.


Usage
-----

    ssc.py <targets> <method> <URI> [<data>]

* `<targets>`: a comma-separated list of machines to which requests
  are to be sent.
* `<method>`: HTTP method; currently supported methods are `DELETE`,
  `GET`, `POST` and `PUT`. 
* `<URI>`: the URI to be requested. The first element of it (up to the
  first `/`) determines the module which will be invoked.
* `<data>`: a set of key-value pairs in the format:
  `<key_1>=<value_1>,...,<key_n>=<value_n>`. If a value is of the format
  `file:<path>` then the contents of file denoted by `<path>` will be
  sent.
