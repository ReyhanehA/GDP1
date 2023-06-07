@@ -15,6 +15,7 @@
import json
import logging
import re

import attr
from frozendict import frozendict
@@ -26,6 +27,9 @@
logger = logging.getLogger(__name__)


def _reject_invalid_json(val):
 """Do not allow Infinity, -Infinity, or NaN values in JSON."""
 raise ValueError("Invalid JSON value: '%s'" % val)
@@ -158,25 +162,54 @@ def log_failure(failure, msg, consumeErrors=True):
 return failure


def glob_to_regex(glob):
 """Converts a glob to a compiled regex object.

    The regex is anchored at the beginning and end of the string.

    Args:
        glob (str)

    Returns:
 re.RegexObject
    """
 res = ""
 for c in glob:
 if c == "*":
 res = res + ".*"
 elif c == "?":
 res = res + "."
 else:
 res = res + re.escape(c)

 # \A anchors at start of string, \Z at end of string
 return re.compile(r"\A" + res + r"\Z", re.IGNORECASE)