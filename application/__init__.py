"""
application is used to register the function apps with the Azure Functions host.
"""
from application.triggers.scf_duplicate import app as scf_duplicate
from application.triggers.scf_no_x import app as scf_no_x
from application.triggers.scf_no_row_tray import app as scf_no_row_tray
from application.triggers.scf_incorrect_row_tray import app as scf_incorrect_row_tray
from application.triggers.scf_withdrawn import app as scf_withdrawn
from application.triggers.iz_no_row_tray import app as iz_no_row_tray
from application.triggers.iz_incorrect_row_tray import app as iz_incorrect_row_tray
