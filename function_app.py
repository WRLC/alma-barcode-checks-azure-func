"""
This file is used to register the function apps with the Azure Functions host.
"""
import azure.functions as func
from BarcodesDuplicateScf import app as dupe

app = func.FunctionApp()
app.register_functions(dupe)
