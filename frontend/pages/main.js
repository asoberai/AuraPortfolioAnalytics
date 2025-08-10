// AuraQuant Main Application Controller
// Initializes and coordinates all components

class AuraQuantApp {
    constructor() {
        this.currentView = 'chat';
        this.portfolioData = null;
        this.marketData = null;
        this.updateInterval = null;
        
        this.init();
    }
    
    init() {
        this.setupNavigation();
        this.setupRefreshButton();
        this.startDataUpdates();
        this.checkSystemStatus();
        
        console.log('AuraQuant Professional Platform initialized');
    }
    
    setupNavigation() {
        const navItems = document.querySelectorAll('.nav-item');
        const views = document.querySelectorAll('.view');
        
        navItems.forEach(item => {
            item.addEventListener('click', () => {
                const viewName = item.getAttribute('data-view');
                this.switchView(viewName);
            });
        });
    }
    
    switchView(viewName) {
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-view="${viewName}"]`).classList.add('active');
        
        // Update views
        document.querySelectorAll('.view').forEach(view => {
            view.classList.remove('active');
        });
        document.getElementById(`${viewName}-view`).classList.add('active');
        
        this.currentView = viewName;
        
        // Load view-specific data
        this.loadViewData(viewName);
    }
    
    async loadViewData(viewName) {
        switch (viewName) {
            case 'portfolio':
                await this.loadPortfolioView();
                break;
            case 'analytics':
                await this.loadAnalyticsView();
                break;
            case 'market':
                await this.loadMarketView();
                break;
        }
    }
    
    async loadPortfolioView() {
        const content = document.getElementById('portfolio-content');
        if (!content) return;
        
        content.innerHTML = '<div class="loading-state">Loading portfolio data...</div>';
        
        try {
            const response = await fetch('/api/live-positions');
            const data = await response.json();
            
            if (data.success) {
                this.renderPortfolioTable(content, data.data);
            } else {
                content.innerHTML = `<div class="error-state">Failed to load portfolio: ${data.error}</div>`;
            }
        } catch (error) {
            console.error('Portfolio loading error:', error);
            content.innerHTML = '<div class="error-state">Connection error</div>';
        }
    }
    
    renderPortfolioTable(container, portfolioData) {
        const positions = portfolioData.positions || [];
        const summary = portfolioData.summary || {};
        
        let html = `
            <div class="portfolio-overview">
                <div class="overview-grid">
                    <div class="overview-card">
                        <h3>Total Portfolio Value</h3>
                        <div class="card-value">$${(summary.total_portfolio_value || 0).toLocaleString()}</div>
                    </div>
                    <div class="overview-card">
                        <h3>Unrealized P&L</h3>
                        <div class="card-value ${(summary.total_unrealized_pnl || 0) >= 0 ? 'positive' : 'negative'}">
                            ${(summary.total_unrealized_pnl || 0) >= 0 ? '+' : ''}$${(summary.total_unrealized_pnl || 0).toLocaleString()}
                        </div>
                    </div>
                    <div class="overview-card">
                        <h3>Cash Balance</h3>
                        <div class="card-value">$${(summary.cash_balance || 0).toLocaleString()}</div>
                    </div>
                    <div class="overview-card">
                        <h3>Active Positions</h3>
                        <div class="card-value">${positions.length}</div>
                    </div>
                </div>
            </div>
            
            <div class="positions-table-container">
                <table class="positions-table">
                    <thead>
                        <tr>
                            <th>Symbol</th>
                            <th>Quantity</th>
                            <th>Market Value</th>
                            <th>Avg Cost</th>
                            <th>P&L</th>
                            <th>Allocation</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        positions.forEach(position => {
            const pnl = position.unrealized_pnl || 0;
            const pnlClass = pnl >= 0 ? 'positive' : 'negative';
            
            html += `
                <tr>
                    <td class="symbol-cell">
                        <strong>${position.symbol}</strong>
                    </td>
                    <td>${(position.quantity || 0).toLocaleString()}</td>
                    <td>$${(position.market_value || 0).toLocaleString()}</td>
                    <td>$${(position.average_cost || 0).toFixed(2)}</td>
                    <td class="${pnlClass}">
                        ${pnl >= 0 ? '+' : ''}$${pnl.toLocaleString()}
                    </td>
                    <td>${(position.percentage || 0).toFixed(1)}%</td>
                </tr>
            `;
        });
        
