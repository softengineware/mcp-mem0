// Claude Code hook script for automatically saving messages
// This is a conceptual script that demonstrates how you would integrate 
// with Claude Code's hooks if they were available

function onUserMessage(message) {
  // Call MCP tool to save user message
  claude.callMcpTool("auto_mem0", "auto_save_message", {
    role: "user",
    content: message.content
  });
}

function onAssistantMessage(message) {
  // Call MCP tool to save assistant message
  claude.callMcpTool("auto_mem0", "auto_save_message", {
    role: "assistant",
    content: message.content
  });
}

// Register hooks
claude.on("userMessage", onUserMessage);
claude.on("assistantMessage", onAssistantMessage);