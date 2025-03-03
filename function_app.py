"""
This file is used to register the function apps with the Azure Functions host.
"""
import dotenv
import azure.functions as func
from app.extensions import engine, Base

# import triggers
from app import scf_duplicate
from app import scf_no_x
from app import scf_no_row_tray
from app import scf_incorrect_row_tray
from app import scf_withdrawn
from app import iz_no_row_tray
from app import iz_incorrect_row_tray

# import db models
from app.models.analysis_sql import Analysis  # pylint: disable=unused-import  # noqa: F401
from app.models.area_sql import Area  # pylint: disable=unused-import  # noqa: F401
from app.models.iz_sql import Iz  # pylint: disable=unused-import  # noqa: F401
from app.models.apikey_sql import Apikey  # pylint: disable=unused-import  # noqa: F401
from app.models.recipient_sql import Recipient  # pylint: disable=unused-import  # noqa: F401
from app.models.azuretrigger_sql import Azuretrigger  # pylint: disable=unused-import  # noqa: F401
from app.models.user_sql import User  # pylint: disable=unused-import  # noqa: F401

dotenv.load_dotenv()  # Load environment variables from .env file

app = func.FunctionApp()  # Create a FunctionApp object

# Register the trigger functions
app.register_functions(scf_duplicate)
app.register_functions(scf_no_x)
app.register_functions(scf_no_row_tray)
app.register_functions(scf_incorrect_row_tray)
app.register_functions(scf_withdrawn)
app.register_functions(iz_no_row_tray)
app.register_functions(iz_incorrect_row_tray)

Base.metadata.create_all(engine)  # Create all tables in the database
