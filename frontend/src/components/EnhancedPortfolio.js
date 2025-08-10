import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  AppBar,
  Toolbar,
  IconButton,
  CircularProgress,
  Grid,
  Tabs,
  Tab,
  LinearProgress,
  useTheme,
  alpha,
  Divider,
  Avatar
} from '@mui/material';
import { 
  Add as AddIcon, 
  ArrowBack as ArrowBackIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  PieChart as PieChartIcon,
  Timeline as TimelineIcon,
  Assessment as AssessmentIcon,
  Refresh as RefreshIcon,
  Speed as SpeedIcon
} from '@mui/icons-material';
import { Doughnut, Line, Bar } from 'react-chartjs-2';
import RiskVisualization from './RiskVisualization';
import axios from 'axios';

function EnhancedPortfolio() {
  const { portfolioId } = useParams();
  const navigate = useNavigate();
  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [tabValue, setTabValue] = useState(0);
  const [refreshing, setRefreshing] = useState(false);
  const [performanceData, setPerformanceData] = useState(null);
  const theme = useTheme();

  useEffect(() => {
    fetchPortfolio();
    // Auto-refresh every 60 seconds
    const interval = setInterval(() => {
      if (!refreshing) {
        fetchPortfolio(true);
      }
    }, 60000);
    return () => clearInterval(interval);
  }, [portfolioId]);

  const fetchPortfolio = async (silent = false) => {
    if (!silent) setLoading(true);
    if (silent) setRefreshing(true);
    
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };
      
      const response = await axios.get(`http://localhost:8000/portfolio/${portfolioId}`, { headers });
      setPortfolio(response.data);
      
      // Generate mock performance data for demonstration
      const mockPerformanceData = generateMockPerformanceData(response.data);
      setPerformanceData(mockPerformanceData);
      
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to fetch portfolio');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const generateMockPerformanceData = (portfolioData) => {
    // Generate 30 days of mock performance data
    const dates = [];
    const values = [];
    const baseValue = portfolioData.total_value || 100000;
    
    for (let i = 29; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      dates.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
      
      // Generate realistic random walk
      const randomChange = (Math.random() - 0.5) * 0.02; // ±1% daily change
      const value = i === 29 ? baseValue * 0.95 : values[values.length - 1] * (1 + randomChange);
      values.push(value);
    }
    
    return { dates, values };
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const formatCurrency = (value) => {
    if (value === null || value === undefined) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  const formatPercent = (value) => {
    if (value === null || value === undefined) return 'N/A';
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const getPercentColor = (value) => {
    if (value === null || value === undefined) return 'default';
    return value >= 0 ? 'success' : 'error';
  };

  // Portfolio Allocation Chart
  const AllocationChart = () => {
    if (!portfolio || portfolio.holdings.length === 0) return null;

    const data = {
      labels: portfolio.holdings.map(h => h.ticker),
      datasets: [{
        data: portfolio.holdings.map(h => h.current_value || 0),
        backgroundColor: [
          theme.palette.primary.main,
          theme.palette.secondary.main,
          theme.palette.success.main,
          theme.palette.warning.main,
          theme.palette.error.main,
          theme.palette.info.main,
          theme.palette.purple?.main || '#9c27b0',
          theme.palette.orange?.main || '#ff9800'
        ],
        borderWidth: 2,
        borderColor: theme.palette.background.paper
      }]
    };

    const options = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right',
          labels: {
            usePointStyle: true,
            padding: 20
          }
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              const value = context.parsed;
              const total = context.dataset.data.reduce((a, b) => a + b, 0);
              const percentage = ((value / total) * 100).toFixed(1);
              return `${context.label}: ${formatCurrency(value)} (${percentage}%)`;
            }
          }
        }
      }
    };

    return (
      <Box sx={{ height: 300 }}>
        <Doughnut data={data} options={options} />
      </Box>
    );
  };

  // Performance Chart
  const PerformanceChart = () => {
    if (!performanceData) return <CircularProgress />;

    const data = {
      labels: performanceData.dates,
      datasets: [{
        label: 'Portfolio Value',
        data: performanceData.values,
        borderColor: theme.palette.primary.main,
        backgroundColor: alpha(theme.palette.primary.main, 0.1),
        fill: true,
        tension: 0.4,
        borderWidth: 2,
        pointRadius: 0,
        pointHoverRadius: 6
      }]
    };

    const options = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            label: (context) => `Value: ${formatCurrency(context.parsed.y)}`
          }
        }
      },
      scales: {
        x: {
          grid: {
            display: false
          }
        },
        y: {
          beginAtZero: false,
          ticks: {
            callback: (value) => formatCurrency(value)
          }
        }
      },
      interaction: {
        intersect: false,
        mode: 'index'
      }
    };

    return (
      <Box sx={{ height: 300 }}>
        <Line data={data} options={options} />
      </Box>
    );
  };

  // Portfolio Summary Cards
  const SummaryCards = () => {
    if (!portfolio) return null;

    const cards = [
      {
        title: 'Total Value',
        value: formatCurrency(portfolio.total_value),
        change: formatPercent(portfolio.total_unrealized_pnl_percent),
        changeValue: formatCurrency(portfolio.total_unrealized_pnl),
        color: portfolio.total_unrealized_pnl >= 0 ? 'success' : 'error',
        icon: <TrendingUpIcon />
      },
      {
        title: 'Holdings',
        value: portfolio.holdings.length,
        change: 'Active positions',
        color: 'primary',
        icon: <PieChartIcon />
      },
      {
        title: 'Total Cost',
        value: formatCurrency(portfolio.total_cost),
        change: 'Initial investment',
        color: 'info',
        icon: <TimelineIcon />
      },
      {
        title: 'Day Change',
        value: portfolio.holdings.length > 0 ? 
          formatPercent(portfolio.holdings.reduce((acc, h) => acc + (h.change_percent || 0), 0) / portfolio.holdings.length) :
          'N/A',
        change: 'Average across holdings',
        color: 'warning',
        icon: <SpeedIcon />
      }
    ];

    return (
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {cards.map((card, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card 
              sx={{ 
                height: '100%',
                background: `linear-gradient(135deg, ${alpha(theme.palette[card.color].main, 0.1)} 0%, ${alpha(theme.palette[card.color].main, 0.05)} 100%)`,
                border: `1px solid ${alpha(theme.palette[card.color].main, 0.2)}`,
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: theme.shadows[4]
                }
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Avatar 
                    sx={{ 
                      bgcolor: theme.palette[card.color].main,
                      mr: 2,
                      width: 40,
                      height: 40
                    }}
                  >
                    {card.icon}
                  </Avatar>
                  <Typography variant="subtitle2" color="text.secondary">
                    {card.title}
                  </Typography>
                </Box>
                <Typography variant="h5" fontWeight="bold" color={`${card.color}.main`} sx={{ mb: 1 }}>
                  {card.value}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {card.changeValue && (
                    <span style={{ color: card.color === 'success' ? theme.palette.success.main : card.color === 'error' ? theme.palette.error.main : 'inherit' }}>
                      {card.changeValue}
                    </span>
                  )} {card.change}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    );
  };

  // Enhanced Holdings Table
  const HoldingsTable = () => {
    if (!portfolio || portfolio.holdings.length === 0) {
      return (
        <Paper sx={{ p: 4, textAlign: 'center', backgroundColor: alpha(theme.palette.primary.main, 0.05) }}>
          <PieChartIcon sx={{ fontSize: 60, color: theme.palette.primary.light, mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No holdings in this portfolio yet
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Add your first stock or ETF to start tracking your investment performance
          </Typography>
          <Button
            variant="contained"
            size="large"
            startIcon={<AddIcon />}
            onClick={() => navigate(`/portfolio/${portfolioId}/add-holding`)}
            sx={{
              background: `linear-gradient(45deg, ${theme.palette.primary.main} 30%, ${theme.palette.secondary.main} 90%)`,
            }}
          >
            Add Your First Holding
          </Button>
        </Paper>
      );
    }

    return (
      <TableContainer component={Paper} sx={{ borderRadius: 2, overflow: 'hidden' }}>
        <Table>
          <TableHead sx={{ backgroundColor: alpha(theme.palette.primary.main, 0.1) }}>
            <TableRow>
              <TableCell><Typography fontWeight="bold">Symbol</Typography></TableCell>
              <TableCell align="right"><Typography fontWeight="bold">Shares</Typography></TableCell>
              <TableCell align="right"><Typography fontWeight="bold">Avg Cost</Typography></TableCell>
              <TableCell align="right"><Typography fontWeight="bold">Current Price</Typography></TableCell>
              <TableCell align="right"><Typography fontWeight="bold">Market Value</Typography></TableCell>
              <TableCell align="right"><Typography fontWeight="bold">P&L</Typography></TableCell>
              <TableCell align="right"><Typography fontWeight="bold">Allocation</Typography></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {portfolio.holdings.map((holding, index) => {
              const allocation = ((holding.current_value / portfolio.total_value) * 100).toFixed(1);
              
              return (
                <TableRow 
                  key={holding.id} 
                  hover
                  sx={{ 
                    '&:nth-of-type(odd)': { 
                      backgroundColor: alpha(theme.palette.grey[100], 0.5) 
                    },
                    '&:hover': {
                      backgroundColor: alpha(theme.palette.primary.main, 0.05)
                    }
                  }}
                >
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Avatar 
                        sx={{ 
                          width: 32, 
                          height: 32, 
                          mr: 2, 
                          bgcolor: theme.palette.primary.main,
                          fontSize: '0.8rem',
                          fontWeight: 'bold'
                        }}
                      >
                        {holding.ticker.substring(0, 2)}
                      </Avatar>
                      <Box>
                        <Typography variant="h6" fontWeight="bold">
                          {holding.ticker}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Stock
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body1">
                      {holding.quantity.toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body1">
                      {formatCurrency(holding.purchase_price)}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body1" fontWeight="medium">
                      {formatCurrency(holding.current_price)}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body1" fontWeight="bold">
                      {formatCurrency(holding.current_value)}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Box sx={{ textAlign: 'right' }}>
                      <Typography 
                        variant="body2" 
                        color={getPercentColor(holding.unrealized_pnl_percent) + '.main'}
                        fontWeight="bold"
                      >
                        {formatPercent(holding.unrealized_pnl_percent)}
                      </Typography>
                      <Typography 
                        variant="caption" 
                        color={getPercentColor(holding.unrealized_pnl_percent) + '.main'}
                      >
                        {formatCurrency(holding.unrealized_pnl)}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell align="right">
                    <Box sx={{ minWidth: 60 }}>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        {allocation}%
                      </Typography>
                      <LinearProgress 
                        variant="determinate" 
                        value={parseFloat(allocation)} 
                        sx={{ 
                          height: 6, 
                          borderRadius: 3,
                          backgroundColor: alpha(theme.palette.grey[300], 0.3),
                          '& .MuiLinearProgress-bar': {
                            backgroundColor: theme.palette.primary.main,
                            borderRadius: 3
                          }
                        }} 
                      />
                    </Box>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
    );
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (error) {
    return (
      <Container>
        <Paper sx={{ p: 4, textAlign: 'center', mt: 4 }}>
          <Typography color="error.main" variant="h6" gutterBottom>
            {error}
          </Typography>
          <Button variant="contained" onClick={() => navigate('/dashboard')} sx={{ mt: 2 }}>
            Back to Dashboard
          </Button>
        </Paper>
      </Container>
    );
  }

  return (
    <>
      <AppBar 
        position="static"
        sx={{ 
          background: `linear-gradient(45deg, ${theme.palette.primary.main} 30%, ${theme.palette.secondary.main} 90%)`,
          boxShadow: theme.shadows[4]
        }}
      >
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            onClick={() => navigate('/dashboard')}
            sx={{ mr: 2 }}
          >
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            {portfolio?.name || 'Portfolio'}
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <IconButton
              color="inherit"
              onClick={() => fetchPortfolio()}
              disabled={refreshing}
              sx={{ 
                backgroundColor: alpha(theme.palette.common.white, 0.1),
                '&:hover': { backgroundColor: alpha(theme.palette.common.white, 0.2) }
              }}
            >
              <RefreshIcon />
            </IconButton>
            <Button
              color="inherit"
              startIcon={<AddIcon />}
              onClick={() => navigate(`/portfolio/${portfolioId}/add-holding`)}
              sx={{ 
                backgroundColor: alpha(theme.palette.common.white, 0.1),
                '&:hover': { backgroundColor: alpha(theme.palette.common.white, 0.2) }
              }}
            >
              Add Holding
            </Button>
          </Box>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {/* Summary Cards */}
        <SummaryCards />

        {/* Tabs */}
        <Card sx={{ mb: 3 }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={tabValue} onChange={handleTabChange} variant="fullWidth">
              <Tab 
                label="Holdings" 
                icon={<PieChartIcon />} 
                iconPosition="start"
                sx={{ minHeight: 64 }}
              />
              <Tab 
                label="Performance" 
                icon={<TimelineIcon />} 
                iconPosition="start"
                sx={{ minHeight: 64 }}
              />
              <Tab 
                label="Allocation" 
                icon={<AssessmentIcon />} 
                iconPosition="start"
                sx={{ minHeight: 64 }}
              />
              <Tab 
                label="Risk Analysis" 
                icon={<SpeedIcon />} 
                iconPosition="start"
                sx={{ minHeight: 64 }}
              />
            </Tabs>
          </Box>

          <CardContent sx={{ p: 3 }}>
            {tabValue === 0 && <HoldingsTable />}
            
            {tabValue === 1 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Portfolio Performance (30 Days)
                </Typography>
                <Divider sx={{ mb: 3 }} />
                <PerformanceChart />
              </Box>
            )}
            
            {tabValue === 2 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Asset Allocation
                </Typography>
                <Divider sx={{ mb: 3 }} />
                <AllocationChart />
              </Box>
            )}
            
            {tabValue === 3 && portfolio && (
              <RiskVisualization portfolioData={portfolio} />
            )}
          </CardContent>
        </Card>

        {refreshing && (
          <LinearProgress 
            sx={{ 
              position: 'fixed', 
              top: 0, 
              left: 0, 
              right: 0, 
              zIndex: theme.zIndex.appBar + 1 
            }} 
          />
        )}
      </Container>
    </>
  );
}

export default EnhancedPortfolio;