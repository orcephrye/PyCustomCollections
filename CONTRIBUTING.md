# Contributing and Development

We are welcome and open to suggestions and code contributions. Below are some guidelines and development 
tips.

## Development on Github

* We use Github actions to do a finial check on all PRs to Main. 
* Main is a protected branch and all PRs must be approved by code owner. 
* It would be best practice to first open an Issue to discuss changes.


## Python with Hatch

This code base use [Hatch](https://hatch.pypa.io/latest/) to manage the environments, run tests etc. A hopeful
contributor is expected to be able to use hatch for testing/type checking/linting and so on.

Below is a small setup guide for using hatch with this repo.

### Setup Hatch.

The version of Python you install hatch onto isn't important, although it is suggested to use the latest officially 
supported version. The installation guide is here: https://hatch.pypa.io/latest/install/ 

```bash
python -m pip install hatch
```

Once you have hatch installed in your preferred pythong environment you can set up a new environment within the 
repo that you have cloned. 

```bash
python -m hatch new --init
```

This reads the prproject.toml to configure a new virtual python environment. You can enter this environment with
the following command.

```bash
python -m hatch shell
```

Hatch will attempt to make multiple environments for each Python version this repo supports. Currently, that
is Python 3.8 through 3.11. 'hatch shell' enters the default environment, but you can get a list of all environments
with the following command within an initialized repo.

```bash
hatch env show
```

You can enter the shell or run a command on a specific environment with the environment flag: '--evn'

```bash
hatch --env test.py3.10 shell
```

### Running hatch commands

Once you have a hatch environment setup within the repo you can run the pre-built commands which is the primary
purpose of this tool.

To run a command on the default environment simply do 'hatch run command'. Commands are also known as 'Scripts'
within hatch. They are pre-configured bash commands in pyproject.toml setup by the repo maintainer. 

Examples:
```bash
hatch run lint
hatch run typing
hatch run test
```

The scripts lint/typing/test leave cache files behind that can be cleaned like so:

```bash
hatch run lint-clean
hatch run typing-clean
hatch run test-clean
```

The above commands run against the default environment. But there are a number of test environments. To run
against them, you can do the following. This will run against all test environments in serial.

```bash
hatch run test:test
hatch run test:lint
hatch run test:typing
```

To clean you can simply run:

```bash
hatch run test:clean
```

### Testing Documentation

Hatch with [Portray](https://timothycrosley.github.io/portray/) makes it easy to test and deploy documentation.

```bash
hatch run docs:test
```

To clean docs simply use the clean script.

```bash
hatch run docs:clean
```

## Expectations 

We expect that a person who wants to make a code contribution has used hatch to run test:all successfully. And 
within the default hatch environment ran linting/type checking/testing. 

Also, we wish to maintain testing code coverage as current or even better levels. Any additional code will also 
require additional tests using PyTest located inside the 'tests' directory.