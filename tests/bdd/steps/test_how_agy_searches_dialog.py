"""
BDD step bindings for How Agy Searches @st.dialog migration (MATTGPT-110).

Red (scenarios) commit: scenarios bound via scenarios() loader with NO step
definitions — every step resolves to undefined-step state. Step definitions
land in the Red (step defs) commit; production code lands in Green.
"""

from pytest_bdd import scenarios

scenarios("../features/how_agy_searches_dialog.feature")
