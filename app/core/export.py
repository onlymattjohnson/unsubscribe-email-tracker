import csv
import io
from typing import Iterable, List, Dict, Any

from fastapi import Response
from fastapi.responses import JSONResponse, StreamingResponse

from app.models import UnsubscribedEmail

def generate_csv_stream(data_list: List[Dict[str, Any]]) -> Response:
    """
    Creates a streaming response for a CSV file from a list of data.
    """
    buffer = io.StringIO()
    # Add 'id' to the fieldnames list to match the data
    fieldnames = ["id", "sender_name", "sender_email", "unsub_method", "inserted_at"]
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    
    writer.writeheader()
    writer.writerows(data_list)
    
    # Get the complete CSV as a single string
    output_string = buffer.getvalue()
    
    filename = "unsubscribed_emails_export.csv"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    
    # Return a normal Response object with the full content
    return Response(content=output_string, media_type="text/csv", headers=headers)

def generate_json_response(data_list: List[Dict[str, Any]]) -> JSONResponse:
    """
    Creates a JSON response for an export.
    """
    filename = "unsubscribed_emails_export.json"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    
    return JSONResponse(content=data_list, headers=headers)