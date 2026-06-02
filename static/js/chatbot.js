/**
 * AI Chatbot JavaScript Module
 * Handles all chatbot interactions and UI
 */

class AIAssistantChatbot {
    constructor(containerId = 'chatbot-widget') {
        this.containerId = containerId;
        this.messages = [];
        this.isMinimized = false;
        this.isLoading = false;
        this.conversationHistory = [];
        this.init();
    }

    init() {
        this.render();
        this.attachEventListeners();
        this.loadConversationHistory();
    }

    render() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Container ${this.containerId} not found`);
            return;
        }

        container.innerHTML = `
            <div class="chatbot-widget">
                <!-- Header -->
                <div class="chatbot-header">
                    <h3>
                        <span class="chatbot-header-icon">🤖</span>
                        <span>AI Assistant</span>
                    </h3>
                    <div class="chatbot-controls">
                        <button class="chatbot-btn" id="chatbot-history-btn" title="History">📋</button>
                        <button class="chatbot-btn" id="chatbot-minimize-btn" title="Minimize">−</button>
                        <button class="chatbot-btn" id="chatbot-close-btn" title="Close">✕</button>
                    </div>
                </div>

                <!-- Messages Area -->
                <div class="chatbot-messages" id="chatbot-messages">
                    <div class="chatbot-empty">
                        <div class="chatbot-empty-icon">💡</div>
                        <div class="chatbot-empty-text">
                            <strong>Hi! I'm your AI Assistant</strong><br>
                            I can help with:<br>
                            ✓ Technical Issues<br>
                            ✓ HR & Leave Policies<br>
                            ✓ Project Management
                        </div>
                        <div class="chatbot-empty-suggestions">
                            <button class="suggestion-btn" data-suggestion="How do I reset my password?">
                                🔐 Password Help
                            </button>
                            <button class="suggestion-btn" data-suggestion="What is the leave policy?">
                                📅 Leave Policy
                            </button>
                            <button class="suggestion-btn" data-suggestion="How do I track a project?">
                                📊 Project Tracking
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Input Area -->
                <div class="chatbot-input-area">
                    <textarea 
                        id="chatbot-input" 
                        class="chatbot-input" 
                        placeholder="Type your question..."
                        rows="1"
                    ></textarea>
                    <button class="chatbot-send-btn" id="chatbot-send-btn">
                        <span>➤</span>
                    </button>
                </div>
            </div>

