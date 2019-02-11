## DOT to PseudoC converter

This tool will convert graphviz DOT files to PseudoC programs.

### Installation

The tool depends on [dot_tools library](https://github.com/timtadh/dot_tools) so you need to install it first.

**Python 3 note:** dot_tools requires Python 2, so the easiest way is to set up Python 2 virtual environment like this:

```
virtualenv --python=$(which python2) env
source env/bin/activate
pip install -e git+https://github.com/timtadh/dot_tools#egg=dot_tools
```

### Usage

```
python dot2pseudoc.py test_graphs/gr1.dot
```
or

```
python dot2pseudoc.py test_graphs/gr1.dot -o prog1.lst
```
