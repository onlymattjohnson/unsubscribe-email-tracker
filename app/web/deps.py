from fastapi import Request
from fastapi.templating import Jinja2Templates
from typing import Optional

# Initialize templates once
templates = Jinja2Templates(directory="app/templates")

def get_templates(request: Request):
    """Dependency to get templates with request context."""
    return templates