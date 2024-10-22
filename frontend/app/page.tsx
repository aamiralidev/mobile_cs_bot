'use client'

import { useState, useEffect } from "react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Menu, MessageCircle, MoreVertical, Phone, Search, Send, Video } from 'lucide-react'
import Chat from "@/components/Chat"

export default function Home() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)

  const [contacts, setContacts] = useState([])
  const [selectedChat, setSelectedChat] = useState(null)

  // Inside the Home component
  const handleChatSelect = (contact: any) => {
    setSelectedChat(contact); // Set the selected chat to the clicked contact
  }

  useEffect(() => {
    fetchContacts();

    // Websocket logic.
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
        console.log(data)
        const phoneNumber = data.phone_number;
        const newMessage = data.messages;

        fetchContacts();

        // if (phoneNumber === contact.phone_number) {
        //     // setMessages((prevMessages) => [...prevMessages, newMessage]);
        // }
        // scrollToBottom();
    };

    socket.onclose = function () {
        console.log("WebSocket connection closed");
    };

    // Cleanup the WebSocket connection when the component unmounts
    return () => {
        socket.close();
    };
    
  }, [])

  function fetchContacts(){
    fetch('http://localhost:9000/contacts-list')
      .then((res) => res.json())
      .then((data) => {
        setContacts(data.contacts_list)
        // console.log(data.contacts_list)
      })
  }

  const toggleSidebar = () => setIsSidebarOpen(!isSidebarOpen)

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div
        className={`bg-white w-full max-w-sm border-r ${
          isSidebarOpen ? "block" : "hidden"
        } md:block`}
      >
        <div className="p-4 border-b">
          {/* <div className="flex items-center justify-between">
            <Avatar>
              <AvatarImage src="/placeholder-user.jpg" alt="User" />
              <AvatarFallback>U</AvatarFallback>
            </Avatar>
            <div className="flex space-x-2">
              <Button variant="ghost" size="icon">
                <MessageCircle className="h-5 w-5" />
                <span className="sr-only">New chat</span>
              </Button>
              <Button variant="ghost" size="icon">
                <MoreVertical className="h-5 w-5" />
                <span className="sr-only">More options</span>
              </Button>
            </div>
          </div> */}
          <div className="mt-4 relative">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input placeholder="Search or start new chat" className="pl-8" />
          </div>
        </div>
        <ScrollArea className="h-[calc(100vh-129px)]">
          {contacts.map((contact, i) => (
            <div key={i} className="flex items-center space-x-4 p-4 hover:bg-gray-100 cursor-pointer" onClick={() => handleChatSelect(contact)}>
              <Avatar>
                <AvatarImage src={`https://w7.pngwing.com/pngs/124/934/png-transparent-computer-icons-person-avatar-heroes-black-avatar.png`} alt={`Contact ${i + 1}`} />
                <AvatarFallback>{contact.phone_number}</AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">{contact.phone_number}</p>
                <p className="text-sm text-gray-500 truncate">{contact.message.content}</p>
              </div>
              <span className="text-xs text-gray-400">3:14 PM</span>
            </div>
          ))}
        </ScrollArea>
      </div>

      { selectedChat ? <>
        <Chat key={selectedChat.phone_number} contact={selectedChat} />
      </> : <>
              
        <div className="flex-1 flex flex-col">
          <Button variant="ghost" size="icon" className="md:hidden" onClick={toggleSidebar}>
            <Menu className="h-5 w-5" />
            <span className="sr-only">Toggle sidebar</span>
          </Button>
          <div className="flex-1 flex items-center justify-center">
            Please select a chat to view the messages
          </div>
        </div>
            
      </>}

      
    </div>
  )
}