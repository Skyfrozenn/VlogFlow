from flask import Flask
import os
from dotenv import load_dotenv
load_dotenv()
 

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] =  os.getenv("SECRET_KEY")



from .routers import (
    auth,
    entrance,
    profile,
    save_new_vlog
    
    
    
)
