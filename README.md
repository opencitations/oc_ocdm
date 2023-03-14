# oc_ocdm
[<img src="https://img.shields.io/badge/powered%20by-OpenCitations-%239931FC?labelColor=2D22DE" />](http://opencitations.net)
[![Run tests](https://github.com/opencitations/oc_ocdm/actions/workflows/run_tests.yml/badge.svg)](https://github.com/opencitations/oc_ocdm/actions/workflows/run_tests.yml)
![Coverage](https://raw.githubusercontent.com/opencitations/oc_ocdm/master/oc_ocdm/test/coverage/coverage.svg)
[![Documentation Status](https://readthedocs.org/projects/oc-ocdm/badge/?version=latest)](https://oc-ocdm.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/oc-ocdm.svg)](https://badge.fury.io/py/oc-ocdm)
![PyPI](https://img.shields.io/pypi/pyversions/oc_meta)

[![DOI](https://zenodo.org/badge/322327342.svg)](https://zenodo.org/badge/latestdoi/322327342)
[![License: ISC](https://img.shields.io/badge/License-ISC-blue.svg)](https://opensource.org/licenses/ISC)

Documentation can be found here: [https://oc-ocdm.readthedocs.io](https://oc-ocdm.readthedocs.io).

**oc_ocdm** is a Python &ge;3.7 library that enables the user to import, produce, modify and export RDF data
structures which are compliant with the [OCDM v2.0.1](https://figshare.com/articles/Metadata_for_the_OpenCitations_Corpus/3443876) specification.

## User's guide
This package can be simply installed with **pip**:
``` bash
    pip install oc_ocdm
```
**Please, have a look at the notebooks [available here](https://github.com/opencitations/oc_ocdm/blob/master/notebooks/).**

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

**AAA: when adding a non-dev dependency via `poetry add`, always remember to add
that same dependency to the `autodoc_mock_imports` list in `docs/source/conf.py`**
(otherwise "Read the Docs" won't be able to compile the documentation correctly!).

### How to publish the package onto Pypi
``` bash
    poetry publish --build
```
### Install dependencies needed for the documentation
``` bash
    pip install Sphinx sphinx_rtd_theme
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

## Citation
If you are using or extending `oc_ocdm` as part of a scientific publication, we would appreciate a citation of our [article](https://link.springer.com/chapter/10.1007/978-3-031-06981-9_18).

```bibtex
@inproceedings{persiani2022programming,
  title={{A} {P}rogramming {I}nterface for {C}reating {D}ata {A}ccording to the {SPAR} {O}ntologies and the {O}pen{C}itations {D}ata {M}odel},
  author={Persiani, Simone and Daquino, Marilena and Peroni, Silvio},
  booktitle={The Semantic Web: 19th International Conference, ESWC 2022, Hersonissos, Crete, Greece, May 29--June 2, 2022, Proceedings},
  pages={305--322},
  year={2022},
  organization={Springer}
}
```

## Acknowledgements
This work has been funded by the project “Open Biomedical Citations in Context Corpus”
(Wellcome Trust, Grant n. 214471/Z/18/Z) and the project “Wikipedia Citations in Wikidata”
(Wikimedia Foundation, https://meta.wikimedia.org/wiki/Wikicite/grant/Wikipedia_Citations_in_Wikidata).

We would like to thank (in alphabetic order) Fabio Mariani (@FabioMariani), Arcangelo
Massari (@arcangelo7), and Gabriele Pisciotta (@GabrielePisciotta) for the constructive feedback.
