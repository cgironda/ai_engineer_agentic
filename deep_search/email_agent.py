import os
from typing import Dict

# import sendgrid
# from sendgrid.helpers.mail import Email, Mail, Content, To
import sib_api_v3_sdk
from sib_api_v3_sdk import SendSmtpEmail
from sib_api_v3_sdk.rest import ApiException
from agents import Agent, function_tool


@function_tool
def send_email(subject: str, html_body: str) -> Dict[str, str]:
    """ Send out an email with the given subject and HTML body """
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = os.environ.get("BREVO_API_KEY")

    api_client = sib_api_v3_sdk.ApiClient(configuration)
    email_api = sib_api_v3_sdk.TransactionalEmailsApi(api_client)

    email = SendSmtpEmail(
        sender={"email": "cgirondat@gmail.com"},   # must be a verified sender
        to=[{"email": "max.andinux@gmail.com"}],
        subject="Sales email",
        text_content=html_body,
    )

    email_api.send_transac_email(email)
    return({"status": "success"})


INSTRUCTIONS = """You are able to send a nicely formatted HTML email based on a detailed report.
You will be provided with a detailed report. You should use your tool to send one email, providing the 
report converted into clean, well presented HTML with an appropriate subject line."""

email_agent = Agent(
    name="Email agent",
    instructions=INSTRUCTIONS,
    tools=[send_email],
    model="gpt-4o-mini",
)
