from fastapi import APIRouter, Form, HTTPException, status
import re

from utils.customException import EmailSyntaxeError
from utils.email import get_in_touch

EMAIL_PATTERN = re.compile("^[\w\-\.]+@([\w]+\.)+[\w]{2,4}$")

router = APIRouter()

# For user sign up
@router.post("/get_in_touch", status_code=status.HTTP_200_OK)
async def contact_admin(fullname:str = Form(...), email:str = Form(...), message:str = Form(...)):
    if not re.match(EMAIL_PATTERN, email):
        raise EmailSyntaxeError()
    try:
        message = await get_in_touch(fullname, email, message)
        return {"message" : message}
    except Exception as e:
        print(e)
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


