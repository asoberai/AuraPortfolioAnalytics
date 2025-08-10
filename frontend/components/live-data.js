// AuraQuant Live Data Component
// Handles LimeTrader API integration for live portfolio data

class LiveDataComponent {
    constructor() {
        this.liveSection = document.getElementById('liveSection');
        this.refreshInterval = null;
        this.autoRefreshEnabled = false;
        
        this.init();
    }

    init() {
        // Auto-refresh toggle (could be added to UI later)
        this.setupAutoRefresh();
    }

    async displayLiveData(liveData) {
        // Update account metrics
        this.updateAccountMetrics(liveData.account_info);
        
        // Update live positions table
        this.updateLivePositionsTable(liveData.positions);
        
        // Update portfolio summary if available
        if (liveData.summary) {
            this.updatePortfolioSummary(liveData.summary);
        }
        
        // Show live section
        this.liveSection.style.display = 'block';
        this.liveSection.scrollIntoView({ behavior: 'smooth' });
        
        // Start auto-refresh if not already running
        if (!this.autoRefreshEnabled) {
            this.startAutoRefresh();
        }
    }

    updateAccountMetrics(accountInfo) {
        document.getElementById('liveAccountValue').textContent = `$${accountInfo.total_value.toLocaleString()}`;
        document.getElementById('liveCash').textContent = `$${accountInfo.cash.toLocaleString()}`;
        document.getElementById('liveBuyingPower').textContent = `$${accountInfo.buying_power.toLocaleString()}`;
    }

    updateLivePositionsTable(positions) {
        const tableContainer = document.getElementById('livePositionsTable');
        
        if (positions.length === 0) {
            tableContainer.innerHTML = '<p class="text-secondary">No positions found in your account</p>';
            return;
        }
        
        const table = document.createElement('table');
        table.innerHTML = `
            <thead>
                <tr>
                    <th>Symbol</th>
                    <th>Quantity</th>
                    <th>Market Value</th>
                    <th>Unrealized P&L</th>
                    <th>Portfolio %</th>
                </tr>
            </thead>
            <tbody>
                ${positions.map(pos => `
                    <tr>
                        <td><strong>${pos.symbol}</strong></td>
                        <td>${pos.quantity}</td>
                        <td>$${pos.market_value.toLocaleString()}</td>
                        <td class="${pos.unrealized_pnl >= 0 ? 'text-success' : 'text-danger'}">
                            ${pos.unrealized_pnl >= 0 ? '+' : ''}$${pos.unrealized_pnl.toLocaleString()}
                        </td>
                        <td>${pos.percentage.toFixed(1)}%</td>
                    </tr>
                `).join('')}
            </tbody>
        `;
        
        tableContainer.innerHTML = '';
        tableContainer.appendChild(table);
    }

    async refreshLiveData() {
        try {
            const result = await api.getLivePositions();
            
            if (result.success) {
                this.updateAccountMetrics(result.data.account_info);
                this.updateLivePositionsTable(result.data.positions);
                
                // Update timestamp
                const now = new Date().toLocaleTimeString();
                this.showRefreshStatus(`Last updated: ${now}`, 'success');
            } else {
                this.showRefreshStatus(`Update failed: ${result.error}`, 'error');
            }
        } catch (error) {
            this.showRefreshStatus(`Update failed: ${error.message}`, 'error');
        }
    }

    showRefreshStatus(message, type) {
        // Create or update status indicator
        let statusElement = document.getElementById('refreshStatus');
        if (!statusElement) {
            statusElement = document.createElement('div');
            statusElement.id = 'refreshStatus';
            statusElement.style.cssText = `
                position: absolute;
                top: 10px;
                right: 80px;
                padding: 0.25rem 0.5rem;
                border-radius: 0.25rem;
                font-size: 0.75rem;
                z-index: 10;
            `;
            this.liveSection.querySelector('.section-header').appendChild(statusElement);
        }
        
        statusElement.textContent = message;
        statusElement.className = type === 'success' ? 'text-success' : 'text-danger';
        
        // Remove after 3 seconds
        setTimeout(() => {
            if (statusElement.parentNode) {
                statusElement.parentNode.removeChild(statusElement);
            }
        }, 3000);
    }

