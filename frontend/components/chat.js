// AuraQuant Chat Component
// Handles Ollama-powered chat interface

class ChatComponent {
    constructor() {
        this.messagesArea = document.getElementById('messages-area');
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.loadingOverlay = document.getElementById('loading-overlay');
        
        this.isProcessing = false;
        this.conversationHistory = [];
        
        this.init();
    }
    
    init() {
        if (!this.messagesArea || !this.messageInput || !this.sendButton) {
            console.error('Chat elements not found');
            return;
        }
        
        this.setupEventListeners();
        this.clearWelcomeMessage();
        
        console.log('Professional Chat initialized');
    }
    
    setupEventListeners() {
        // Send button
        this.sendButton.addEventListener('click', () => this.handleSend());
        
        // Enter key handling
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSend();
            }
        });
        
        // Input validation
        this.messageInput.addEventListener('input', () => {
            const hasText = this.messageInput.value.trim().length > 0;
            this.sendButton.disabled = !hasText || this.isProcessing;
        });
        
        // Suggestion chips
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('suggestion-chip')) {
                const suggestion = e.target.getAttribute('data-suggestion');
                if (suggestion) {
                    this.messageInput.value = suggestion;
                    this.messageInput.focus();
                    this.sendButton.disabled = false;
                }
            }
        });
    }
    
    clearWelcomeMessage() {
        // Remove welcome message after first interaction
        setTimeout(() => {
            const welcomeMsg = this.messagesArea.querySelector('.welcome-message');
            if (welcomeMsg && this.conversationHistory.length === 0) {
                // Keep welcome message until first real interaction
            }
        }, 1000);
    }
    
    async handleSend() {
        const message = this.messageInput.value.trim();
        if (!message || this.isProcessing) return;
        
        // Clear welcome message on first send
        const welcomeMsg = this.messagesArea.querySelector('.welcome-message');
        if (welcomeMsg) {
            welcomeMsg.remove();
        }
        
        // Add user message
        this.addUserMessage(message);
        this.messageInput.value = '';
        this.sendButton.disabled = true;
        
        // Show processing state
        this.setProcessingState(true);
        
        try {
            // Get portfolio context
            const portfolioContext = await this.getPortfolioContext();
            
            // Call AI API
            const response = await this.callAI(message, portfolioContext);
            
            if (response.success) {
                this.addAIMessage(response.data);
                this.updateAIMetrics(response.data);
            } else {
                this.addErrorMessage(response.error || 'Failed to get AI response');
            }
            
        } catch (error) {
            console.error('Chat error:', error);
            this.addErrorMessage('Connection error. Please try again.');
        } finally {
            this.setProcessingState(false);
        }
    }
    
    async callAI(message, portfolioContext) {
        const requestData = {
            question: message,
            portfolio_context: portfolioContext
        };
        
        console.log('Sending to AI:', requestData);
        
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('AI Response:', data);
        
        return data;
    }
    
    async getPortfolioContext() {
        try {
            const response = await fetch('/api/live-positions');
            if (response.ok) {
                const data = await response.json();
                return data.success ? data.data : {};
            }
        } catch (error) {
            console.warn('Could not fetch portfolio context:', error);
        }
        return {};
    }
    
    addUserMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-text">${this.formatText(message)}</div>
            </div>
        `;
        
        this.messagesArea.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Add to conversation history
        this.conversationHistory.push({
            role: 'user',
            content: message,
            timestamp: new Date()
        });
    }
    
    addAIMessage(responseData) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message ai-message';
        
        const aiResponse = responseData.ai_response || responseData.message || 'No response received';
        const intelligenceScore = responseData.intelligence_score || 0;
        const confidenceLevel = responseData.confidence_level || 0;
        const responseQuality = responseData.response_quality || 'standard';
        const analyzedStocks = responseData.analyzed_stocks || [];
        
        let html = `
            <div class="message-content">
                <div class="message-header">
                    <div class="ai-badge">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                        </svg>
                        AuraQuant AI
                    </div>
                    <div class="quality-indicator">
        `;
        
        // Add quality indicators if available
        if (intelligenceScore > 0) {
            html += `
                <span class="quality-metric">Intelligence: ${intelligenceScore}/100</span>
            `;
        }
        
        if (confidenceLevel > 0) {
            html += `
                <span class="quality-metric">Confidence: ${Math.round(confidenceLevel * 100)}%</span>
            `;
        }
        
        if (responseQuality && responseQuality !== 'standard') {
            html += `
                <span class="quality-score ${responseQuality}">${responseQuality.toUpperCase()}</span>
            `;
        }
        
        html += `
                    </div>
                </div>
                <div class="message-text">${this.formatText(aiResponse)}</div>
        `;
        
        // Add analyzed stocks if available
        if (analyzedStocks.length > 0) {
            html += `
                <div class="analyzed-stocks">
                    <div class="stocks-label">Analyzed Securities:</div>
                    <div class="stocks-list">
                        ${analyzedStocks.map(stock => `<span class="stock-tag">${stock}</span>`).join('')}
                    </div>
                </div>
            `;
        }
        
        html += `</div>`;
        
        messageDiv.innerHTML = html;
        this.messagesArea.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Add to conversation history
        this.conversationHistory.push({
            role: 'assistant',
            content: aiResponse,
            metadata: responseData,
            timestamp: new Date()
        });
    }
    
    addErrorMessage(errorText) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message ai-message error';
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-header">
                    <div class="ai-badge error">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="10"></circle>
                            <line x1="15" y1="9" x2="9" y2="15"></line>
                            <line x1="9" y1="9" x2="15" y2="15"></line>
                        </svg>
                        System Error
                    </div>
                </div>
                <div class="message-text">
                    <p><strong>I apologize, but I encountered an error:</strong></p>
                    <p>${errorText}</p>
                    <p>Please try rephrasing your question or check your connection.</p>
                </div>
            </div>
        `;
        
        this.messagesArea.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    setProcessingState(isProcessing) {
        this.isProcessing = isProcessing;
        
        if (isProcessing) {
            // Show typing indicator
            this.showTypingIndicator();
            // Show loading overlay for longer requests
            setTimeout(() => {
                if (this.isProcessing) {
                    this.loadingOverlay.classList.add('show');
                }
            }, 2000);
        } else {
            // Hide indicators
            this.hideTypingIndicator();
            this.loadingOverlay.classList.remove('show');
            this.sendButton.disabled = this.messageInput.value.trim().length === 0;
        }
    }
    
    showTypingIndicator() {
        const existing = this.messagesArea.querySelector('.typing-indicator');
        if (existing) existing.remove();
        
        const indicator = document.createElement('div');
        indicator.className = 'typing-indicator';
        indicator.innerHTML = `
            <div class="ai-badge">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                </svg>
                Analyzing...
            </div>
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        
        this.messagesArea.appendChild(indicator);
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        const indicator = this.messagesArea.querySelector('.typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }
    
    updateAIMetrics(responseData) {
        // Update sidebar metrics
        if (responseData.intelligence_score) {
            const qualityBar = document.getElementById('quality-bar');
            const qualityScore = document.getElementById('quality-score');
            
            if (qualityBar && qualityScore) {
                const score = responseData.intelligence_score;
                qualityBar.style.width = `${score}%`;
                qualityScore.textContent = `${score}/100`;
                
                // Update color based on score
                if (score >= 80) {
                    qualityBar.style.background = 'var(--success-color)';
                } else if (score >= 60) {
                    qualityBar.style.background = 'var(--primary-color)';
                } else {
                    qualityBar.style.background = 'var(--warning-color)';
                }
            }
        }
        
        if (responseData.confidence_level) {
            const confidenceBar = document.getElementById('confidence-bar');
            const confidenceScore = document.getElementById('confidence-score');
            
            if (confidenceBar && confidenceScore) {
                const confidence = Math.round(responseData.confidence_level * 100);
                confidenceBar.style.width = `${confidence}%`;
                confidenceScore.textContent = `${confidence}%`;
                
                // Update color based on confidence
                if (confidence >= 80) {
                    confidenceBar.style.background = 'var(--success-color)';
                } else if (confidence >= 60) {
                    confidenceBar.style.background = 'var(--primary-color)';
                } else {
                    confidenceBar.style.background = 'var(--warning-color)';
                }
            }
        }
        
        // Update connection status
        this.updateConnectionStatus('connected', 'AI Connected');
    }
    
    updateConnectionStatus(status, text) {
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('status-text');
        
        if (statusDot && statusText) {
            statusDot.className = `status-indicator ${status}`;
            statusText.textContent = text;
        }
    }
    
    formatText(text) {
        // Convert markdown-like formatting to HTML
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/^(.*)$/, '<p>$1</p>')
            .replace(/<p><\/p>/g, '')
            .replace(/^\s*[-\*\+]\s+(.*)$/gm, '<li>$1</li>')
            .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    }
    
    scrollToBottom() {
        this.messagesArea.scrollTop = this.messagesArea.scrollHeight;
    }
    
    // Public methods
    clearChat() {
        this.messagesArea.innerHTML = '';
        this.conversationHistory = [];
    }
    
    getConversationHistory() {
        return this.conversationHistory;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.chatComponent = new ChatComponent();
}); 