from fastapi import HTTPException, Request, status
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from jinja2 import Environment, PackageLoader, select_autoescape
from pydantic import EmailStr

import hashlib
import random
import string

from models.config import settings
from tables import users
from database import database


env = Environment(
    loader=PackageLoader('utils', 'html_templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


class Email:
    def __init__(self, name: str, url: str, email: EmailStr):
        self.name = name
        self.sender = 'C-Elect <admin@celect.com>'
        self.mail = email
        self.url = url


    async def send_mail(self, subject, template):
        # Define the config
        conf = ConnectionConfig(
            MAIL_USERNAME=settings.EMAIL_USERNAME,
            MAIL_PASSWORD=settings.EMAIL_PASSWORD,
            MAIL_FROM=settings.EMAIL_FROM,
            MAIL_PORT=settings.EMAIL_PORT,
            MAIL_SERVER=settings.EMAIL_HOST,
            MAIL_SSL_TLS= False,
            MAIL_STARTTLS= True,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )
        # Generate the HTML template base on the template name
        template = env.get_template(f'{template}.html')

        html = template.render(
            url=self.url,
            first_name=self.name,
            subject=subject
        )

        # Define the message options
        message = MessageSchema(
            subject=subject,
            recipients=[self.mail],
            body=html,
            subtype="html"
        )

        # Send the email
        fm = FastMail(conf)
        await fm.send_message(message)

    async def send_verification_code(self):
        await self.send_mail('Email Verification', 'verification')


async def mail_to(username:str, user_mail:str, request:Request):
    try:
        token = random.randbytes(10)
        hashed_code = hashlib.sha256()
        hashed_code.update(token)
        verification_code = hashed_code.hexdigest()
        # ts = datetime.timestamp(datetime.now())
        # verification_code = get_random_digit(16) + str(int(ts))
        query = users.update().where(users.c.email == user_mail).values(
            verification_code = verification_code
        )
        await database.execute(query)

        url = f"{request.url.scheme}://{request.client.host}:{request.url.port}/auth/verify_user/{token.hex()}"
        await Email(username, url, user_mail).send_verification_code()
    except Exception as error:
        print('Error', error)
        query = users.update().where(users.c.email == user_mail).values(
            verification_code = None
        )
        await database.execute(query)
        
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='An error occured while sending email')
    return {'message': 'Verification token successfully sent to your email'}



async def verify(token: str):
    hashed_code = hashlib.sha256()
    hashed_code.update(bytes.fromhex(token))
    verification_code = hashed_code.hexdigest()

    query = users.select().where(users.c.verification_code  == verification_code)
    user = await database.fetch_one(query)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid code or user doesn't exist")
    if user.verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='Your email adress has already been verified. Email can only be verified once!')
    query = users.update().where(users.c.verification_code  == verification_code).values(
            verification_code = None,
            verified = True
        )
    await database.execute(query)
    
    return "Your account is verified successfully ! You can log in"


# get random string of letters and digits
def get_random_digit(l):
    source = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(source) for _ in range(l)))
    return result_str