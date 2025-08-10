// AuraQuant Portfolio Component
// Handles portfolio analysis and generation display

class PortfolioComponent {
    constructor() {
        this.analysisSection = document.getElementById('analysisSection');
        this.generationSection = document.getElementById('generationSection');
        
        this.currentAnalysis = null;
        this.currentGeneration = null;
        
        this.init();
    }

    init() {
        // Approval button handlers
        document.getElementById('approveAll')?.addEventListener('click', () => {
            this.handleApproval('approve_all');
        });
        
        document.getElementById('modifyPositions')?.addEventListener('click', () => {
            this.handleApproval('modify_positions');
        });
        
        document.getElementById('rejectAndRegenerate')?.addEventListener('click', () => {
            this.handleApproval('reject_and_regenerate');
        });
    }

    displayAnalysis(analysisData) {
        this.currentAnalysis = analysisData;
        
        // Update metrics
        this.updateAnalysisMetrics(analysisData.analysis);
        
        // Update positions table
        this.updatePositionsTable(analysisData.analysis.positions);
        
        // Update recommendations
        this.updateRecommendations(analysisData.recommendations);
        
        // Show analysis section
        this.analysisSection.style.display = 'block';
        this.analysisSection.scrollIntoView({ behavior: 'smooth' });
    }

    updateAnalysisMetrics(analysis) {
        // Total Value
        document.getElementById('totalValue').textContent = `$${analysis.total_value.toLocaleString()}`;
        
        // Risk Score
        document.getElementById('riskScore').textContent = `${analysis.risk_score}/100`;
        
        // Risk Indicator
        const riskIndicator = document.getElementById('riskIndicator');
        riskIndicator.className = 'risk-indicator';
        if (analysis.risk_score <= 30) {
            riskIndicator.classList.add('low');
        } else if (analysis.risk_score <= 70) {
            riskIndicator.classList.add('medium');
        } else {
            riskIndicator.classList.add('high');
        }
        
        // Expected Return
        document.getElementById('expectedReturn').textContent = `${analysis.expected_return.toFixed(1)}%`;
        
        // Cash Allocation
        document.getElementById('cashAllocation').textContent = `${analysis.cash_percentage.toFixed(1)}%`;
    }

