// AuraQuant Helper Utilities
// Common utility functions for the frontend

// Loading overlay functions
function showLoading(message = 'Processing...') {
    const overlay = document.getElementById('loadingOverlay');
    const loadingText = document.getElementById('loadingText');
    
    if (loadingText) {
        loadingText.textContent = message;
    }
    
    if (overlay) {
        overlay.style.display = 'flex';
    }
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

// Format currency values
function formatCurrency(value, decimals = 0) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    }).format(value);
}

// Format percentage values
function formatPercentage(value, decimals = 1) {
    return `${value.toFixed(decimals)}%`;
}

// Format large numbers with K, M, B suffixes
function formatLargeNumber(value) {
    if (Math.abs(value) >= 1e9) {
        return (value / 1e9).toFixed(1) + 'B';
    } else if (Math.abs(value) >= 1e6) {
        return (value / 1e6).toFixed(1) + 'M';
    } else if (Math.abs(value) >= 1e3) {
        return (value / 1e3).toFixed(1) + 'K';
    }
    return value.toString();
}

// Get risk level color class
function getRiskColorClass(riskScore) {
    if (riskScore <= 20) return 'text-success';
    if (riskScore <= 40) return 'text-info';
    if (riskScore <= 60) return 'text-warning';
    if (riskScore <= 80) return 'text-danger';
    return 'text-danger';
}

// Get risk level text
function getRiskLevelText(riskScore) {
    if (riskScore <= 20) return 'Very Low';
    if (riskScore <= 40) return 'Low';
    if (riskScore <= 60) return 'Moderate';
    if (riskScore <= 80) return 'High';
    return 'Very High';
}

// Debounce function for input events
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle function for frequent events
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Show toast notification
function showToast(message, type = 'info', duration = 3000) {
    // Create toast element if it doesn't exist
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1100;
            max-width: 350px;
        `;
        document.body.appendChild(toastContainer);
    }
    
    // Create toast
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.style.cssText = `
        background: white;
        border-left: 4px solid ${getToastColor(type)};
        padding: 1rem;
        margin-bottom: 0.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        animation: slideInRight 0.3s ease-out;
    `;
    
    toast.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" style="
                background: none;
                border: none;
                font-size: 1.2rem;
                cursor: pointer;
                color: #6b7280;
            ">&times;</button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (toast.parentNode) {
            toast.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => toast.remove(), 300);
        }
    }, duration);
}

function getToastColor(type) {
    const colors = {
        success: '#059669',
        error: '#dc2626',
        warning: '#d97706',
        info: '#2563eb'
    };
    return colors[type] || colors.info;
}

// Add CSS animations for toasts
if (!document.getElementById('toastStyles')) {
    const style = document.createElement('style');
    style.id = 'toastStyles';
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

// Local storage helpers
const storage = {
    set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.warn('Failed to save to localStorage:', error);
        }
    },
    
    get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.warn('Failed to read from localStorage:', error);
            return defaultValue;
        }
    },
    
    remove(key) {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.warn('Failed to remove from localStorage:', error);
        }
    },
    
    clear() {
        try {
            localStorage.clear();
        } catch (error) {
            console.warn('Failed to clear localStorage:', error);
        }
    }
};

// Copy text to clipboard
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('Copied to clipboard!', 'success', 2000);
        return true;
    } catch (error) {
        console.warn('Failed to copy to clipboard:', error);
        showToast('Failed to copy to clipboard', 'error', 2000);
        return false;
    }
}

// Download data as JSON file
function downloadJSON(data, filename = 'auraquant-data.json') {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Validate portfolio description format
function validatePortfolioDescription(description) {
    const errors = [];
    
    if (!description || description.trim().length === 0) {
        errors.push('Portfolio description cannot be empty');
        return { valid: false, errors };
    }
    
    // Check for basic format
    const hasPositions = /[A-Z]{2,5}:\s*\$?\d+/i.test(description);
    if (!hasPositions) {
        errors.push('Please include at least one position (e.g., AAPL: $10000)');
    }
    
    // Check for reasonable values
    const values = description.match(/\$?(\d+(?:,\d{3})*)/g);
    if (values) {
        const numericValues = values.map(v => parseInt(v.replace(/[$,]/g, '')));
        const totalValue = numericValues.reduce((sum, val) => sum + val, 0);
        
        if (totalValue < 100) {
            errors.push('Portfolio values seem too small (minimum $100)');
        }
        
        if (totalValue > 10000000) {
            errors.push('Portfolio values seem unusually large');
        }
    }
    
    return {
        valid: errors.length === 0,
        errors: errors
    };
}

// Parse portfolio description into structured data
function parsePortfolioDescription(description) {
    const positions = [];
    let cash = 0;
    let totalValue = 0;
    
    const lines = description.split(',').map(line => line.trim());
    
    lines.forEach(line => {
        // Match cash
        const cashMatch = line.match(/cash:\s*\$?(\d+(?:,\d{3})*)/i);
        if (cashMatch) {
            cash = parseInt(cashMatch[1].replace(/,/g, ''));
            totalValue += cash;
            return;
        }
        
        // Match positions
        const positionMatch = line.match(/([A-Z]{2,5}):\s*\$?(\d+(?:,\d{3})*)/i);
        if (positionMatch) {
            const symbol = positionMatch[1].toUpperCase();
            const value = parseInt(positionMatch[2].replace(/,/g, ''));
            
            positions.push({
                symbol: symbol,
                value: value,
                percentage: 0 // Will be calculated after totalValue is known
            });
            
            totalValue += value;
        }
    });
    
    // Calculate percentages
    positions.forEach(pos => {
        pos.percentage = (pos.value / totalValue) * 100;
    });
    
    return {
        positions: positions,
        cash: cash,
        totalValue: totalValue,
        cashPercentage: (cash / totalValue) * 100
    };
}

// Export all utilities to global scope
window.AuraQuantHelpers = {
    showLoading,
    hideLoading,
    formatCurrency,
    formatPercentage,
    formatLargeNumber,
    getRiskColorClass,
    getRiskLevelText,
    debounce,
    throttle,
    showToast,
    storage,
    copyToClipboard,
    downloadJSON,
    validatePortfolioDescription,
    parsePortfolioDescription
}; 