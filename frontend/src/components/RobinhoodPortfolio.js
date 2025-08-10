import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Card,
  Typography,
  alpha,
  Divider,
  Button,
  CircularProgress
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon
} from '@mui/icons-material';
import { Doughnut, Line } from 'react-chartjs-2';
import { ROBINHOOD_COLORS, getDoughnutOptions, getChartOptions } from '../utils/chartSetup';
import axios from 'axios';

function RobinhoodPortfolio() {
  const { portfolioId } = useParams();
  const [portfolioData, setPortfolioData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedView, setSelectedView] = useState('allocation');

  const fetchPortfolioData = useCallback(async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const response = await axios.get(`http://localhost:8000/portfolio/${portfolioId}`, { headers });
      setPortfolioData(response.data);
    } catch (error) {
      console.error('Failed to fetch portfolio data:', error);
    } finally {
      setLoading(false);
    }
  }, [portfolioId]);

  useEffect(() => {
    fetchPortfolioData();
  }, [portfolioId, fetchPortfolioData]);

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value || 0);
  };

  const formatPercent = (value, showSign = true) => {
    const color = value >= 0 ? ROBINHOOD_COLORS.primary : ROBINHOOD_COLORS.danger;
    const sign = value >= 0 ? '+' : '';
    return {
      color,
      text: `${showSign ? sign : ''}${value.toFixed(2)}%`
    };
  };

  // Create allocation chart data
  const getAllocationChartData = () => {
    if (!portfolioData || !portfolioData.holdings) return null;

    const labels = portfolioData.holdings.map(h => h.ticker);
    const data = portfolioData.holdings.map(h => h.current_value);
    
    // Generate colors for each holding
    const colors = portfolioData.holdings.map((_, index) => {
      const hue = (index * 137.508) % 360; // Golden angle approximation for nice color distribution
      return `hsl(${hue}, 70%, 60%)`;
    });

    return {
      labels,
      datasets: [{
        data,
        backgroundColor: colors,
        borderWidth: 0,
        hoverBorderWidth: 2,
        hoverBorderColor: '#ffffff'
      }]
    };
  };

  // Create performance chart data
  const getPerformanceChartData = () => {
    if (!portfolioData || !portfolioData.holdings) return null;

    // Mock historical data for demo
    const days = 30;
    const labels = Array.from({ length: days }, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - (days - 1 - i));
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });

    const baseValue = portfolioData.total_cost;
    const currentValue = portfolioData.total_value;
    const dailyReturn = Math.pow(currentValue / baseValue, 1 / days) - 1;

    const data = Array.from({ length: days }, (_, i) => {
      const volatility = 0.02;
      const randomFactor = 1 + (Math.random() - 0.5) * volatility;
      return baseValue * Math.pow(1 + dailyReturn, i) * randomFactor;
    });

    return {
      labels,
      datasets: [{
        label: 'Portfolio Value',
        data,
        borderColor: portfolioData.total_unrealized_pnl >= 0 ? ROBINHOOD_COLORS.primary : ROBINHOOD_COLORS.danger,
        backgroundColor: alpha(portfolioData.total_unrealized_pnl >= 0 ? ROBINHOOD_COLORS.primary : ROBINHOOD_COLORS.danger, 0.1),
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 4,
        pointHoverBackgroundColor: '#ffffff'
      }]
    };
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <CircularProgress sx={{ color: ROBINHOOD_COLORS.primary }} />
      </Box>
    );
  }

  if (!portfolioData) {
    return (
      <Box sx={{ textAlign: 'center', py: 8 }}>
        <Typography color="text.secondary">Portfolio data not available</Typography>
      </Box>
    );
  }

  const allocationData = getAllocationChartData();
  const performanceData = getPerformanceChartData();
  const totalPnLFormatted = formatPercent(portfolioData.total_unrealized_pnl_percent);

  return (
    <Box sx={{ 
      bgcolor: '#0D1421', 
      minHeight: '100vh', 
      color: 'white',
      fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
    }}>
      {/* Header */}
      <Box sx={{ p: 3, borderBottom: `1px solid ${alpha('#ffffff', 0.1)}` }}>
        <Typography 
          variant="h4" 
          sx={{ 
            fontWeight: '300', 
            color: 'white',
            mb: 1
          }}
        >
          {portfolioData.name}
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <Typography 
            variant="h2" 
            sx={{ 
              fontWeight: '300', 
              color: 'white',
              fontSize: '2.5rem'
            }}
          >
            {formatCurrency(portfolioData.total_value)}
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            {portfolioData.total_unrealized_pnl >= 0 ? 
              <TrendingUpIcon sx={{ color: ROBINHOOD_COLORS.primary, fontSize: '1.2rem' }} /> :
              <TrendingDownIcon sx={{ color: ROBINHOOD_COLORS.danger, fontSize: '1.2rem' }} />
            }
            <Typography 
              sx={{ 
                color: totalPnLFormatted.color, 
                fontWeight: '400',
                fontSize: '1rem'
              }}
            >
              {formatCurrency(portfolioData.total_unrealized_pnl)} ({totalPnLFormatted.text})
            </Typography>
          </Box>
        </Box>

        {/* View Toggle */}
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant={selectedView === 'performance' ? 'contained' : 'outlined'}
            onClick={() => setSelectedView('performance')}
            sx={{
              color: selectedView === 'performance' ? '#000' : ROBINHOOD_COLORS.primary,
              borderColor: ROBINHOOD_COLORS.primary,
              bgcolor: selectedView === 'performance' ? ROBINHOOD_COLORS.primary : 'transparent',
              '&:hover': {
                bgcolor: selectedView === 'performance' ? ROBINHOOD_COLORS.primaryDark : alpha(ROBINHOOD_COLORS.primary, 0.1)
              },
              textTransform: 'none',
              fontWeight: '500'
            }}
          >
            Performance
          </Button>
          <Button
            variant={selectedView === 'allocation' ? 'contained' : 'outlined'}
            onClick={() => setSelectedView('allocation')}
            sx={{
              color: selectedView === 'allocation' ? '#000' : ROBINHOOD_COLORS.primary,
              borderColor: ROBINHOOD_COLORS.primary,
              bgcolor: selectedView === 'allocation' ? ROBINHOOD_COLORS.primary : 'transparent',
              '&:hover': {
                bgcolor: selectedView === 'allocation' ? ROBINHOOD_COLORS.primaryDark : alpha(ROBINHOOD_COLORS.primary, 0.1)
              },
              textTransform: 'none',
              fontWeight: '500'
            }}
          >
            Allocation
          </Button>
        </Box>
      </Box>

      <Box sx={{ p: 3 }}>
        {/* Main Chart */}
        <Card sx={{ 
          bgcolor: '#1B2232', 
          mb: 3, 
          border: `1px solid ${alpha('#ffffff', 0.1)}`,
          borderRadius: 2
        }}>
          <Box sx={{ p: 3 }}>
            {selectedView === 'performance' && performanceData && (
              <Box sx={{ height: 300 }}>
                <Line 
                  data={performanceData} 
                  options={getChartOptions()} 
                />
              </Box>
            )}
            
            {selectedView === 'allocation' && allocationData && (
              <Box sx={{ height: 300 }}>
                <Doughnut 
                  data={allocationData} 
                  options={getDoughnutOptions('Portfolio Allocation')} 
                />
              </Box>
            )}
          </Box>
        </Card>

        {/* Holdings List */}
        <Card sx={{ 
          bgcolor: '#1B2232', 
          border: `1px solid ${alpha('#ffffff', 0.1)}`,
          borderRadius: 2
        }}>
          <Box sx={{ p: 3 }}>
            <Typography 
              variant="h6" 
              sx={{ 
                mb: 3, 
                fontWeight: '500', 
                color: 'white' 
              }}
            >
              Holdings
            </Typography>
            
            {portfolioData.holdings.map((holding, index) => {
              const pnlFormatted = formatPercent(holding.unrealized_pnl_percent);
              
              return (
                <Box key={index}>
                  <Box sx={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center',
                    py: 2
                  }}>
                    <Box>
                      <Typography 
                        variant="h6" 
                        sx={{ 
                          fontWeight: '500', 
                          color: 'white',
                          fontSize: '1rem'
                        }}
                      >
                        {holding.ticker}
                      </Typography>
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          color: ROBINHOOD_COLORS.textSecondary,
                          fontSize: '0.875rem'
                        }}
                      >
                        {holding.quantity} shares
                      </Typography>
                    </Box>
                    
                    <Box sx={{ textAlign: 'right' }}>
                      <Typography 
                        sx={{ 
                          fontWeight: '500', 
                          color: 'white',
                          fontSize: '1rem'
                        }}
                      >
                        {formatCurrency(holding.current_value)}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 0.5 }}>
                        {holding.unrealized_pnl >= 0 ? 
                          <TrendingUpIcon sx={{ color: pnlFormatted.color, fontSize: '0.875rem' }} /> :
                          <TrendingDownIcon sx={{ color: pnlFormatted.color, fontSize: '0.875rem' }} />
                        }
                        <Typography 
                          variant="body2" 
                          sx={{ 
                            color: pnlFormatted.color,
                            fontSize: '0.875rem'
                          }}
                        >
                          {pnlFormatted.text}
                        </Typography>
                      </Box>
                    </Box>
                  </Box>
                  
                  {index < portfolioData.holdings.length - 1 && (
                    <Divider sx={{ bgcolor: alpha('#ffffff', 0.1) }} />
                  )}
                </Box>
              );
            })}
          </Box>
        </Card>
      </Box>
    </Box>
  );
}

export default RobinhoodPortfolio;