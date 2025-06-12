import csv
import io
from typing import Iterable, List, Dict, Any

from fastapi.responses import JSONResponse, StreamingResponse

from app.models import UnsubscribedEmail

def generate_csv_stream(data_iterator: Iterable[UnsubscribedEmail]) -> StreamingResponse:
    """
    Creates a streaming response for a CSV file from a data iterator.
    """
    def stream_generator():
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        
        headers = ["sender_name", "sender_email", "unsub_method", "inserted_at"]
        writer.writerow(headers)
        buffer.seek(0)
        yield buffer.read()
        buffer.seek(0)
        buffer.truncate(0)

        for item in data_iterator:
            writer.writerow([
                item.sender_name,
                item.sender_email,
                item.unsub_method,
                item.inserted_at.isoformat()
            ])
            buffer.seek(0)
            yield buffer.read()
            buffer.seek(0)
            buffer.truncate(0)

    filename = "unsubscribed_emails_export.csv"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    
    return StreamingResponse(
        stream_generator(), 
        media_type="text/csv",
        headers=headers
    )

def generate_json_response(data_list: List[Dict[str, Any]]) -> JSONResponse:
    """
    Creates a JSON response for an export.
    """
    filename = "unsubscribed_emails_export.json"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    
    return JSONResponse(content=data_list, headers=headers)