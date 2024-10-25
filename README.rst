HGraph
======

A functional reactive programming engine with a Python front-end.

This provides a Domain Specific Language (DSL) and runtime to support the computation of results over time, featuring
a graph based directed acyclic dependency graph and the concept of time-series properties.
The language is function based, and promotes composition to extend behaviour.

Here is a simple example:

.. testcode:: python

    from hgraph import graph, run_graph, const
    from hgraph.nodes import debug_print

    @graph
    def main():
        a = const(1)
        c = a + 2
        debug_print("a + 2", c)

    run_graph(main)

Results in:

.. testoutput::

    [1970-01-01 00:00:00.000385][1970-01-01 00:00:00.000001] a + 2: 3


Development
-----------

The project is currently configured to make use of `Poetry <https://python-poetry.org>`_ for dependency management.
Take a look at the website to see how best to install the tool.

Here are some useful commands:

First, this will cause the virtual environment to be installed in the same folder as the project (in .venv folder)

.. code-block:: bash

    poetry config virtualenvs.in-project true

Use this command to set the version of Python to make use of if you want a specific version of Python.

.. code-block:: bash

    poetry env use 3.11

Then use the following command to install the project and its dependencies. Note that the ``--with docs`` installs
the dependencies to build the documentation set which is not required otherwise, also the ``--all-extras`` is only
required for the adaptors.

.. code-block:: bash

    poetry install --with docs --all-extras

If you did not use the first command, you can find the location of the installation using:

.. code-block:: bash

    poetry env info


PyCharm can make use of poetry to ``setup`` the project.

Run Tests
.........

.. code-block:: bash

    # No Coverage
    poetry run pytest

.. code-block:: bash

    # Generate Coverage Report
    poetry run pytest --cov=your_package_name --cov-report=xml

