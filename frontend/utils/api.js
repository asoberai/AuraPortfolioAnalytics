// AuraQuant API Utilities
// Handles all communication with the Ollama-powered backend

class AuraQuantAPI {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
        this.defaultHeaders = {
            'Content-Type': 'application/json',
        };
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: this.defaultHeaders,
            ...options,
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || `HTTP error! status: ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // System Status
    async getSystemStatus() {
        return this.request('/api/system-status');
    }

    async getHealthCheck() {
        return this.request('/');
    }

    // Natural Language Processing
    async parseRequirements(userInput) {
        return this.request('/api/parse-requirements', {
            method: 'POST',
            body: JSON.stringify({ user_input: userInput }),
        });
    }

    // Portfolio Analysis
    async analyzePortfolio(portfolioDescription, targetReturn = null, timeHorizonMonths = null) {
        const payload = {
            portfolio_description: portfolioDescription,
        };
        
        if (targetReturn !== null) payload.target_return = targetReturn;
        if (timeHorizonMonths !== null) payload.time_horizon_months = timeHorizonMonths;

        return this.request('/api/analyze-portfolio', {
            method: 'POST',
            body: JSON.stringify(payload),
        });
    }

    // Portfolio Generation
    async generatePortfolio(userInput) {
        return this.request('/api/generate-portfolio', {
            method: 'POST',
            body: JSON.stringify({ user_input: userInput }),
        });
    }

    // Chat Interface
    async chatAboutPortfolio(question, portfolioContext) {
        return this.request('/api/chat', {
            method: 'POST',
            body: JSON.stringify({
                question: question,
                portfolio_context: portfolioContext,
            }),
        });
    }

    // Live Data
    async getLivePositions() {
        return this.request('/api/live-positions');
    }

    // Portfolio Actions
    async approvePortfolio(action, modifications = null, newRequirements = null) {
        const payload = { action };
        
        if (modifications) payload.modifications = modifications;
        if (newRequirements) payload.new_requirements = newRequirements;

        return this.request('/api/approve-portfolio', {
            method: 'POST',
            body: JSON.stringify(payload),
        });
    }
}

// Create global API instance
const api = new AuraQuantAPI();

// Export for use in other modules
window.AuraQuantAPI = api; 