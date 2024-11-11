from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
import datetime as dt

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar']


class taskRequest(Model):
    message: str

class taskResponse(Model):
    message: str

TaskAgent = Agent(
    name="Task Agent",
    port=8001,
    seed="Task agent",
    endpoint=["http://127.0.0.1:8001/submit"],
)

# fund_agent_if_low(TaskAgent.wallet.address())

@TaskAgent.on_event('startup')
async def agent_details(ctx: Context):
    ctx.logger.info(f'{TaskAgent.name} Address is {TaskAgent.address}')

@TaskAgent.on_message(model=taskRequest, replies={taskResponse})
async def query_handler(ctx: Context, sender: str, msg: taskRequest):
    creds = Credentials.from_authorized_user_file('token.json')
    try:
        ctx.logger.info(f"Received message : {msg.message}")
        service = build('calendar', 'v3', credentials=creds)
        now = dt.datetime.now().isoformat() + 'Z'
        event_result = service.events().list(calendarId='primary', timeMin=now, maxResults=10, singleEvents=True, orderBy='startTime').execute()
        events = event_result.get('items', [])
        if not events:
            ctx.logger.info('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            ctx.logger.info(f"Event: {event['summary']} starts at {start}")
        resp = events[0]['summary']
        ctx.logger.info(f"Sending message: {resp}")
        await ctx.send(sender, taskResponse(message=events))
    except Exception as ex:
        ctx.logger.warning(ex)

if __name__ == "__main__":
    TaskAgent.run()