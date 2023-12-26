Quick Start
===========

The minimum python version currently supported is Python 3.11.

Use pip to install the hgraph package:

```bash
pip install hgraph
```

Now try the hello world example:

[hello world](hello_world.md)

You have now successfully run your first HGraph program.

Note: All examples are also available as python scripts in the docs/quick_start folder of the
project. This is great to try out the examples and play around with them.

Next, let's take a look as simple [graph and nodes](graphs_and_nodes.md).

A design principle of HGraph is that code should be built from small reusable nodes, with 
business logic being largely implemented using graph wiring. The nodes should be
well described in terms of pre- and post-conditions, and should be well tested.
To facilitate this, HGraph provides a set of helpful tools to make node testing easy.

[Testing nodes](node_testing.md).

The type system also supports the concept of generics. Generics are a useful way to 
describe a generic type. The generic types describe the constraints that the function
can support. For more information on generics, see the [generics](generics.md) page.

Nodes support life-cycle methods, namely start and stop. These methods are called when
the node is started prior to evaluation and when the node is stopped after evaluation.

Here are details on the [life-cycle](life_cycle.md) methods.

Next steps, we take a look at some of the more advanced features of node construction.

[Using injectable attributes](injectable_attributes.md).

Now we take a look at some of the more advance graph wiring features.

[map_, reduce, switch](map_reduce_switch.md).


