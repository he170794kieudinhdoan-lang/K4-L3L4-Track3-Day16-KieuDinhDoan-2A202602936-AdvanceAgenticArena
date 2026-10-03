import os
import subprocess
import _pytest.runner

# Fix 1: Windows subprocess default text encoding
_orig_run = subprocess.run

def _patched_run(*args, **kwargs):
    if kwargs.get("text") or kwargs.get("universal_newlines"):
        if "encoding" not in kwargs:
            kwargs["encoding"] = "utf-8"
            kwargs.setdefault("errors", "replace")
    return _orig_run(*args, **kwargs)

subprocess.run = _patched_run

# Fix 2: Windows os.environ 32767 character limit when test parameter strings are huge
_orig_update = _pytest.runner._update_current_test_var

def _patched_update_current_test_var(item, when):
    var_name = "PYTEST_CURRENT_TEST"
    if when:
        value = f"{item.nodeid} ({when})"
        value = value.replace("\x00", "(null)")
        if len(value) > 30000:
            value = value[:30000]
        os.environ[var_name] = value
    else:
        os.environ.pop(var_name, None)

_pytest.runner._update_current_test_var = _patched_update_current_test_var