        html += `
                    </tbody>
                </table>
            </div>
        `;
        
        container.innerHTML = html;
    }
    
    async loadAnalyticsView() {
        const content = document.getElementById('analytics-content');
        if (!content) return;
        
        content.innerHTML = '<div class="loading-state">Loading analytics...</div>';
        
        try {
            // Get portfolio analysis
            const portfolioResponse = await fetch('/api/live-positions');
            const portfolioData = await portfolioResponse.json();
            
            if (portfolioData.success) {
                const analysisResponse = await fetch('/api/analyze-portfolio', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        portfolio_summary: portfolioData.data,
                        target_return: 10,
                        time_horizon_months: 12
                    })
                });
                
                const analysisData = await analysisResponse.json();
                
                if (analysisData.success) {
                    this.renderAnalytics(content, analysisData.data);
                } else {
                    content.innerHTML = `<div class="error-state">Analysis failed: ${analysisData.error}</div>`;
                }
            }
        } catch (error) {
            console.error('Analytics loading error:', error);
            content.innerHTML = '<div class="error-state">Connection error</div>';
        }
    }
    
    renderAnalytics(container, analysisData) {
        let html = `
            <div class="analytics-grid">
                <div class="analytics-card">
                    <h3>Risk Analysis</h3>
                    <div class="metric-row">
                        <span>Portfolio Beta</span>
                        <span>${(analysisData.portfolio_beta || 0).toFixed(2)}</span>
                    </div>
                    <div class="metric-row">
                        <span>Volatility</span>
                        <span>${((analysisData.portfolio_volatility || 0) * 100).toFixed(1)}%</span>
                    </div>
                    <div class="metric-row">
                        <span>Sharpe Ratio</span>
                        <span>${(analysisData.sharpe_ratio || 0).toFixed(2)}</span>
                    </div>
                </div>
                
                <div class="analytics-card">
                    <h3>Performance Metrics</h3>
                    <div class="metric-row">
                        <span>Expected Return</span>
                        <span>${((analysisData.expected_return || 0) * 100).toFixed(1)}%</span>
                    </div>
                    <div class="metric-row">
                        <span>Max Drawdown</span>
                        <span>${((analysisData.max_drawdown || 0) * 100).toFixed(1)}%</span>
                    </div>
                    <div class="metric-row">
                        <span>VaR (95%)</span>
                        <span>${((analysisData.var_95 || 0) * 100).toFixed(1)}%</span>
                    </div>
                </div>
            </div>
        `;
        
        if (analysisData.recommendations && analysisData.recommendations.length > 0) {
            html += `
                <div class="recommendations-section">
                    <h3>AI Recommendations</h3>
                    <div class="recommendations-list">
            `;
            
            analysisData.recommendations.forEach((rec, index) => {
                html += `
                    <div class="recommendation-item">
                        <div class="rec-number">${index + 1}</div>
                        <div class="rec-content">${rec}</div>
                    </div>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        }
        
        container.innerHTML = html;
    }
    
    async loadMarketView() {
        const content = document.getElementById('market-content');
        if (!content) return;
        
        content.innerHTML = '<div class="loading-state">Loading market data...</div>';
        
        // For now, show simulated market data
        // In production, this would call real market data APIs
        setTimeout(() => {
            this.renderMarketData(content);
        }, 1000);
    }
    
    renderMarketData(container) {
        const marketData = {
            indices: {
                'S&P 500': { value: 4150.25, change: 0.85, volume: '3.2B' },
                'NASDAQ': { value: 12845.50, change: 1.20, volume: '2.8B' },
                'Dow Jones': { value: 33875.40, change: 0.65, volume: '1.9B' },
                'VIX': { value: 18.45, change: -2.10, volume: '45M' }
            },
            sectors: {
                'Technology': 1.45,
                'Healthcare': 0.85,
                'Financial': 0.65,
                'Energy': -0.45,
                'Utilities': -0.25,
                'Real Estate': -0.15
            }
        };
        
        let html = `
            <div class="market-grid">
                <div class="market-section">
                    <h3>Major Indices</h3>
                    <div class="indices-grid">
        `;
        
        Object.entries(marketData.indices).forEach(([name, data]) => {
            const changeClass = data.change >= 0 ? 'positive' : 'negative';
            html += `
                <div class="index-card">
                    <div class="index-name">${name}</div>
                    <div class="index-value">${data.value.toLocaleString()}</div>
                    <div class="index-change ${changeClass}">
                        ${data.change >= 0 ? '+' : ''}${data.change.toFixed(2)}%
                    </div>
                    <div class="index-volume">Vol: ${data.volume}</div>
                </div>
            `;
        });
        
        html += `
                    </div>
                </div>
                
                <div class="market-section">
                    <h3>Sector Performance</h3>
                    <div class="sectors-list">
        `;
        
        Object.entries(marketData.sectors).forEach(([sector, performance]) => {
            const changeClass = performance >= 0 ? 'positive' : 'negative';
            html += `
                <div class="sector-item">
                    <span class="sector-name">${sector}</span>
                    <span class="sector-performance ${changeClass}">
                        ${performance >= 0 ? '+' : ''}${performance.toFixed(2)}%
                    </span>
                </div>
            `;
        });
        
        html += `
                    </div>
                </div>
            </div>
        `;
        
        container.innerHTML = html;
    }
    
    setupRefreshButton() {
        const refreshBtn = document.getElementById('refresh-all');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshAllData();
            });
        }
    }
    
    async refreshAllData() {
        // Update sidebar data
        await this.updateSidebarData();
        
        // Update current view
        await this.loadViewData(this.currentView);
        
        // Show toast notification
        this.showToast('Data refreshed successfully', 'success');
    }
    
    async updateSidebarData() {
        try {
            const response = await fetch('/api/live-positions');
            const data = await response.json();
            
            if (data.success) {
                this.portfolioData = data.data;
                this.updateSidebarStats(data.data);
            }
        } catch (error) {
            console.error('Sidebar update error:', error);
        }
    }
    
    updateSidebarStats(portfolioData) {
        const summary = portfolioData.summary || {};
        const positions = portfolioData.positions || [];
        
        // Update total value
        const totalValueEl = document.getElementById('total-value');
        if (totalValueEl) {
            totalValueEl.textContent = `$${(summary.total_portfolio_value || 0).toLocaleString()}`;
        }
        
        // Update daily P&L
        const dailyPnlEl = document.getElementById('daily-pnl');
        if (dailyPnlEl) {
            const pnl = summary.total_unrealized_pnl || 0;
            dailyPnlEl.textContent = `${pnl >= 0 ? '+' : ''}$${pnl.toLocaleString()}`;
            dailyPnlEl.className = `stat-value ${pnl >= 0 ? 'positive' : 'negative'}`;
        }
        
        // Update position count
        const positionCountEl = document.getElementById('position-count');
        if (positionCountEl) {
            positionCountEl.textContent = positions.length.toString();
        }
    }
    
    startDataUpdates() {
        // Initial load
        this.updateSidebarData();
        
        // Set up periodic updates
        this.updateInterval = setInterval(() => {
            this.updateSidebarData();
        }, 30000); // Update every 30 seconds
    }
    
    async checkSystemStatus() {
        try {
            const response = await fetch('/api/system-status');
            const data = await response.json();
            
            if (data.success) {
                this.updateConnectionStatus('connected', 'System Online');
            } else {
                this.updateConnectionStatus('error', 'System Error');
            }
        } catch (error) {
            this.updateConnectionStatus('error', 'Connection Failed');
        }
    }
    
    updateConnectionStatus(status, text) {
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('status-text');
        
        if (statusDot && statusText) {
            statusDot.className = `status-indicator ${status}`;
            statusText.textContent = text;
        }
    }
    
    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        container.appendChild(toast);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
    
    // Cleanup
    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.auraQuantApp = new AuraQuantApp();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.auraQuantApp) {
        window.auraQuantApp.destroy();
    }
}); 