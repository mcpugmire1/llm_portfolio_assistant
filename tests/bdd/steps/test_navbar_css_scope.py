"""
BDD step bindings for navbar CSS scope regression guard (MATTGPT-110 fix).

Red (scenarios) commit: scenarios bound via scenarios() loader with NO step
definitions — every step resolves to undefined-step state.
"""

from pytest_bdd import scenarios

scenarios("../features/navbar_css_scope.feature")
