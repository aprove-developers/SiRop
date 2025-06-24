# Artifact SiRop for "Deciding Termination of Simple Randomized Loops"

Note that for reasons of simplicity SiRop only deals with rational values for the probability p.

## Run via Docker
The easiest way to run the artifact is to do so via Docker.
To that end, please load the provided docker image (see [“Releases”](https://github.com/aprove-developers/SiRop/releases)) by executing `docker load -i sirop-docker.tar.zst`.
You are then able to run the container and our included artifact via the command `docker run -t sirop-docker EXAMPLE` where `EXAMPLE` is a path to an input file for SiRop.
If you have trouble with loading the docker image, it might be helpful to first unpack the `.tar.zst` file (on linux run `zstd -d sirop-docker.tar.zst`) and then import the resulting `.tar` file by running `docker load -i sirop-docker.tar`.

The included examples can be found under the path `examples/EXAMPLE_NAME` (`/provided-examples` inside the docker container) where `EXAMPLE_NAME` is the name of the example from the table below.
So if you want to run SiRop via Docker on the `leading` example, then you can do so via executing `docker run -t sirop-docker /provided-examples/leading.sage`.

Moreover, it is possible to run SiRop on your own user-created examples.
To do so, you have to mount the corresponding folder into the docker container.
So if you have an example `my_example.sage` in a directory `/path/to/dir` you can run your example by executing `docker run -v /path/to/dir:/my-examples -t sirop-docker /my-examples/my_example.sage`. For example, to run SiRop on the leading example in the sub-directory `examples` of the current working directory, one can execute `docker run -v $(pwd)/examples:/my-examples -t sirop-docker /my-examples/leading.sage` (On Windows you have to replace `$(pwd)` with `$pwd` to refer to the current working directory.)

## Building & Running from Source
Note that we have only tested the following procedure on "x86_64-linux" systems.
Using the (flake-enabled) [Nix package manager](https://nixos.org/), you can "build" SiRop, i.e., ensure that the required dependencies are available, by executing `nix build .` from the `src/` folder of the artifact.
Then simply run `result/bin/sirop.py /path/to/example_file` to run SiRop on the example `example_file` under the path `/path/to`.
Alternatively, you can build and run SiRop in one step via `nix run`, i.e., by executing `nix run . -- /path/to/example`.

The provided docker image can also be built by Nix.
To that end, run `nix build '.#dockerImage'` and collect the created image as the target of the `result` symlink.

## Examples

We provide the following examples (and added comments on each example in the respective file).

| Name                       | PAST | Runtime |
|:---------------------------|:-----|:--------|
| `complex_terminating`      | Yes  | 3.8s    |
| `eps_example`              | No   | 3.1s    |
| `example1`                 | No   | 3.2s    |
| `example2`                 | Yes  | 3.0s    |
| `l_example`                | No   | 3.0s    |
| `leading`                  | No   | 3.3s    |
| `no_direction_terminating` | Yes  | 4.2s    |
| `r_example_n`              | No   | 3.0s    |
| `r_example`                | No   | 3.1s    |
| `tpdb_example`             | No   | 3.2s    |

The runtimes in the table above include the startup time of Sage inside of the docker container and that of the container itself.
SiRop was executed on an ordinary notebook (Intel i7-9750H, 32GB Ram).

Note that the TPDB example from which `tpdb_example` is derived includes the comment that the example is non-terminating over the integers (in the initial state `x=1,y=1`).
However, this comment is incorrect.
The program does terminate over the integers and the given initial state is clearly terminating.