    startAutoRefresh() {
        if (this.refreshInterval) return;
        
        this.autoRefreshEnabled = true;
        this.refreshInterval = setInterval(() => {
            // Only refresh if the live section is visible
            if (this.liveSection.style.display !== 'none') {
                this.refreshLiveData();
            }
        }, 30000); // Refresh every 30 seconds
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
            this.autoRefreshEnabled = false;
        }
    }

    setupAutoRefresh() {
        // Stop auto-refresh when live section is closed
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                    if (this.liveSection.style.display === 'none') {
                        this.stopAutoRefresh();
                    }
                }
            });
        });
        
        observer.observe(this.liveSection, { attributes: true });
    }

    // Method to manually convert portfolio description to live data format
    convertPortfolioToLiveFormat(portfolioDescription) {
        // Parse portfolio description and convert to live data format
        // This is useful when user wants to analyze a hypothetical portfolio as if it were live
        
        const positions = [];
        let totalValue = 0;
        let cash = 0;
        
        // Simple parsing - in production, you'd want more robust parsing
        const lines = portfolioDescription.split(',').map(line => line.trim());
        
        lines.forEach(line => {
            const cashMatch = line.match(/cash:\s*\$?(\d+(?:,\d{3})*)/i);
            if (cashMatch) {
                cash = parseInt(cashMatch[1].replace(/,/g, ''));
                totalValue += cash;
                return;
            }
            
            const positionMatch = line.match(/([A-Z]{2,5}):\s*\$?(\d+(?:,\d{3})*)/i);
            if (positionMatch) {
                const symbol = positionMatch[1];
                const value = parseInt(positionMatch[2].replace(/,/g, ''));
                
                positions.push({
                    symbol: symbol,
                    quantity: Math.floor(value / 100), // Estimate shares at $100 each
                    market_value: value,
                    unrealized_pnl: 0, // Unknown for hypothetical
                    percentage: 0 // Will be calculated after totalValue is known
                });
                
                totalValue += value;
            }
        });
        
        // Calculate percentages
        positions.forEach(pos => {
            pos.percentage = (pos.market_value / totalValue) * 100;
        });
        
        return {
            account_info: {
                total_value: totalValue,
                cash: cash,
                buying_power: cash * 2 // Assume 2:1 margin
            },
            positions: positions
        };
    }

    updatePortfolioSummary(summary) {
        // Add portfolio summary section if it doesn't exist
        let summarySection = document.getElementById('portfolioSummarySection');
        if (!summarySection) {
            summarySection = document.createElement('div');
            summarySection.id = 'portfolioSummarySection';
            summarySection.className = 'portfolio-summary-section';
            summarySection.innerHTML = `
                <h3>📊 Portfolio Summary</h3>
                <div class="summary-grid" id="summaryGrid"></div>
                <div class="ai-analysis-section">
                    <button class="analyze-btn" id="analyzePortfolioBtn">
                        <i class="fas fa-robot"></i> Get AI Analysis
                    </button>
                    <div class="ai-analysis-result" id="aiAnalysisResult" style="display: none;"></div>
                </div>
            `;
            
            // Insert after account overview
            const accountOverview = this.liveSection.querySelector('.account-overview');
            accountOverview.parentNode.insertBefore(summarySection, accountOverview.nextSibling);
            
            // Add click handler for AI analysis
            document.getElementById('analyzePortfolioBtn').addEventListener('click', () => {
                this.analyzePortfolioWithAI();
            });
        }
        
        // Update summary grid
        const summaryGrid = document.getElementById('summaryGrid');
        summaryGrid.innerHTML = `
            <div class="summary-card">
                <h4>Total P&L</h4>
                <div class="metric-value ${summary.total_unrealized_pnl >= 0 ? 'text-success' : 'text-danger'}">
                    ${summary.total_unrealized_pnl >= 0 ? '+' : ''}$${summary.total_unrealized_pnl.toLocaleString()}
                </div>
                <small>${summary.unrealized_pnl_percentage.toFixed(1)}%</small>
            </div>
            <div class="summary-card">
                <h4>Concentration Risk</h4>
                <div class="metric-value ${summary.concentration_risk > 30 ? 'text-warning' : 'text-success'}">
                    ${summary.concentration_risk.toFixed(1)}%
                </div>
                <small>Largest position</small>
            </div>
            <div class="summary-card">
                <h4>Tech Exposure</h4>
                <div class="metric-value">
                    ${summary.tech_exposure.toFixed(1)}%
                </div>
                <small>Technology allocation</small>
            </div>
            <div class="summary-card">
                <h4>Diversification</h4>
                <div class="metric-value ${summary.position_count < 5 ? 'text-warning' : 'text-success'}">
                    ${summary.position_count}
                </div>
                <small>Positions</small>
            </div>
        `;
    }

    async analyzePortfolioWithAI() {
        const analyzeBtn = document.getElementById('analyzePortfolioBtn');
        const resultDiv = document.getElementById('aiAnalysisResult');
        
        try {
            // Update button state
            analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
            analyzeBtn.disabled = true;
            
            // Call AI analysis endpoint
            const response = await fetch('/api/analyze-live-portfolio', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                
                if (data.success) {
                    // Display AI analysis
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = `
                        <div class="ai-analysis-header">
                            <h4><i class="fas fa-robot"></i> AI Portfolio Analysis</h4>
                            <small>Generated: ${new Date(data.data.analysis_timestamp).toLocaleString()}</small>
                            ${data.data.is_live_data ? '<span class="live-badge">🔴 Live Data</span>' : '<span class="demo-badge">📊 Demo Data</span>'}
                        </div>
                        <div class="ai-analysis-content">
                            ${this.formatAIAnalysis(data.data.ai_analysis)}
                        </div>
                    `;
                    
                    // Scroll to analysis
                    resultDiv.scrollIntoView({ behavior: 'smooth' });
                    
                } else {
                    throw new Error(data.error || 'Analysis failed');
                }
            } else {
                throw new Error(`Server error: ${response.status}`);
            }
            
        } catch (error) {
            console.error('AI analysis error:', error);
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    AI analysis failed: ${error.message}
                </div>
            `;
        } finally {
            // Reset button
            analyzeBtn.innerHTML = '<i class="fas fa-robot"></i> Get AI Analysis';
            analyzeBtn.disabled = false;
        }
    }

    formatAIAnalysis(analysisText) {
        // Convert AI analysis text to formatted HTML
        return analysisText
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/^\d+\.\s*/gm, '<strong>$&</strong>')
            .replace(/^([A-Z][^:]+:)/gm, '<strong>$1</strong>')
            .replace(/^/, '<p>')
            .replace(/$/, '</p>');
    }
}

// Global function for refreshing live data
window.refreshLiveData = async function() {
    if (window.liveDataComponent) {
        await window.liveDataComponent.refreshLiveData();
    }
};

// Initialize live data component when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.liveDataComponent = new LiveDataComponent();
}); 