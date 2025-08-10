import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  Box,
  TextField,
  Button,
  Alert,
  AppBar,
  Toolbar,
  IconButton,
  Chip,
  Card,
  CardContent,
  CircularProgress,
  Autocomplete
} from '@mui/material';
import { 
  ArrowBack as ArrowBackIcon,
  Search as SearchIcon,
  TrendingUp as TrendingUpIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

function AddHolding() {
  const { portfolioId } = useParams();
  const navigate = useNavigate();
  const { token } = useAuth();
  const [formData, setFormData] = useState({
    ticker_symbol: '',
    quantity: '',
    purchase_price: '',
    purchase_date: new Date().toISOString().split('T')[0] // Default to today
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [tickerInfo, setTickerInfo] = useState(null);
  const [loadingTicker, setLoadingTicker] = useState(false);
  const [historicalPrice, setHistoricalPrice] = useState(null);
  const [loadingPrice, setLoadingPrice] = useState(false);
  const [popularTickers] = useState([
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
    'SPY', 'QQQ', 'VTI', 'VOO', 'BRK.B', 'JPM', 'JNJ', 'WMT'
  ]);

  // Fetch ticker information and historical price
  const fetchTickerInfo = async (ticker) => {
    if (!ticker || ticker.length < 1) {
      setTickerInfo(null);
      return;
    }
    
    setLoadingTicker(true);
    try {
      const response = await axios.get(`http://localhost:8000/market/stock/${ticker.toUpperCase()}`);
      setTickerInfo(response.data.basic_data);
      setError('');
    } catch (error) {
      console.log('Ticker not found or error:', error);
      setTickerInfo(null);
    } finally {
      setLoadingTicker(false);
    }
  };

  const fetchHistoricalPrice = async (ticker, date) => {
    if (!ticker || !date) {
      setHistoricalPrice(null);
      return;
    }

    setLoadingPrice(true);
    try {
      const response = await axios.get(`http://localhost:8000/market/historical/${ticker.toUpperCase()}?date=${date}`);
      setHistoricalPrice(response.data.price);
      setError('');
    } catch (error) {
      console.log('Error fetching historical price:', error);
      // Fall back to estimation if API fails
      try {
        const currentResponse = await axios.get(`http://localhost:8000/market/stock/${ticker.toUpperCase()}`);
        const currentPrice = currentResponse.data.basic_data?.price || 100;
        
        const purchaseDate = new Date(date);
        const today = new Date();
        const yearsDiff = (today - purchaseDate) / (365 * 24 * 60 * 60 * 1000);
        
        const growthRate = 0.08;
        const volatility = 0.2;
        const randomFactor = 1 + (Math.random() - 0.5) * volatility;
        const estimatedHistoricalPrice = currentPrice / Math.pow(1 + growthRate, yearsDiff) * randomFactor;
        
        setHistoricalPrice(Math.max(0.01, estimatedHistoricalPrice));
      } catch (fallbackError) {
        setHistoricalPrice(null);
      }
    } finally {
      setLoadingPrice(false);
    }
  };

  const handleChange = (field) => (event) => {
    const value = event.target.value;
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));

    // Auto-fetch ticker info when ticker changes
    if (field === 'ticker_symbol' && value.length >= 1) {
      fetchTickerInfo(value);
    }

    // Auto-fetch historical price when date changes
    if (field === 'purchase_date' && formData.ticker_symbol) {
      fetchHistoricalPrice(formData.ticker_symbol, value);
    }
  };

  // Effect to fetch historical price when ticker is selected
  useEffect(() => {
    if (formData.ticker_symbol && formData.purchase_date) {
      fetchHistoricalPrice(formData.ticker_symbol, formData.purchase_date);
    }
  }, [formData.ticker_symbol, formData.purchase_date]);

  const handleTickerSelect = (ticker) => {
    setFormData(prev => ({
      ...prev,
      ticker_symbol: ticker
    }));
    fetchTickerInfo(ticker);
  };

  const useHistoricalPrice = () => {
    if (historicalPrice) {
      setFormData(prev => ({
        ...prev,
        purchase_price: historicalPrice.toFixed(2)
      }));
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');

    try {
      const payload = {
        ticker_symbol: formData.ticker_symbol.toUpperCase(),
        quantity: parseFloat(formData.quantity),
        purchase_price: formData.purchase_price ? parseFloat(formData.purchase_price) : null,
        purchase_date: formData.purchase_date || null
      };

      await axios.post(`http://localhost:8000/portfolio/${portfolioId}/holdings`, payload, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      navigate(`/portfolio/${portfolioId}`);
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to add holding');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            onClick={() => navigate(`/portfolio/${portfolioId}`)}
          >
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h6" component="div">
            Add New Holding
          </Typography>
        </Toolbar>
      </AppBar>

      <Container component="main" maxWidth="sm">
        <Box sx={{ marginTop: 4, marginBottom: 4 }}>
          <Paper elevation={3} sx={{ padding: 4 }}>
            <Typography component="h1" variant="h4" align="center" gutterBottom>
              Add Holding
            </Typography>
            <Typography variant="body1" align="center" color="textSecondary" sx={{ mb: 3 }}>
              Add a stock or ETF to your portfolio
            </Typography>

            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

            <Box component="form" onSubmit={handleSubmit}>
              {/* Popular Tickers */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom color="text.secondary">
                  Popular Stocks & ETFs
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {popularTickers.map(ticker => (
                    <Chip
                      key={ticker}
                      label={ticker}
                      onClick={() => handleTickerSelect(ticker)}
                      variant={formData.ticker_symbol === ticker ? 'filled' : 'outlined'}
                      color={formData.ticker_symbol === ticker ? 'primary' : 'default'}
                      clickable
                      size="small"
                    />
                  ))}
                </Box>
              </Box>

              {/* Ticker Symbol Input */}
              <Box sx={{ position: 'relative' }}>
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  id="ticker_symbol"
                  label="Ticker Symbol (e.g., AAPL, GOOGL)"
                  name="ticker_symbol"
                  autoComplete="off"
                  autoFocus
                  value={formData.ticker_symbol}
                  onChange={handleChange('ticker_symbol')}
                  inputProps={{ style: { textTransform: 'uppercase' } }}
                  InputProps={{
                    endAdornment: loadingTicker ? <CircularProgress size={20} /> : null,
                  }}
                />
                {loadingTicker && (
                  <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                    Looking up ticker...
                  </Typography>
                )}
              </Box>

              {/* Ticker Information Card */}
              {tickerInfo && (
                <Card sx={{ mt: 2, mb: 2, bgcolor: 'primary.50', border: '1px solid', borderColor: 'primary.200' }}>
                  <CardContent sx={{ py: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <TrendingUpIcon color="primary" fontSize="small" />
                      <Typography variant="h6" color="primary">
                        {formData.ticker_symbol.toUpperCase()}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {tickerInfo.name || 'Stock Information'}
                      </Typography>
                    </Box>
                    <Typography variant="body2">
                      <strong>Current Price:</strong> ${tickerInfo.price?.toFixed(2) || 'N/A'}
                    </Typography>
                    {tickerInfo.change && (
                      <Typography 
                        variant="body2" 
                        color={tickerInfo.change >= 0 ? 'success.main' : 'error.main'}
                      >
                        <strong>Today's Change:</strong> ${tickerInfo.change.toFixed(2)} 
                        ({tickerInfo.changePercent >= 0 ? '+' : ''}{tickerInfo.changePercent?.toFixed(2)}%)
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              )}

              {/* Purchase Date */}
              <TextField
                margin="normal"
                required
                fullWidth
                id="purchase_date"
                label="Purchase Date"
                name="purchase_date"
                type="date"
                value={formData.purchase_date}
                onChange={handleChange('purchase_date')}
                InputLabelProps={{
                  shrink: true,
                }}
                inputProps={{
                  min: '2000-01-01',
                  max: new Date().toISOString().split('T')[0]
                }}
                helperText="Select any date from 2000 onwards"
              />

              {/* Historical Price Information */}
              {historicalPrice && formData.ticker_symbol && formData.purchase_date && (
                <Card sx={{ mt: 2, mb: 2, bgcolor: 'info.50', border: '1px solid', borderColor: 'info.200' }}>
                  <CardContent sx={{ py: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <InfoIcon color="info" fontSize="small" />
                      <Typography variant="subtitle2" color="info.main">
                        Estimated Historical Price
                      </Typography>
                    </Box>
                    <Typography variant="body2">
                      <strong>Estimated Price on {formData.purchase_date}:</strong> ${historicalPrice.toFixed(2)}
                    </Typography>
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={useHistoricalPrice}
                      sx={{ mt: 1 }}
                      disabled={loadingPrice}
                    >
                      {loadingPrice ? <CircularProgress size={16} /> : 'Use This Price'}
                    </Button>
                  </CardContent>
                </Card>
              )}

              {/* Quantity Input */}
              <TextField
                margin="normal"
                required
                fullWidth
                id="quantity"
                label="Number of Shares"
                name="quantity"
                type="number"
                value={formData.quantity}
                onChange={handleChange('quantity')}
                inputProps={{ min: 0.001, step: 0.001 }}
                helperText="You can enter fractional shares (e.g., 1.5 shares)"
              />

              {/* Purchase Price Input */}
              <TextField
                margin="normal"
                fullWidth
                id="purchase_price"
                label="Purchase Price Per Share"
                name="purchase_price"
                type="number"
                value={formData.purchase_price}
                onChange={handleChange('purchase_price')}
                inputProps={{ min: 0, step: 0.01 }}
                helperText="Enter the price you paid per share, or use the estimated historical price above"
              />

              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2 }}
                disabled={loading || !formData.ticker_symbol || !formData.quantity}
              >
                {loading ? 'Adding Holding...' : 'Add Holding'}
              </Button>

              <Button
                fullWidth
                variant="outlined"
                onClick={() => navigate(`/portfolio/${portfolioId}`)}
              >
                Cancel
              </Button>
            </Box>

            <Box sx={{ mt: 3, p: 3, bgcolor: 'grey.50', borderRadius: 2 }}>
              <Typography variant="h6" gutterBottom>
                📊 Portfolio Analytics Features
              </Typography>
              <Typography variant="body2" color="textSecondary" paragraph>
                <strong>Historical Analysis:</strong> Select any purchase date from 2000 onwards to see how your investments have performed over time.
              </Typography>
              <Typography variant="body2" color="textSecondary" paragraph>
                <strong>Real-time Tracking:</strong> Current prices are fetched from market data to show your portfolio's current value and performance.
              </Typography>
              <Typography variant="body2" color="textSecondary" paragraph>
                <strong>Risk Analytics:</strong> View comprehensive risk metrics, correlation analysis, and Monte Carlo simulations for your portfolio.
              </Typography>
              <Typography variant="body2" color="textSecondary">
                <strong>Future Projections:</strong> See potential future performance scenarios and optimize your portfolio allocation.
              </Typography>
            </Box>
          </Paper>
        </Box>
      </Container>
    </>
  );
}

export default AddHolding; 