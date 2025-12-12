import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  Avatar,
  Chip,
  Fab,
  Tooltip,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
  MoreVert as MoreIcon,
  Psychology as PsychologyIcon,
  Code as CodeIcon,
  Help as HelpIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

const Chat = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your AI mentor. I'm here to help you with robotics, programming, and learning. What would you like to explore today?",
      sender: 'bot',
      timestamp: new Date(),
      type: 'text',
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage = {
      id: messages.length + 1,
      text: inputValue,
      sender: 'user',
      timestamp: new Date(),
      type: 'text',
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    try {
      // Simulate API call - replace with actual backend integration
      await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));

      const botResponse = {
        id: messages.length + 2,
        text: generateBotResponse(inputValue),
        sender: 'bot',
        timestamp: new Date(),
        type: 'text',
      };

      setMessages(prev => [...prev, botResponse]);
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage = {
        id: messages.length + 2,
        text: "I'm sorry, I encountered an error. Please try again or check if the backend is running.",
        sender: 'bot',
        timestamp: new Date(),
        type: 'error',
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const generateBotResponse = (userInput) => {
    const input = userInput.toLowerCase();

    if (input.includes('python') || input.includes('programming')) {
      return "Great question about programming! Python is an excellent language for robotics. Would you like me to help you with:\n\n• Setting up your development environment\n• Learning basic Python syntax\n• Working with robotics libraries like ROS\n• Building your first robot control script";
    }

    if (input.includes('robot') || input.includes('hardware')) {
      return "Robotics is fascinating! Let's break this down:\n\n• **Hardware**: Microcontrollers (Arduino, Raspberry Pi), sensors, motors\n• **Software**: Control algorithms, computer vision, machine learning\n• **Integration**: ROS (Robot Operating System), embedded programming\n\nWhat aspect interests you most?";
    }

    if (input.includes('learn') || input.includes('start')) {
      return "Perfect! Let's create a personalized learning path for you. I'll assess your current skills and goals to recommend the best starting point.\n\nCould you tell me:\n• Your current programming experience\n• Specific robotics interests (drones, autonomous vehicles, industrial robots, etc.)\n• How much time you can dedicate weekly";
    }

    return "That's an interesting topic! I'm here to help you learn about robotics, programming, AI, and related technologies. Feel free to ask me about:\n\n• Programming languages and frameworks\n• Robotics hardware and software\n• Machine learning and AI concepts\n• Career guidance in tech\n• Learning resources and projects\n\nWhat would you like to explore?";
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const handleMenuClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const quickActions = [
    { label: 'Explain Python basics', icon: <CodeIcon />, action: () => setInputValue('Explain Python basics for robotics') },
    { label: 'ROS tutorial', icon: <PsychologyIcon />, action: () => setInputValue('Guide me through ROS setup') },
    { label: 'Project ideas', icon: <HelpIcon />, action: () => setInputValue('Suggest beginner robotics projects') },
  ];

  const MessageBubble = ({ message }) => (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.3 }}
      style={{
        display: 'flex',
        marginBottom: '16px',
        justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
      }}
    >
      <Box
        sx={{
          display: 'flex',
          alignItems: 'flex-start',
          maxWidth: '70%',
          gap: 1,
        }}
      >
        {message.sender === 'bot' && (
          <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
            <BotIcon sx={{ fontSize: 18 }} />
          </Avatar>
        )}

        <Paper
          elevation={1}
          sx={{
            p: 2,
            backgroundColor: message.sender === 'user' ? 'primary.main' : 'background.paper',
            color: message.sender === 'user' ? 'primary.contrastText' : 'text.primary',
            borderRadius: message.sender === 'user' ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
            whiteSpace: 'pre-line',
            position: 'relative',
          }}
        >
          <Typography variant="body1">{message.text}</Typography>
          <Typography
            variant="caption"
            sx={{
              display: 'block',
              mt: 1,
              opacity: 0.7,
              textAlign: message.sender === 'user' ? 'right' : 'left',
            }}
          >
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </Typography>
        </Paper>

        {message.sender === 'user' && (
          <Avatar sx={{ bgcolor: 'secondary.main', width: 32, height: 32 }}>
            <PersonIcon sx={{ fontSize: 18 }} />
          </Avatar>
        )}
      </Box>
    </motion.div>
  );

  return (
    <Box sx={{ height: 'calc(100vh - 100px)', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h4" gutterBottom sx={{ mb: 2, fontWeight: 'bold' }}>
        AI Chat Assistant
      </Typography>

      {/* Quick Actions */}
      <Box sx={{ mb: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
        {quickActions.map((action, index) => (
          <Chip
            key={index}
            icon={action.icon}
            label={action.label}
            onClick={action.action}
            variant="outlined"
            sx={{ cursor: 'pointer' }}
          />
        ))}
      </Box>

      {/* Messages Container */}
      <Paper
        elevation={2}
        sx={{
          flex: 1,
          p: 2,
          mb: 2,
          overflowY: 'auto',
          backgroundColor: 'background.default',
          borderRadius: 2,
        }}
      >
        <AnimatePresence>
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
        </AnimatePresence>

        {isTyping && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              marginBottom: '16px',
            }}
          >
            <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
              <BotIcon sx={{ fontSize: 18 }} />
            </Avatar>
            <Paper sx={{ p: 2, backgroundColor: 'background.paper', borderRadius: '18px 18px 18px 4px' }}>
              <Typography variant="body2" color="textSecondary">
                Thinking...
              </Typography>
            </Paper>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </Paper>

      {/* Input Area */}
      <Paper
        elevation={2}
        sx={{
          p: 2,
          borderRadius: 2,
          backgroundColor: 'background.paper',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything about robotics, programming, or learning..."
            variant="outlined"
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 2,
              },
            }}
          />
          <IconButton
            onClick={handleMenuClick}
            sx={{ color: 'text.secondary' }}
          >
            <MoreIcon />
          </IconButton>
          <Tooltip title="Send message">
            <span>
              <IconButton
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || isTyping}
                color="primary"
                sx={{
                  bgcolor: 'primary.main',
                  color: 'primary.contrastText',
                  '&:hover': {
                    bgcolor: 'primary.dark',
                  },
                  '&.Mui-disabled': {
                    bgcolor: 'action.disabledBackground',
                    color: 'action.disabled',
                  },
                }}
              >
                <SendIcon />
              </IconButton>
            </span>
          </Tooltip>
        </Box>
      </Paper>

      {/* Context Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleMenuClose}>Clear Chat</MenuItem>
        <MenuItem onClick={handleMenuClose}>Export Conversation</MenuItem>
        <MenuItem onClick={handleMenuClose}>Help</MenuItem>
      </Menu>
    </Box>
  );
};

export default Chat;