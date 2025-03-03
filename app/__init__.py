"""
app is used to register the function apps with the Azure Functions host.
"""
from app.triggers.scf_duplicate import app as scf_duplicate  # noqa: F401
from app.triggers.scf_no_x import app as scf_no_x  # noqa: F401
from app.triggers.scf_no_row_tray import app as scf_no_row_tray  # noqa: F401
from app.triggers.scf_incorrect_row_tray import app as scf_incorrect_row_tray  # noqa: F401
from app.triggers.scf_withdrawn import app as scf_withdrawn  # noqa: F401
from app.triggers.iz_no_row_tray import app as iz_no_row_tray  # noqa: F401
from app.triggers.iz_incorrect_row_tray import app as iz_incorrect_row_tray  # noqa: F401
