import json
import logging
import os

import psycopg2
from fastapi import APIRouter, Form, Request
from fastapi.responses import PlainTextResponse
from twilio.twiml.messaging_response import MessagingResponse

from app.dependencies.utils import create_chat_completion
from app.internal.prompt import Initial_prompt
from fastapi import WebSocket, WebSocketDisconnect
from typing import List
from datetime import datetime, timezone


# Keep track of connected clients
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, phone_number: str, messages: List[dict], websocket: WebSocket):
        """Send a structured message containing phone number and message list to a specific client."""
        message_payload = {
            "contact_number": phone_number,
            "messages": messages
        }
        await websocket.send_json(message_payload)

    async def broadcast(self, phone_number: str, response_dict: dict):
        """Broadcast a structured message to all connected clients."""
        message_payload = {
            "phone_number": phone_number,
            "response_dict": response_dict
        }
        for connection in self.active_connections:
            await connection.send_json(message_payload)


manager = ConnectionManager()

router = APIRouter()



# Environment variables
DB_NAME = os.getenv("DB_USER")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


def connect_to_db():
    """Create and return a database connection and cursor."""
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,  # noqa
    )
    cur = conn.cursor()
    return conn, cur

# WebSocket endpoint for real-time communication
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # WebSocket needs to keep the connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logging.error(f"WebSocket Error: {e}")
        await websocket.close()

        
        
@router.post("/recieve/sms")
async def incoming_sms(
    request: Request, Body: str = Form(None), From: str = Form(None)
):
    """Send a dynamic reply to an incoming text message"""
    from_number = From
    message = Body

    if not message or not from_number:
        return {"error": "Invalid request"}

    conn, cur = connect_to_db()

    try:
        # Check if conversation exists
        cur.execute(
            "SELECT messages FROM conversation_entries WHERE phone_number = %s",  # noqa
            (from_number,),
        )
        result = cur.fetchone()

        user_message_data = {"role": "user", "content": message, "read": False, "timestamp": datetime.now(timezone.utc).isoformat()}
        if result:
            # Append the message to existing conversation
            conversation_messages = result[0]
            conversation_messages.append(user_message_data)
            cur.execute(
                "UPDATE conversation_entries SET messages = %s WHERE phone_number = %s",  # noqa
                (json.dumps(conversation_messages), from_number),
            )
        else:
            # Create a new conversation
            initial_prompt = Initial_prompt()
            conversation_messages = initial_prompt + [
                user_message_data
            ]
            cur.execute(
                "INSERT INTO conversation_entries (phone_number, messages) VALUES (%s, %s)",  # noqa
                (from_number, json.dumps(conversation_messages)),
            )

        conn.commit()

        await manager.broadcast(from_number, user_message_data)
        
        # Generate the response from the bot
        message_content, response_dict = await create_chat_completion(
            conversation_messages
        )

        if message_content == "Exception":
            return PlainTextResponse(
                "Request Failed", media_type="application/xml"
            )  # noqa

        # Append the bot response to the conversation
        response_dict["read"] = False
        response_dict["timestamp"] = datetime.now(timezone.utc).isoformat()
        
        conversation_messages.append(response_dict)
        cur.execute(
            "UPDATE conversation_entries SET messages = %s WHERE phone_number = %s",  # noqa
            (json.dumps(conversation_messages), from_number),
        )

        conn.commit()

        # Broadcast the new message to WebSocket clients
        await manager.broadcast(from_number, response_dict)
        
        # print(type(response_dict))
        
        # Start our TwiML response
        resp = MessagingResponse()
        resp.message(message_content)

        return PlainTextResponse(str(resp), media_type="application/xml")

    except Exception as e:
        conn.rollback()
        logging.error(f"Error: {e}")
        return {"error": "An error occurred while processing the message"}

    finally:
        cur.close()
        conn.close()


