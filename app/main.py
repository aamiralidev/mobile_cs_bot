import logging
import os
from contextlib import asynccontextmanager
import json
import openai
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from app.routers.chat import connect_to_db
from app.dependencies import database
from fastapi import HTTPException
from .routers import chat

from fastapi import Body, HTTPException
from pydantic import BaseModel

# Define a Pydantic model for the request body
class ContactRequest(BaseModel):
    contact_number: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Database connection has started successfully")

    # Initialize database connection
    await database.init_db()

    yield  # This point is where the FastAPI application runs

    # Close database connection
    await database.close_db_connection()

    logging.info("Database connection closed successfully")


load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")
print("key = ", str(os.environ.get("OPENAI_API_KEY")))


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)


templates = Jinja2Templates(directory="app/templates")


@app.get("/chat_interface")
async def chat_interface(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})  # noqa


@app.get("/")
async def root():
    return "Dan Chatbot api"

@app.get("/messages")
async def get_messages(request: Request):
    """Retrieve all conversations and display them on a webpage"""
    conn, cur = connect_to_db()
    try:
        # Fetch conversations from the database
        cur.execute("SELECT phone_number, messages FROM conversation_entries")
        conversations = cur.fetchall()
        # Structure the data for display
        conversation_data = []
        for conversation in conversations:
            # print(conversation)
            phone_number = conversation[0]
            messages = conversation[1]  # parse JSON messages
            print(messages)
            conversation_data.append({
                "phone_number": phone_number,
                "messages": messages
            })

        # Render the conversations in a webpage
        return templates.TemplateResponse("messages.html", {
            "request": request,
            "conversations": conversation_data
        })

    except Exception as e:
        conn.rollback()
        logging.error(f"Error retrieving messages: {e}")
        return {"error": "An error occurred while retrieving the messages"}

    finally:
        cur.close()
        conn.close()

@app.get("/contacts-list")
async def get_messages(request: Request):
    """Retrieve all conversations and display them on a webpage"""
    conn, cur = connect_to_db()
    try:
        # Fetch conversations from the database
        cur.execute("SELECT phone_number, messages FROM conversation_entries")
        conversations = cur.fetchall()
        # Structure the data for display
        contacts_list = []
        for conversation in conversations:
            # print(conversation)
            phone_number = conversation[0]
            messages = conversation[1]  # parse JSON messages
            unread_count = sum(1 for message in messages if message.get("read") == False)
            contacts_list.append({
                "phone_number": phone_number,
                "message": messages[len(messages)-1],
                "unread_count": unread_count,
                "timestamp": messages[len(messages)-1].get("timestamp", None)
            })
            contacts_list.sort(key=lambda x: (x['timestamp'] is None, x['timestamp']), reverse=True)
            
        # Render the conversations in a webpage
        return {"contacts_list": contacts_list}

    except Exception as e:
        conn.rollback()
        logging.error(f"Error retrieving messages: {e}")
        return {"error": "An error occurred while retrieving the messages"}

    finally:
        cur.close()
        conn.close()





@app.post("/messages-by-contact")
async def get_messages_by_contact(request: ContactRequest):
    """Retrieve all messages for a specific contact number."""
    contact_number = request.contact_number
    # print("Contact", contact_number)
    conn, cur = connect_to_db()
    try:
        # Fetch messages for the specified contact number
        cur.execute("SELECT messages FROM conversation_entries WHERE phone_number = %s", (contact_number,))
        result = cur.fetchone()

        if result:
            # Parse the messages from JSON
            messages = result[0]  # Ensure to load the JSON here
            
            # Mark all messages as read
            for message in messages:
                message["read"] = True

            # Update the messages back to the database
            cur.execute("UPDATE conversation_entries SET messages = %s WHERE phone_number = %s",
                        (json.dumps(messages), contact_number))
            conn.commit()
            
            return {"contact_number": contact_number, "messages": messages}
        else:
            raise HTTPException(status_code=404, detail="Contact not found")

    except Exception as e:
        logging.error(f"Error retrieving messages for {contact_number}: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving the messages")

    finally:
        cur.close()
        conn.close()

