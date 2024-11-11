from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
import datetime as dt

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar']


class schedulerRequest(Model):
    message: str

class schedulerResponse(Model):
    message: str

schedulerAgent = Agent(
    name="Scheduler Agent",
    port=8001,
    seed="Scheduler agent",
    endpoint=["http://127.0.0.1:8001/submit"],
)

# fund_agent_if_low(TaskAgent.wallet.address())

@schedulerAgent.on_event('startup')
async def agent_details(ctx: Context):
    ctx.logger.info(f'{schedulerAgent.name} Address is {schedulerAgent.address}')

@schedulerAgent.on_message(model=schedulerRequest, replies={schedulerResponse})
async def query_handler(ctx: Context, sender: str, msg: schedulerRequest):
    creds = Credentials.from_authorized_user_file('token.json')
    try:
        service = build('calendar', 'v3', credentials=creds)
        event ={"summary": "Testing",
                "location": "Meerut",
                "description": "Test Description",
                "start": {"dateTime": "2024-11-14T16:00:00", "timeZone": "Asia/Kolkata"},
                "end": {"dateTime": "2024-11-14T17:00:00", "timeZone": "Asia/Kolkata"},
                "colorId": 3,
                "recurrence": ["RRULE:FREQ=DAILY;COUNT=1"],
                "attendees": [{"email": "dev.chauhan@fetch.ai"}],
        }
        event = service.events().insert(calendarId='primary', body=event).execute() 
        ctx.logger.info('Event created: %s' % (event.get('htmlLink')))
    except Exception as ex:
        ctx.logger.warning(ex)

if __name__ == "__main__":
    schedulerAgent.run()