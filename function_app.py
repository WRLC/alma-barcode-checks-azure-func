"""
This file is used to register the function apps with the Azure Functions host.
"""
import azure.functions as func
from barcodes_duplicate_scf import app as dupe
from barcodes_no_x_scf import app as no_x_scf

app = func.FunctionApp()
app.register_functions(dupe)
app.register_functions(no_x_scf)
