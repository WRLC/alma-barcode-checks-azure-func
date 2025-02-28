"""
This file is used to register the function apps with the Azure Functions host.
"""
import dotenv
import azure.functions as func
from application.extensions import engine, Base

# import triggers
from application import scf_duplicate
from application import scf_no_x
from application import scf_no_row_tray
from application import scf_incorrect_row_tray
from application import scf_withdrawn
from application import iz_no_row_tray
from application import iz_incorrect_row_tray

# import db models
from application.models.analysis_sql import Analysis  # pylint: disable=unused-import  # noqa: F401
from application.models.area_sql import Area  # pylint: disable=unused-import  # noqa: F401
from application.models.iz_sql import Iz  # pylint: disable=unused-import  # noqa: F401
from application.models.key_sql import Key  # pylint: disable=unused-import  # noqa: F401
from application.models.recipient_sql import Recipient  # pylint: disable=unused-import  # noqa: F401
from application.models.trigger_sql import Trigger  # pylint: disable=unused-import  # noqa: F401
from application.models.user_sql import User  # pylint: disable=unused-import  # noqa: F401

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
