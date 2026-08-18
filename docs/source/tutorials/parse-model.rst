Parse a Model
=============

Use the public ``parse`` function to obtain diagnostics and an AST.

.. code-block:: python

   from pysysmlv2 import parse

   result = parse("package Demo { part def Vehicle; }")
   assert result.ok
   print(result.ast)
