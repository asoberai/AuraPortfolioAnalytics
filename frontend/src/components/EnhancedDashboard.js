import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  Grid,
  AppBar,
  Toolbar,
  IconButton,
  Avatar,
  Chip,
  Paper,
  Divider,
  CircularProgress,
  LinearProgress,
  useTheme,
  alpha
} from '@mui/material';
import {
  Add as AddIcon,
  Logout as LogoutIcon,
  Assessment as AssessmentIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  AccountBalance as PortfolioIcon,
  Security as SecurityIcon,
  Speed as SpeedIcon,
  Visibility as VisibilityIcon,
  ShowChart as ShowChartIcon,
  Analytics as AnalyticsIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

function EnhancedDashboard() {
  const [portfolios, setPortfolios] = useState([]);
  const [portfolioSummary, setPortfolioSummary] = useState(null);
  const [marketData, setMarketData] = useState({});
  const [loading, setLoading] = useState(true);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const theme = useTheme();

  useEffect(() => {
    fetchDashboardData();
    // Set up real-time updates every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      // Fetch portfolios
      const portfoliosResponse = await axios.get('http://localhost:8000/portfolios', { headers });
      setPortfolios(portfoliosResponse.data);

      // Fetch portfolio summaries with current values
      const summaryData = {
        totalValue: 0,
        totalCost: 0,
        totalPnL: 0,
        totalPnLPercent: 0,
        holdings: [],
        riskLevel: 'Medium'
      };

      for (const portfolio of portfoliosResponse.data) {
        try {
          const portfolioResponse = await axios.get(`http://localhost:8000/portfolio/${portfolio.id}`, { headers });
          const data = portfolioResponse.data;
          
          summaryData.totalValue += data.total_value || 0;
          summaryData.totalCost += data.total_cost || 0;
          summaryData.totalPnL += data.total_unrealized_pnl || 0;
          summaryData.holdings.push(...(data.holdings || []));
        } catch (error) {
          console.error(`Failed to fetch portfolio ${portfolio.id}:`, error);
        }
      }

      if (summaryData.totalCost > 0) {
        summaryData.totalPnLPercent = (summaryData.totalPnL / summaryData.totalCost) * 100;
      }

      setPortfolioSummary(summaryData);

      // Fetch market data for top holdings
      if (summaryData.holdings.length > 0) {
        const topTickers = summaryData.holdings
          .sort((a, b) => (b.current_value || 0) - (a.current_value || 0))
          .slice(0, 5)
          .map(h => h.ticker);
        
        const marketPromises = topTickers.map(async (ticker) => {
          try {
            const response = await axios.get(`http://localhost:8000/market/stock/${ticker}`);
            return { ticker, data: response.data };
          } catch (error) {
            console.error(`Failed to fetch market data for ${ticker}:`, error);
            return null;
          }
        });

        const marketResults = await Promise.all(marketPromises);
        const marketDataMap = {};
        marketResults.filter(Boolean).forEach(result => {
          marketDataMap[result.ticker] = result.data;
        });
        setMarketData(marketDataMap);
      }

    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value || 0);
  };

  const formatPercent = (value) => {
    const color = value >= 0 ? theme.palette.success.main : theme.palette.error.main;
    const icon = value >= 0 ? <TrendingUpIcon fontSize="small" /> : <TrendingDownIcon fontSize="small" />;
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', color }}>
        {icon}
        <Typography variant="inherit" sx={{ ml: 0.5 }}>
          {value >= 0 ? '+' : ''}{value.toFixed(2)}%
        </Typography>
      </Box>
    );
  };

  // Portfolio Summary Cards
  const SummaryCards = () => {
    if (!portfolioSummary) return null;

    const cards = [
      {
        title: 'Total Portfolio Value',
        value: formatCurrency(portfolioSummary.totalValue),
        subtitle: 'Across all portfolios',
        icon: <PortfolioIcon />,
        color: 'primary'
      },
      {
        title: 'Total P&L',
        value: formatCurrency(portfolioSummary.totalPnL),
        subtitle: formatPercent(portfolioSummary.totalPnLPercent),
        icon: portfolioSummary.totalPnL >= 0 ? <TrendingUpIcon /> : <TrendingDownIcon />,
        color: portfolioSummary.totalPnL >= 0 ? 'success' : 'error'
      },
      {
        title: 'Active Portfolios',
        value: portfolios.length,
        subtitle: `${portfolioSummary.holdings.length} holdings`,
        icon: <SecurityIcon />,
        color: 'info'
      },
      {
        title: 'Risk Level',
        value: portfolioSummary.riskLevel,
        subtitle: user?.risk_profile || 'Complete assessment',
        icon: <SpeedIcon />,
        color: 'warning'
      }
    ];

    return (
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {cards.map((card, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card 
              sx={{ 
                height: '100%',
                background: `linear-gradient(135deg, ${alpha(theme.palette[card.color].main, 0.1)} 0%, ${alpha(theme.palette[card.color].main, 0.05)} 100%)`,
                border: `1px solid ${alpha(theme.palette[card.color].main, 0.2)}`,
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: theme.shadows[8]
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
                  <Typography variant="h6" color={`${card.color}.main`}>
                    {card.title}
                  </Typography>
                </Box>
                <Typography variant="h4" fontWeight="bold" sx={{ mb: 1 }}>
                  {card.value}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {card.subtitle}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    );
  };

  // Top Holdings Performance
  const TopHoldings = () => {
    if (!portfolioSummary || portfolioSummary.holdings.length === 0) return null;

    const topHoldings = portfolioSummary.holdings
      .sort((a, b) => (b.current_value || 0) - (a.current_value || 0))
      .slice(0, 5);

    return (
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <TrendingUpIcon sx={{ mr: 1 }} />
            Top Holdings Performance
          </Typography>
          <Divider sx={{ mb: 2 }} />
          
          {topHoldings.map((holding, index) => {
            const marketInfo = marketData[holding.ticker];
            const pnlPercent = holding.unrealized_pnl_percent || 0;
            
            return (
              <Box key={index} sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Chip 
                      label={holding.ticker} 
                      size="small" 
                      color="primary" 
                      sx={{ mr: 2, minWidth: 60 }} 
                    />
                    <Typography variant="body2">
                      {formatCurrency(holding.current_value)}
                    </Typography>
                  </Box>
                  <Box sx={{ textAlign: 'right' }}>
                    {formatPercent(pnlPercent)}
                    {marketInfo && (
                      <Typography variant="caption" color="text.secondary" display="block">
                        Current: {formatCurrency(holding.current_price)}
                      </Typography>
                    )}
                  </Box>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={Math.min(Math.abs(pnlPercent), 20) * 5} 
                  color={pnlPercent >= 0 ? 'success' : 'error'}
                  sx={{ height: 4, borderRadius: 2 }}
                />
              </Box>
            );
          })}
        </CardContent>
      </Card>
    );
  };

  // Enhanced Portfolio List
  const PortfolioList = () => {
    return (
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Your Portfolios</Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={async () => {
                try {
                  const token = localStorage.getItem('token');
                  await axios.post('http://localhost:8000/portfolio/create', 
                    { name: `Portfolio ${portfolios.length + 1}` },
                    { headers: { Authorization: `Bearer ${token}` }}
                  );
                  fetchDashboardData();
                } catch (error) {
                  console.error('Failed to create portfolio:', error);
                }
              }}
              sx={{
                background: `linear-gradient(45deg, ${theme.palette.primary.main} 30%, ${theme.palette.secondary.main} 90%)`,
                '&:hover': {
                  background: `linear-gradient(45deg, ${theme.palette.primary.dark} 30%, ${theme.palette.secondary.dark} 90%)`,
                }
              }}
            >
              Create Portfolio
            </Button>
          </Box>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
              <CircularProgress />
            </Box>
          ) : portfolios.length === 0 ? (
            <Paper sx={{ p: 3, textAlign: 'center', backgroundColor: alpha(theme.palette.primary.main, 0.05) }}>
              <PortfolioIcon sx={{ fontSize: 60, color: theme.palette.primary.light, mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No portfolios yet
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Create your first portfolio to start tracking your investments
              </Typography>
            </Paper>
          ) : (
            <Grid container spacing={2}>
              {portfolios.map((portfolio) => (
                <Grid item xs={12} md={6} key={portfolio.id}>
                  <Card 
                    sx={{ 
                      cursor: 'pointer',
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'translateY(-2px)',
                        boxShadow: theme.shadows[4]
                      }
                    }}
                    onClick={() => navigate(`/portfolio/${portfolio.id}`)}
                  >
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Box>
                          <Typography variant="h6" gutterBottom>
                            {portfolio.name}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Created: {new Date(portfolio.created_at).toLocaleDateString()}
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <IconButton 
                            color="primary"
                            onClick={(e) => {
                              e.stopPropagation();
                              navigate(`/portfolio/${portfolio.id}`);
                            }}
                            sx={{ 
                              backgroundColor: alpha(theme.palette.primary.main, 0.1),
                              '&:hover': { backgroundColor: alpha(theme.palette.primary.main, 0.2) }
                            }}
                            title="Portfolio view"
                          >
                            <VisibilityIcon />
                          </IconButton>
                          <IconButton 
                            color="secondary"
                            onClick={(e) => {
                              e.stopPropagation();
                              navigate(`/portfolio/${portfolio.id}/robinhood`);
                            }}
                            sx={{ 
                              backgroundColor: alpha(theme.palette.secondary.main, 0.1),
                              '&:hover': { backgroundColor: alpha(theme.palette.secondary.main, 0.2) }
                            }}
                            title="Robinhood-style view"
                          >
                            <ShowChartIcon />
                          </IconButton>
                          <IconButton 
                            color="success"
                            onClick={(e) => {
                              e.stopPropagation();
                              navigate(`/portfolio/${portfolio.id}/analytics`);
                            }}
                            sx={{ 
                              backgroundColor: alpha(theme.palette.success.main, 0.1),
                              '&:hover': { backgroundColor: alpha(theme.palette.success.main, 0.2) }
                            }}
                            title="Advanced Analytics"
                          >
                            <AnalyticsIcon />
                          </IconButton>
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </CardContent>
      </Card>
    );
  };

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
          <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
            <Typography variant="h5" component="div" fontWeight="bold">
              AuraVest
            </Typography>
            <Chip 
              label="Enhanced" 
              size="small" 
              sx={{ 
                ml: 2, 
                backgroundColor: alpha(theme.palette.common.white, 0.2),
                color: 'white',
                fontWeight: 'bold'
              }} 
            />
          </Box>
          
          {user && (
            <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
              <Avatar sx={{ bgcolor: theme.palette.secondary.main, mr: 2 }}>
                {user.email?.charAt(0).toUpperCase()}
              </Avatar>
              <Box sx={{ display: { xs: 'none', sm: 'block' } }}>
                <Typography variant="body2">Welcome back</Typography>
                <Typography variant="caption">{user.email}</Typography>
              </Box>
            </Box>
          )}
          
          <IconButton 
            color="inherit" 
            onClick={handleLogout}
            sx={{ 
              backgroundColor: alpha(theme.palette.common.white, 0.1),
              '&:hover': { backgroundColor: alpha(theme.palette.common.white, 0.2) }
            }}
          >
            <LogoutIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {/* Summary Cards */}
        <SummaryCards />

        <Grid container spacing={3}>
          {/* Left Column */}
          <Grid item xs={12} lg={8}>
            <TopHoldings />
            <PortfolioList />
          </Grid>

          {/* Right Column */}
          <Grid item xs={12} lg={4}>
            {/* Quick Actions */}
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                  <SpeedIcon sx={{ mr: 1 }} />
                  Quick Actions
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Button 
                    variant={user?.risk_profile ? 'outlined' : 'contained'}
                    startIcon={<AssessmentIcon />}
                    onClick={() => navigate('/risk-questionnaire')}
                    fullWidth
                    color={user?.risk_profile ? 'primary' : 'warning'}
                  >
                    {user?.risk_profile ? 'Update Risk Profile' : 'Complete Risk Assessment'}
                  </Button>
                  
                  {portfolios.length > 0 && (
                    <Button 
                      variant="outlined" 
                      startIcon={<TrendingUpIcon />}
                      onClick={() => navigate(`/portfolio/${portfolios[0].id}/risk-analysis`)}
                      fullWidth
                    >
                      View Risk Analysis
                    </Button>
                  )}
                </Box>
              </CardContent>
            </Card>

            {/* Risk Profile Card */}
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Risk Profile
                </Typography>
                <Divider sx={{ mb: 2 }} />
                {user?.risk_profile ? (
                  <Box>
                    <Chip 
                      label={user.risk_profile} 
                      color={
                        user.risk_profile === 'Conservative' ? 'success' :
                        user.risk_profile === 'Moderate' ? 'warning' : 'error'
                      }
                      sx={{ mb: 2, fontSize: '0.9rem' }}
                    />
                    <Typography variant="body2" color="text.secondary">
                      Your investment strategy is aligned with {user.risk_profile.toLowerCase()} risk tolerance.
                    </Typography>
                  </Box>
                ) : (
                  <Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      Complete your risk assessment to get personalized recommendations.
                    </Typography>
                    <Button 
                      size="small" 
                      variant="contained" 
                      onClick={() => navigate('/risk-questionnaire')}
                    >
                      Get Started
                    </Button>
                  </Box>
                )}
              </CardContent>
            </Card>

            {/* Market Status */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Market Overview
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <Typography variant="body2" color="text.secondary">
                  Real-time data powered by Yahoo Finance
                </Typography>
                <Box sx={{ mt: 2 }}>
                  <Typography variant="caption" color="success.main">
                    • System Status: Online
                  </Typography>
                  <br />
                  <Typography variant="caption" color="primary.main">
                    • Last Update: {new Date().toLocaleTimeString()}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </>
  );
}

export default EnhancedDashboard;