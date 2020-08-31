# oc_graphlib

### First steps
  1. Install Poetry:
``` bash
    pip install poetry
```
  2. Clone this repository:
``` bash
    git clone https://github.com/iosonopersia/oc_graphlib
    cd ./oc_graphlib
```
  3. Install all the dependencies:
``` bash
    poetry install
```
  4. Build the package (_output dir:_ `dist`):
``` bash
    poetry build
```
  5. Globally install the package (_alternatively, you can also install it inside a virtual-env,
  by providing the full path to the .tar.gz archive_):
``` bash
    pip install ./dist/oc_graphlib-<VERSION>.tar.gz
```
  6. If everything went the right way, than you should be able to use the `oc_graphlib` library in your Python modules as follows:
``` python
    from oc_graphlib.graph_set import GraphSet
    from oc_graphlib.agent_role import AgentRole
    # ...
```

### How to run the tests
Just run the following command inside the root project folder:
``` bash
    poetry run test
```

### How to manage the project using Poetry
See [Poetry commands documentation](https://python-poetry.org/docs/cli/).

### How to build the documentation
  1. Always remember to move inside the `docs` folder:
``` bash
    cd docs
```
  2. Use the Makefile provided to build the docs:
      + _on Windows_
        ```
            make.bat html
        ```
      + _on Linux and MacOs_
        ```
            make html
        ```
  3. Open the `build/html/index.html` file with a web browser of your choice!
