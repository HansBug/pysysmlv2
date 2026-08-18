"""Placeholder for generic model queries used by downstream analyzers.

Future query helpers should accept the public semantic model rather than
generated parser contexts. Keeping this module as the query boundary lets
state-machine discovery code depend on stable model concepts when symbol
resolution is added.
"""
