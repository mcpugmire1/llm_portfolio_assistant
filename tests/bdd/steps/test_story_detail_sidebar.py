"""BDD steps for MATTGPT-212: story detail sidebar pill rendering.

Both scenarios open the Cendian story via deeplink and count pills against the
story's own field length. Counting against the fixture (not a hardcoded 15/28)
means a corpus edit to Cendian's Competencies or public_tags will re-baseline
the assertion instead of breaking it.
"""

from pytest_bdd import scenarios

scenarios("../features/story_detail_sidebar.feature")
