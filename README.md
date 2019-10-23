# M - a software build tool

## usage:

```sh
#Make the project using meson, cmake, or make/autotools
m

#Run the project modifiying environmental arguments
CXX=clang++ m

#Run the project tests
m t

#pass arguments to the test script when using CMake to only run "python" tests
m t -c "-R python"

#Cleanup the project
m c

#Install the project
m i

#See configured settings
m s

#Build and run tests in a different build root using clang
CXX=clang++ CC=clang m -b build_clang t
```

M supports a configuration file written in JSON in the root of the repository.
Keys are the names of the options that show up in `m s`

For example, this file would set the command line options passed to the testing
command to run only python test cases:

```json
{
  "cmdline_test": ['-R', 'python']
}
```

The configuration file overridden defaults set by the plug-ins, and the configuration file is in turn overridden by command line arguments.
