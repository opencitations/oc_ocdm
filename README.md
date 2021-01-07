# oc_ocdm
[![Documentation Status](https://readthedocs.org/projects/oc-ocdm/badge/?version=latest)](https://oc-ocdm.readthedocs.io/en/latest/?badge=latest)

Documentation can be found here: [https://oc-ocdm.readthedocs.io](https://oc-ocdm.readthedocs.io).

**oc_ocdm** is a Python &ge;3.7 library that enables the user to import, produce, modify and export RDF data
structures which are compliant with the [OCDM v2.0.1](https://figshare.com/articles/Metadata_for_the_OpenCitations_Corpus/3443876) specification.

## User's guide
This package can be simply installed with **pip**:
``` bash
    pip install oc_ocdm
```

## Developer's guide

### First steps
  1. Install Poetry:
``` bash
    pip install poetry
```
  2. Clone this repository:
``` bash
    git clone https://github.com/iosonopersia/oc_ocdm
    cd ./oc_ocdm
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
    pip install ./dist/oc_ocdm-<VERSION>.tar.gz
```
  6. If everything went the right way, than you should be able to use the `oc_ocdm` library in your Python modules as follows:
``` python
    from oc_ocdm.graph import GraphSet
    from oc_ocdm.graph.entities.bibliographic import AgentRole
    # ...
```

### How to run the tests
Just run the following command inside the root project folder:
``` bash
    poetry run test
```

### How to manage the project using Poetry
See [Poetry commands documentation](https://python-poetry.org/docs/cli/).

### How to publish the package onto Pypi
``` bash
    poetry publish --build
```

### How to generate the documentation
``` bash
    rm ./docs/source/modules/*
    sphinx-apidoc  -o ./docs/source/modules oc_ocdm *test*
```

### How to build the documentation
___
**Warning! In order to avoid getting the following `WARNING: html_static_path entry '_static' does not exist`, you'll
need to manually create an empty `_static` folder with the command:**
``` bash
    mkdir docs/source/_static
```
___
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
