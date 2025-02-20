"""
This file is used to register the function apps with the Azure Functions host.
"""
import azure.functions as func
from app.barcodes_duplicate_scf import app as dupe
from app.barcodes_incorrect_row_tray_scf import app as incorrect_row_tray_scf
from app.barcodes_no_row_tray_scf import app as no_row_tray_scf
from app.barcodes_no_x_scf import app as no_x_scf

app = func.FunctionApp()
app.register_functions(dupe)
app.register_functions(incorrect_row_tray_scf)
app.register_functions(no_row_tray_scf)
app.register_functions(no_x_scf)
