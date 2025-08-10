class AnalyticsDashboard {
    constructor() {
        this.dashboardContainer = document.getElementById('analytics-dashboard');
        this.chartsContainer = document.getElementById('charts-container');
        this.metricsContainer = document.getElementById('metrics-container');
        
        this.init();
    }
    
    init() {
        this.createDashboardStructure();
        this.loadPortfolioAnalytics();
        
        // Refresh analytics every 5 minutes
        setInterval(() => this.loadPortfolioAnalytics(), 300000);
    }
    
    createDashboardStructure() {
        if (!this.dashboardContainer) return;
        
        this.dashboardContainer.innerHTML = `
            <div class="dashboard-header">
                <h2>📊 Portfolio Analytics Dashboard</h2>
                <div class="dashboard-controls">
                    <button id="refresh-analytics" class="btn-primary">🔄 Refresh</button>
                    <button id="export-analytics" class="btn-secondary">📊 Export</button>
                </div>
            </div>
            
            <div class="analytics-grid">
                <!-- Key Metrics Row -->
                <div class="metrics-row">
                    <div class="metric-card" id="intelligence-score">
                        <div class="metric-icon">🧠</div>
                        <div class="metric-content">
                            <div class="metric-value">--</div>
                            <div class="metric-label">AI Intelligence Score</div>
                        </div>
                    </div>
                    
                    <div class="metric-card" id="portfolio-health">
                        <div class="metric-icon">🏥</div>
                        <div class="metric-content">
                            <div class="metric-value">--</div>
                            <div class="metric-label">Portfolio Health</div>
                        </div>
                    </div>
                    
                    <div class="metric-card" id="risk-score">
                        <div class="metric-icon">⚠️</div>
                        <div class="metric-content">
                            <div class="metric-value">--</div>
                            <div class="metric-label">Risk Score</div>
                        </div>
                    </div>
                    
                    <div class="metric-card" id="market-sentiment">
                        <div class="metric-icon">📈</div>
                        <div class="metric-content">
                            <div class="metric-value">--</div>
                            <div class="metric-label">Market Sentiment</div>
                        </div>
                    </div>
                </div>
                
                <!-- Charts Row -->
                <div class="charts-row">
                    <div class="chart-container">
                        <h3>Portfolio Allocation</h3>
                        <div id="allocation-chart" class="chart-placeholder">
                            <div class="loading-spinner">📊 Loading chart...</div>
                        </div>
                    </div>
                    
                    <div class="chart-container">
                        <h3>Performance vs Benchmark</h3>
                        <div id="performance-chart" class="chart-placeholder">
                            <div class="loading-spinner">📈 Loading chart...</div>
                        </div>
                    </div>
                </div>
                
                <!-- Insights Row -->
                <div class="insights-row">
                    <div class="insights-container">
                        <h3>💡 AI-Generated Insights</h3>
                        <div id="ai-insights" class="insights-list">
                            <div class="loading-spinner">🧠 Analyzing portfolio...</div>
                        </div>
                    </div>
                    
                    <div class="recommendations-container">
                        <h3>🎯 Strategic Recommendations</h3>
                        <div id="ai-recommendations" class="recommendations-list">
                            <div class="loading-spinner">🎯 Generating recommendations...</div>
                        </div>
                    </div>
                </div>
                
                <!-- Market Data Row -->
                <div class="market-data-row">
                    <div class="market-overview">
                        <h3>🌐 Live Market Overview</h3>
                        <div id="market-data" class="market-grid">
                            <div class="loading-spinner">🌐 Loading market data...</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add event listeners
        document.getElementById('refresh-analytics').addEventListener('click', () => {
            this.loadPortfolioAnalytics();
        });
        
        document.getElementById('export-analytics').addEventListener('click', () => {
            this.exportAnalytics();
        });
    }
    
    async loadPortfolioAnalytics() {
        try {
            showLoading('Loading enhanced portfolio analytics...');
            
            // Get portfolio data
            const portfolioResponse = await apiCall('/api/live-positions', 'GET');
            if (!portfolioResponse.success) {
                throw new Error('Failed to load portfolio data');
            }
            
            const portfolioData = portfolioResponse.data;
            
            // Get AI analysis
            const analysisResponse = await apiCall('/api/analyze-portfolio', 'POST', {
                portfolio_summary: portfolioData,
                target_return: 10,
                time_horizon_months: 12
            });
            
            if (analysisResponse.success) {
                this.updateMetrics(analysisResponse.data);
                this.updateInsights(analysisResponse.data);
            }
            
            // Load charts
            await this.loadCharts(portfolioData);
            
            // Load market data
            await this.loadMarketData();
            
            hideLoading();
            
        } catch (error) {
            console.error('Analytics loading error:', error);
            hideLoading();
            this.showError('Failed to load portfolio analytics. Please try again.');
        }
    }
    
    updateMetrics(analysisData) {
        // Update intelligence score
        const intelligenceScore = analysisData.intelligence_score || 0;
        this.updateMetricCard('intelligence-score', intelligenceScore, '/100', this.getScoreColor(intelligenceScore));
        
        // Update portfolio health
        const healthScore = analysisData.portfolio_health_score || 0;
        this.updateMetricCard('portfolio-health', healthScore, '/100', this.getScoreColor(healthScore));
        
        // Update risk score
        const riskScore = analysisData.risk_score || 0;
        this.updateMetricCard('risk-score', riskScore, '/100', this.getRiskColor(riskScore));
        
        // Update market sentiment
        const sentiment = analysisData.market_sentiment || 'Neutral';
        this.updateMetricCard('market-sentiment', sentiment, '', this.getSentimentColor(sentiment));
    }
    
    updateMetricCard(cardId, value, suffix, color) {
        const card = document.getElementById(cardId);
        if (!card) return;
        
        const valueElement = card.querySelector('.metric-value');
        if (valueElement) {
            valueElement.textContent = value + suffix;
            valueElement.style.color = color;
        }
        
        // Add animation
        card.style.transform = 'scale(1.05)';
        setTimeout(() => {
            card.style.transform = 'scale(1)';
        }, 200);
    }
    
    updateInsights(analysisData) {
        const insightsContainer = document.getElementById('ai-insights');
        const recommendationsContainer = document.getElementById('ai-recommendations');
        
        // Update insights
        if (analysisData.key_insights && analysisData.key_insights.length > 0) {
            insightsContainer.innerHTML = '';
            analysisData.key_insights.forEach((insight, index) => {
                const insightElement = this.createInsightElement(insight, index);
                insightsContainer.appendChild(insightElement);
            });
        } else {
            insightsContainer.innerHTML = '<div class="no-data">No insights available</div>';
        }
        
        // Update recommendations
        if (analysisData.top_recommendations && analysisData.top_recommendations.length > 0) {
            recommendationsContainer.innerHTML = '';
            analysisData.top_recommendations.forEach((rec, index) => {
                const recElement = this.createRecommendationElement(rec, index);
                recommendationsContainer.appendChild(recElement);
            });
        } else {
            recommendationsContainer.innerHTML = '<div class="no-data">No recommendations available</div>';
        }
    }
    
    createInsightElement(insight, index) {
        const div = document.createElement('div');
        div.className = 'insight-item analytics-insight';
        
        const confidence = insight.confidence || 70;
        const category = insight.category || 'General';
        const impact = insight.impact_level || 'medium';
        
        div.innerHTML = `
            <div class="insight-header">
                <span class="insight-number">${index + 1}</span>
                <span class="insight-category">${category.toUpperCase()}</span>
                <span class="confidence-badge" style="background-color: ${this.getScoreColor(confidence)}">
                    ${confidence}%
                </span>
                <span class="impact-badge ${impact}">${this.getImpactIcon(impact)}</span>
            </div>
            <div class="insight-content">
                ${insight.insight || insight}
            </div>
        `;
        
        return div;
    }
    
    createRecommendationElement(recommendation, index) {
        const div = document.createElement('div');
        div.className = 'recommendation-item analytics-rec';
        
        div.innerHTML = `
            <div class="rec-header">
                <span class="rec-number">${index + 1}</span>
                <span class="rec-priority">HIGH</span>
            </div>
            <div class="rec-content">
                ${recommendation}
            </div>
        `;
        
        return div;
    }
    
    async loadCharts(portfolioData) {
        try {
            // For now, create placeholder charts
            // In a full implementation, these would load actual chart libraries
            
            this.createAllocationChart(portfolioData);
            this.createPerformanceChart(portfolioData);
            
        } catch (error) {
            console.error('Charts loading error:', error);
        }
    }
    
    createAllocationChart(portfolioData) {
        const container = document.getElementById('allocation-chart');
        if (!container || !portfolioData.positions) return;
        
        const positions = portfolioData.positions;
        const totalValue = positions.reduce((sum, pos) => sum + (pos.market_value || 0), 0);
        
        if (totalValue === 0) {
            container.innerHTML = '<div class="no-data">No position data available</div>';
            return;
        }
        
        let html = '<div class="allocation-bars">';
        
        positions.forEach((pos, index) => {
            const percentage = ((pos.market_value || 0) / totalValue * 100).toFixed(1);
            const color = this.getColorForIndex(index);
            
            html += `
                <div class="allocation-bar">
                    <div class="bar-info">
                        <span class="symbol">${pos.symbol}</span>
                        <span class="percentage">${percentage}%</span>
                    </div>
                    <div class="bar-visual">
                        <div class="bar-fill" style="width: ${percentage}%; background-color: ${color}"></div>
                    </div>
                    <div class="bar-value">$${(pos.market_value || 0).toLocaleString()}</div>
                </div>
            `;
        });
        
        html += '</div>';
        container.innerHTML = html;
    }
    
    createPerformanceChart(portfolioData) {
        const container = document.getElementById('performance-chart');
        if (!container) return;
        
        // Simplified performance visualization
        const totalPnL = portfolioData.summary?.total_unrealized_pnl || 0;
        const pnlPercentage = portfolioData.summary?.unrealized_pnl_percentage || 0;
        
        const isPositive = totalPnL >= 0;
        const color = isPositive ? '#27AE60' : '#E74C3C';
        
        container.innerHTML = `
            <div class="performance-summary">
                <div class="performance-main">
                    <div class="performance-value" style="color: ${color}">
                        ${isPositive ? '+' : ''}$${totalPnL.toLocaleString()}
                    </div>
                    <div class="performance-percentage" style="color: ${color}">
                        ${isPositive ? '+' : ''}${pnlPercentage.toFixed(2)}%
                    </div>
                </div>
                <div class="performance-indicator">
                    <div class="indicator-bar">
                        <div class="indicator-fill" style="width: ${Math.abs(pnlPercentage) * 2}%; background-color: ${color}"></div>
                    </div>
                    <div class="indicator-label">vs. Initial Investment</div>
                </div>
            </div>
        `;
    }
    
    async loadMarketData() {
        const container = document.getElementById('market-data');
        if (!container) return;
        
        try {
            // Simulate market data (in real implementation, this would come from the backend)
            const marketData = {
                'S&P 500': { value: '4,150.25', change: '+0.85%', positive: true },
                'NASDAQ': { value: '12,845.50', change: '+1.20%', positive: true },
                'VIX': { value: '18.45', change: '-2.10%', positive: false },
                'USD/EUR': { value: '1.0825', change: '+0.15%', positive: true }
            };
            
            let html = '';
            Object.entries(marketData).forEach(([name, data]) => {
                const changeColor = data.positive ? '#27AE60' : '#E74C3C';
                html += `
                    <div class="market-item">
                        <div class="market-name">${name}</div>
                        <div class="market-value">${data.value}</div>
                        <div class="market-change" style="color: ${changeColor}">
                            ${data.change}
                        </div>
                    </div>
                `;
            });
            
            container.innerHTML = html;
            
        } catch (error) {
            container.innerHTML = '<div class="error">Failed to load market data</div>';
        }
    }
    
    exportAnalytics() {
        // Create analytics export
        const analyticsData = {
            timestamp: new Date().toISOString(),
            metrics: this.getCurrentMetrics(),
            insights: this.getCurrentInsights(),
            recommendations: this.getCurrentRecommendations()
        };
        
        const blob = new Blob([JSON.stringify(analyticsData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `auraquant-analytics-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
    
    getCurrentMetrics() {
        const metrics = {};
        ['intelligence-score', 'portfolio-health', 'risk-score', 'market-sentiment'].forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                const valueElement = element.querySelector('.metric-value');
                metrics[id] = valueElement ? valueElement.textContent : null;
            }
        });
        return metrics;
    }
    
    getCurrentInsights() {
        const insights = [];
        document.querySelectorAll('.analytics-insight').forEach(element => {
            const content = element.querySelector('.insight-content');
            if (content) {
                insights.push(content.textContent.trim());
            }
        });
        return insights;
    }
    
    getCurrentRecommendations() {
        const recommendations = [];
        document.querySelectorAll('.analytics-rec').forEach(element => {
            const content = element.querySelector('.rec-content');
            if (content) {
                recommendations.push(content.textContent.trim());
            }
        });
        return recommendations;
    }
    
    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `
            <div class="error-content">
                <span class="error-icon">❌</span>
                <span class="error-text">${message}</span>
            </div>
        `;
        
        this.dashboardContainer.insertBefore(errorDiv, this.dashboardContainer.firstChild);
        
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }
    
    // Utility methods
    getScoreColor(score) {
        if (score >= 80) return '#2E86AB';
        if (score >= 60) return '#4ECDC4';
        if (score >= 40) return '#FDCB6E';
        return '#FF6B6B';
    }
    
    getRiskColor(score) {
        if (score >= 80) return '#E74C3C';
        if (score >= 60) return '#F39C12';
        if (score >= 40) return '#F1C40F';
        return '#27AE60';
    }
    
    getSentimentColor(sentiment) {
        const sentimentLower = sentiment.toLowerCase();
        if (sentimentLower.includes('positive') || sentimentLower.includes('bullish')) return '#27AE60';
        if (sentimentLower.includes('negative') || sentimentLower.includes('bearish')) return '#E74C3C';
        return '#95A5A6';
    }
    
    getImpactIcon(impact) {
        const icons = {
            'critical': '🚨',
            'high': '⚠️',
            'medium': '📊',
            'low': 'ℹ️'
        };
        return icons[impact] || '📊';
    }
    
    getColorForIndex(index) {
        const colors = ['#2E86AB', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#FDCB6E', '#E17055', '#74B9FF'];
        return colors[index % colors.length];
    }
}

// Initialize analytics dashboard
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('analytics-dashboard')) {
        window.analyticsDashboard = new AnalyticsDashboard();
    }
}); 