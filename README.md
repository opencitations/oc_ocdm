# oc_graphlib

### How to install the library on your machine
  1. Install Poetry:
``` bash
    pip install poetry
```
  2. Clone this repository:
``` bash
    git clone https://github.com/iosonopersia/oc_graphlib
    cd ./oc_graphlib
```
  3. Build and install the library with all its dependencies:
``` bash
    poetry build
    poetry install
```
  4. If everything went the right way, than you should be able to use the `oc_graphlib` library in your Python modules as follows:
``` python
    from oc_graphlib.graph_set import GraphSet
    from oc_graphlib.agent_role import AgentRole
    # ...
```
  5. Have fun!

### How to run the tests
Just run the following command inside the root project folder:
``` bash
    poetry run test
```

### How to manage the project using Poetry
See [Poetry commands documentation](https://python-poetry.org/docs/cli/).
