from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
import os.path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


taskAgent =" agent1qdztff7ua5dzwvlmfu5z48fgznd8z3xrfnpspw00frdnc0hw9r9g67lrw0a"

backend = ""

SCOPES = ['https://www.googleapis.com/auth/calendar']

class AgentRequest(Model):
    message: str

class AgentResponse(Model):
    message: str

class taskRequest(Model):
    message: str

class taskResponse(Model):
    message: str

class schedulerRequest(Model):
    message: str

class schedulerResponse(Model):
    message: str

OpenAIAgent = Agent(
    name="OpenAI Agent",
    port=8000,
    seed="OpenAI agent",
    endpoint=["http://127.0.0.1:8000/submit"],
)

# fund_agent_if_low(OpenAIAgent.wallet.address())

@OpenAIAgent.on_event('startup')
async def agent_details(ctx: Context):
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    ctx.logger.info(f'{OpenAIAgent.name} Address is {OpenAIAgent.address}')

@OpenAIAgent.on_query(model=AgentRequest, replies={taskRequest,AgentResponse})
async def from_backend(ctx: Context, sender: str, msg: AgentRequest):
    ctx.storage.set("sender", sender)
    try:
        ctx.logger.info(f"Received message from {sender}: {msg.message}")
        if msg.message == "read":
            data = msg.message
            ctx.logger.info(f"Send message to TaskAgent: {data}")
            await ctx.send(taskAgent, taskRequest(message=data))
        elif msg.message == "write":
            resp = "I am an AI agent. I can help you with your queries."
            await ctx.send(taskAgent, taskRequest(message=resp))
        else:
            resp = "nothing"
            await ctx.send(sender, AgentResponse(message=resp))
    except Exception as ex:
        ctx.logger.warning(ex)

@OpenAIAgent.on_message(model=taskResponse, replies={AgentResponse})
async def taskAgentReplie(ctx: Context, sender: str, msg: taskResponse):
    flask = ctx.storage.get("sender")
    try:
        data = msg.message
        ctx.logger.info(f"Received message from TaskAgent: {data}")
        await ctx.send(flask, AgentResponse(message=data))
    except Exception as ex:
        ctx.logger.warning(ex)

@OpenAIAgent.on_message(model=schedulerResponse, replies={AgentResponse})
async def taskAgentReplie(ctx: Context, sender: str, msg: schedulerResponse):
    flask = ctx.storage.get("sender")
    try:
        data = msg.message
        ctx.logger.info(f"Received message from Scheduler Agent: {data}")
        await ctx.send(flask, AgentResponse(message=data))
    except Exception as ex:
        ctx.logger.warning(ex)

if __name__ == "__main__":
    OpenAIAgent.run()