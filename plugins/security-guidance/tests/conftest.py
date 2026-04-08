# conftest.py – prevents pytest from traversing up into the `security-guidance`
# directory (which contains a hyphen and is not a valid Python package name).
# By placing this file here without an __init__.py in the parent, pytest
# treats this directory as a rootdir for collection.