    updatePositionsTable(positions) {
        const tableContainer = document.getElementById('positionsTable');
        
        if (positions.length === 0) {
            tableContainer.innerHTML = '<p class="text-secondary">No positions found</p>';
            return;
        }
        
        const table = document.createElement('table');
        table.innerHTML = `
            <thead>
                <tr>
                    <th>Symbol</th>
                    <th>Value</th>
                    <th>Weight</th>
                    <th>Risk Score</th>
                    <th>Sector</th>
                    <th>YTD Return</th>
                </tr>
            </thead>
            <tbody>
                ${positions.map(pos => `
                    <tr>
                        <td><strong>${pos.symbol}</strong></td>
                        <td>$${pos.value.toLocaleString()}</td>
                        <td>${pos.weight.toFixed(1)}%</td>
                        <td>
                            <span class="${this.getRiskClass(pos.risk_score)}">
                                ${pos.risk_score ? pos.risk_score.toFixed(0) : 'N/A'}
                            </span>
                        </td>
                        <td>${pos.sector || 'Unknown'}</td>
                        <td class="${pos.ytd_return >= 0 ? 'text-success' : 'text-danger'}">
                            ${pos.ytd_return ? pos.ytd_return.toFixed(1) + '%' : 'N/A'}
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        `;
        
        tableContainer.innerHTML = '';
        tableContainer.appendChild(table);
    }

    updateRecommendations(recommendations) {
        const container = document.getElementById('recommendationsList');
        
        if (recommendations.length === 0) {
            container.innerHTML = '<p class="text-secondary">No recommendations at this time</p>';
            return;
        }
        
        container.innerHTML = recommendations.map(rec => `
            <div class="recommendation-item ${rec.priority}-priority">
                <h4>${rec.action}</h4>
                <p>${rec.reason}</p>
                <small>Priority: ${rec.priority.toUpperCase()} | Impact: ${rec.impact.toUpperCase()}</small>
            </div>
        `).join('');
    }

    displayGeneration(portfolioData) {
        this.currentGeneration = portfolioData;
        
        // Update strategy overview
        document.getElementById('strategyName').textContent = portfolioData.strategy_name;
        document.getElementById('strategyDescription').textContent = portfolioData.strategy_description;
        document.getElementById('strategyReturn').textContent = `${portfolioData.expected_return.toFixed(1)}%`;
        document.getElementById('strategyRisk').textContent = portfolioData.risk_level;
        
        // Update Sharpe ratio if available
        const sharpeRatio = portfolioData.performance_metrics?.expected_sharpe || 0;
        document.getElementById('strategySharpe').textContent = sharpeRatio.toFixed(2);
        
        // Update positions grid
        this.updateGeneratedPositions(portfolioData.positions);
        
        // Show generation section
        this.generationSection.style.display = 'block';
        this.generationSection.scrollIntoView({ behavior: 'smooth' });
    }

    updateGeneratedPositions(positions) {
        const container = document.getElementById('generatedPositions');
        
        container.innerHTML = positions.map(pos => `
            <div class="position-card">
                <div class="position-header">
                    <span class="position-symbol">${pos.symbol}</span>
                    <span class="position-allocation">${pos.allocation_percentage.toFixed(1)}%</span>
                </div>
                <div class="position-details">
                    <span>Value: $${pos.value.toLocaleString()}</span>
                    <span>Sector: ${pos.sector || 'Unknown'}</span>
                </div>
                ${pos.risk_score ? `
                    <div class="position-details">
                        <span class="${this.getRiskClass(pos.risk_score)}">
                            Risk: ${pos.risk_score.toFixed(0)}/100
                        </span>
                        ${pos.momentum_score ? `<span>Momentum: ${pos.momentum_score.toFixed(1)}</span>` : ''}
                    </div>
                ` : ''}
            </div>
        `).join('');
    }

    async handleApproval(action) {
        try {
            showLoading('Processing your decision...');
            
            let modifications = null;
            let newRequirements = null;
            
            if (action === 'modify_positions') {
                // In a real app, you'd show a modal for modifications
                modifications = [
                    { symbol: 'EXAMPLE', new_allocation: 15, reason: 'User requested modification' }
                ];
            } else if (action === 'reject_and_regenerate') {
                newRequirements = prompt('What changes would you like to see in the new portfolio?');
                if (!newRequirements) {
                    hideLoading();
                    return;
                }
            }
            
            const result = await api.approvePortfolio(action, modifications, newRequirements);
            hideLoading();
            
            if (result.success) {
                // Add success message to chat
                let message = '';
                switch (action) {
                    case 'approve_all':
                        message = '✅ Portfolio approved! Ready for implementation.';
                        break;
                    case 'modify_positions':
                        message = '✏️ Portfolio modifications noted. Generating updated portfolio...';
                        break;
                    case 'reject_and_regenerate':
                        message = '🔄 Portfolio rejected. Generating new portfolio with your requirements...';
                        break;
                }
                
                window.chatComponent.addMessage(message, 'ai');
                
                // If regenerating, trigger new generation
                if (action === 'reject_and_regenerate' && newRequirements) {
                    setTimeout(() => {
                        window.chatComponent.handleGenerateRequest(newRequirements);
                    }, 1000);
                }
            } else {
                window.chatComponent.addMessage(`❌ Action failed: ${result.error}`, 'ai');
            }
            
        } catch (error) {
            hideLoading();
            window.chatComponent.addMessage(`❌ Error processing approval: ${error.message}`, 'ai');
        }
    }

    getRiskClass(riskScore) {
        if (!riskScore) return '';
        if (riskScore <= 30) return 'text-success';
        if (riskScore <= 70) return 'text-warning';
        return 'text-danger';
    }
}

// Global functions for closing sections
window.closeSection = function(sectionId) {
    document.getElementById(sectionId).style.display = 'none';
};

// Initialize portfolio component when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.portfolioComponent = new PortfolioComponent();
}); 