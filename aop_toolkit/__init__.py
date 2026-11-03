"""aop_toolkit: the reference toolchain for the observe, model, compile, execute pipeline.

Owns: SOP parsing to intent hypothesis, variant mining from observed cases,
decision-rule extraction with thresholds, AOP compilation, and linting.
The schema compiled to is owned by aop-spec; the graph mined from is owned
by aop-context-graph. Standard library only.
"""

__version__ = "0.1.0"
