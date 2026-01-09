import React, { useState, useEffect, useRef } from 'react';
import { io } from "socket.io-client";
import './ChatbotPage.css';

const socket = io("http://localhost:5000", {
  withCredentials: true,
});

const getUserId = () => {
  let id = localStorage.getItem("user_id");
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem("user_id", id);
  }
  return id;
};

const USER_ID = getUserId();

const Chatbot = () => {
  const [messages, setMessages] = useState([
    { id: 1, text: "Hello! Please type in your message!", sender: "bot" }
  ]);
  const [inputValue, setInputValue] = useState("");
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  socket.on("auth_required", () => {
    window.location.href = "http://localhost:5000/login";
  });

  /* Listen for bot messages */
  useEffect(() => {
    socket.on("bot_message", (data) => {
      // Replace the "..." bubble with the real message
      setMessages((prev) => {
        const lastMsg = prev[prev.length - 1];
        if (lastMsg?.text === "..." && lastMsg.sender === "bot") {
          const updated = [...prev];
          updated[updated.length - 1] = {
            id: Date.now(),
            text: data.message,
            sender: "bot"
          };
          return updated;
        } else {
          return [
            ...prev,
            { id: Date.now(), text: data.message, sender: "bot" }
          ];
        }
      });
    });

    return () => socket.off("bot_message");
  }, []);

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: inputValue,
      sender: "user"
    };

    setMessages((prev) => [...prev, userMessage]);

    // Add typing indicator for bot
    setMessages((prev) => [
      ...prev,
      { id: Date.now() + 1, text: "...", sender: "bot" }
    ]);

    // Send message to backend
    socket.emit("user_message", {
      user_id: USER_ID,
      message: inputValue
    });

    setInputValue("");
  };

  return (
    <div className="app-viewport">
      <div className="chatbot-layout">
        
        {/* Main Chat Window */}
        <div className="chat-window">
          <div className="chat-header">
            <span>Schedule Assistance</span>
          </div>

          <div className="message-list">
            {messages.map((msg) => (
              <div key={msg.id} className={`message-row ${msg.sender}`}>
                <div className="message-bubble">{msg.text}</div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Detached Footer Bar */}
        <form className="chat-footer" onSubmit={handleSendMessage}>
          <input 
            type="text" 
            className="chat-input-bar" 
            placeholder="Type a message..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
          />
          <button type="submit" className="chat-send-sq">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </form>

      </div>
    </div>
  );
};

export default Chatbot;