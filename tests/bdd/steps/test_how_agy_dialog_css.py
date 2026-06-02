"""
BDD step bindings for How Agy Searches dialog CSS regression guards (MATTGPT-110).

Red (scenarios) commit: scenarios bound via scenarios() loader with NO step
definitions — every step resolves to undefined-step state.
"""

from pytest_bdd import scenarios

scenarios("../features/how_agy_dialog_css.feature")