            <!-- History Modal (hidden) -->
            <div id="history-modal" style="display: none;">
                <div style="background: white; border-radius: 12px; box-shadow: 0 5px 30px rgba(0,0,0,0.3); width: 500px; max-height: 600px; overflow-y: auto;">
                    <div style="padding: 15px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0;">Conversation History</h4>
                        <button id="history-modal-close" style="background: none; border: none; font-size: 20px; cursor: pointer;">✕</button>
                    </div>
                    <div id="history-list" style="padding: 15px;"></div>
                </div>
            </div>
        `;
    }

    attachEventListeners() {
        // Close button
        document.getElementById('chatbot-close-btn').addEventListener('click', () => {
            document.getElementById(this.containerId).remove();
        });

        // Minimize button
        document.getElementById('chatbot-minimize-btn').addEventListener('click', () => {
            const widget = document.querySelector('.chatbot-widget');
            widget.classList.toggle('minimized');
            this.isMinimized = !this.isMinimized;
        });

        // History button
        document.getElementById('chatbot-history-btn').addEventListener('click', () => {
            this.showHistory();
        });

        // Send button
        document.getElementById('chatbot-send-btn').addEventListener('click', () => {
            this.sendMessage();
        });

        // Input field - send on Enter
        document.getElementById('chatbot-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-resize textarea
        document.getElementById('chatbot-input').addEventListener('input', (e) => {
            e.target.style.height = 'auto';
            e.target.style.height = Math.min(e.target.scrollHeight, 80) + 'px';
        });

        // Suggestion buttons
        document.querySelectorAll('.suggestion-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const suggestion = e.target.getAttribute('data-suggestion');
                document.getElementById('chatbot-input').value = suggestion;
                this.sendMessage();
            });
        });

        // History modal close
        document.getElementById('history-modal-close').addEventListener('click', () => {
            document.getElementById('history-modal').style.display = 'none';
        });
    }

    async sendMessage() {
        const input = document.getElementById('chatbot-input');
        const message = input.value.trim();

        if (!message || this.isLoading) return;

        // Add user message
        this.addMessage('user', message);
        input.value = '';
        input.style.height = 'auto';

        // Show loading state
        this.isLoading = true;
        this.showTypingIndicator();

        try {
            const response = await fetch('/api/chatbot/send_message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();

            // Remove typing indicator
            this.removeTypingIndicator();

            if (data.success) {
                this.addMessage('bot', data.response, data.category);
            } else {
                this.addMessage('bot', data.response || 'Sorry, I encountered an error. Please try again.', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            this.removeTypingIndicator();
            this.addMessage('bot', 'Sorry, I\'m having trouble connecting. Please try again.', 'error');
        } finally {
            this.isLoading = false;
            document.getElementById('chatbot-send-btn').disabled = false;
        }
    }

    addMessage(sender, text, category = '') {
        const messagesContainer = document.getElementById('chatbot-messages');

        // Remove empty state if exists
        const emptyState = messagesContainer.querySelector('.chatbot-empty');
        if (emptyState) {
            emptyState.remove();
        }

        // Create message element
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = this.parseMessageText(text);

        if (category) {
            const categorySpan = document.createElement('div');
            categorySpan.className = 'message-category';
            categorySpan.textContent = category;
            contentDiv.appendChild(categorySpan);
        }

        messageDiv.appendChild(contentDiv);
        messagesContainer.appendChild(messageDiv);

        // Store message
        this.messages.push({ sender, text, category, timestamp: new Date() });

        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    parseMessageText(text) {
        // Make links clickable
        let parsed = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
        
        // Format bold text
        parsed = parsed.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        
        // Format code blocks
        parsed = parsed.replace(/`([^`]+)`/g, '<code style="background: #f0f0f0; padding: 2px 6px; border-radius: 3px;">$1</code>');
        
        // Convert newlines to breaks
        parsed = parsed.replace(/\n/g, '<br>');
        
        return parsed;
    }

    showTypingIndicator() {
        const messagesContainer = document.getElementById('chatbot-messages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-message bot';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `
            <div class="message-content">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        messagesContainer.appendChild(typingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    removeTypingIndicator() {
        const typing = document.getElementById('typing-indicator');
        if (typing) {
            typing.remove();
        }
    }

    async loadConversationHistory() {
        try {
            const response = await fetch('/api/chatbot/history');
            const data = await response.json();
            this.conversationHistory = data.conversations || [];
        } catch (error) {
            console.error('Error loading history:', error);
        }
    }

    async showHistory() {
        await this.loadConversationHistory();
        const historyList = document.getElementById('history-list');
        const modal = document.getElementById('history-modal');

        if (this.conversationHistory.length === 0) {
            historyList.innerHTML = '<p style="color: #999; text-align: center;">No conversation history yet</p>';
        } else {
            historyList.innerHTML = this.conversationHistory.map(conv => `
                <div style="padding: 10px; background: #f9f9f9; border-radius: 6px; margin-bottom: 8px; cursor: pointer; transition: all 0.2s;" 
                     onclick="location.href='/chatbot?conv=${conv.conversation_id}'">
                    <div style="font-weight: 600; color: #667eea;">${conv.topic || 'General'}</div>
                    <div style="font-size: 12px; color: #999;">
                        ${conv.message_count} messages • ${new Date(conv.updated_at).toLocaleDateString()}
                    </div>
                </div>
            `).join('');
        }

        modal.style.display = 'flex';
        modal.style.justifyContent = 'center';
        modal.style.alignItems = 'center';
        modal.style.position = 'fixed';
        modal.style.top = 0;
        modal.style.left = 0;
        modal.style.width = '100%';
        modal.style.height = '100%';
        modal.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        modal.style.zIndex = 9999;
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Create container for chatbot
    if (!document.getElementById('chatbot-widget')) {
        const widget = document.createElement('div');
        widget.id = 'chatbot-widget';
        document.body.appendChild(widget);
    }

    // Initialize chatbot
    window.aiChatbot = new AIAssistantChatbot('chatbot-widget');
});
