from flask import Flask, jsonify, request
from flask_cors import CORS
from uagents.query import query
from uagents import Model
import asyncio
import json

app = Flask(__name__)
CORS(app)

Agent = 'agent1qtyaqr697kjft7y77w4k5q9mndfzntws2uh9q3m3f936qhfth5d3vvjlsqm'

class AgentRequest(Model):
    message: str

class AgentResponse(Model):
    message: str

@app.route('/search', methods=['POST'])
def post():
    new_entry = request.json
    prompt = new_entry.get('message', None)
    response = asyncio.run(contactAgent(prompt))
    print(response)
    return jsonify(response['message'])

async def contactAgent(prompt):
    req = AgentRequest(message=prompt)
    response = await query(destination=Agent, message=req, timeout=15.0)
    print(response)
    data = json.loads(response.decode_payload())
    return data

if __name__ == "__main__":
    app.run(debug=True, port=8080)
