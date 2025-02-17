"""
This file is used to register the function apps with the Azure Functions host.
"""
import azure.functions as func
from barcodes_duplicate_scf import app as dupe

app = func.FunctionApp()
app.register_functions(dupe)
