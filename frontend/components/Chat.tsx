import React, {useState, useEffect, useRef} from 'react'
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Menu, MessageCircle, MoreVertical, Phone, Search, Send, Video } from 'lucide-react'
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"

const Chat = ({contact}) => {

    const [messages, setMessages] = useState([])
    const chatContainerRef = useRef(null);


    const scrollToBottom = () => {

        setTimeout(()=>{
            chatContainerRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' })
        }, 100)
        
    }

    useEffect(() => {

        scrollToBottom();
        
        
        if (contact && contact.phone_number) {
            fetchMessages(contact.phone_number);
        }
    
        // WebSocket setup
        const socket = new WebSocket("ws://localhost:9000/ws");
    
        socket.onopen = function () {
            console.log("WebSocket connection established");
        };
    
        socket.onerror = function (error) {
            console.error("WebSocket error observed:", error);
        };
    
        socket.onmessage = function (event) {
            const data = JSON.parse(event.data);
            const phoneNumber = data.phone_number;
            const newMessage = data.messages;
    
            if (phoneNumber === contact.phone_number) {
                setMessages((prevMessages) => [...prevMessages, newMessage]);
            }
            scrollToBottom();
        };
    
        socket.onclose = function () {
            console.log("WebSocket connection closed");
        };
    
        // Cleanup the WebSocket connection when the component unmounts
        return () => {
            socket.close();
        };
    }, [contact]);

    

    const fetchMessages = async (contactNumber) => {
        try {
        const response = await fetch('http://localhost:9000/messages-by-contact', {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json',
            },
            body: JSON.stringify({
            contact_number: contactNumber
            })
        })

        if (response.ok) {
            const data = await response.json()
            setMessages(data.messages) // assuming response has a messages array
            console.log(messages)
        } else {
            console.error('Failed to fetch messages')
        }
        } catch (error) {
        console.error('Error fetching messages:', error)
        }
    }

  return (
    
    <div className="flex-1 flex flex-col">
    <header className="bg-white border-b p-[22px] flex items-center justify-between">
      <div className="flex items-center space-x-4">
        {/* <Button variant="ghost" size="icon" className="md:hidden" onClick={toggleSidebar}>
          <Menu className="h-5 w-5" />
          <span className="sr-only">Toggle sidebar</span>
        </Button> */}
        <Avatar>
          <AvatarImage src={"/placeholder-user.jpg"} alt="Contact" />
          <AvatarFallback>C</AvatarFallback>
        </Avatar>
        <div>
          <h2 className="text-sm font-medium">{contact.phone_number}</h2>
          {/* <p className="text-xs text-gray-500">Online</p> */}
        </div>
      </div>
      {/* <div className="flex space-x-2">
        <Button variant="ghost" size="icon">
          <Video className="h-5 w-5" />
          <span className="sr-only">Video call</span>
        </Button>
        <Button variant="ghost" size="icon">
          <Phone className="h-5 w-5" />
          <span className="sr-only">Voice call</span>
        </Button>
        <Button variant="ghost" size="icon">
          <Search className="h-5 w-5" />
          <span className="sr-only">Search</span>
        </Button>
      </div> */}
    </header>
    <ScrollArea className="flex-1 p-4">
        <div ref={chatContainerRef}>
            {messages.map((message, i) => (
                <div
                key={i}
                className={`max-w-[70%] rounded-lg p-3 mb-2 ${
                    message.role === 'assistant' ? "bg-blue-500 text-white ml-auto" : "bg-white"
                }`}
                >
                <p className="text-sm">{message.content}</p>
                <span className="text-xs opacity-70 mt-1 block">
                    {/* {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} */}
                </span>
                </div>
            ))}
        </div>
    </ScrollArea>
    <div className="bg-white border-t p-4">
      <div className="flex items-center space-x-2">
        <Input placeholder="Type a message" className="flex-1" />
        <Button size="icon">
          <Send className="h-5 w-5" />
          <span className="sr-only">Send message</span>
        </Button>
      </div>
    </div>
  </div>
  )
}

export default Chat