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
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle
} from '@mui/material';
import { 
  Add as AddIcon, 
  ArrowBack as ArrowBackIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';
import axios from 'axios';

function Portfolio() {
  const { portfolioId } = useParams();
  const navigate = useNavigate();
  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deleteDialog, setDeleteDialog] = useState({ open: false, holdingId: null, ticker: '', quantity: 0 });

  useEffect(() => {
    fetchPortfolio();
  }, [portfolioId]);

  const fetchPortfolio = async () => {
    try {
      const response = await axios.get(`/portfolio/${portfolioId}`);
      setPortfolio(response.data);
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to fetch portfolio');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    if (value === null || value === undefined) return 'N/A';
    return `$${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const formatPercent = (value) => {
    if (value === null || value === undefined) return 'N/A';
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const getPercentColor = (value) => {
    if (value === null || value === undefined) return 'default';
    return value >= 0 ? 'success' : 'error';
  };

  const handleDeleteHolding = (holding) => {
    setDeleteDialog({
      open: true,
      holdingId: holding.id,
      ticker: holding.ticker || holding.ticker_symbol,
      quantity: holding.quantity
    });
  };

  const confirmDeleteHolding = async () => {
    try {
      await axios.delete(`/portfolio/${portfolioId}/holdings/${deleteDialog.holdingId}`);
      setDeleteDialog({ open: false, holdingId: null, ticker: '', quantity: 0 });
      fetchPortfolio(); // Refresh portfolio data
    } catch (error) {
      console.error('Failed to delete holding:', error);
    }
  };

  const cancelDeleteHolding = () => {
    setDeleteDialog({ open: false, holdingId: null, ticker: '', quantity: 0 });
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container>
        <Typography color="error" align="center" sx={{ mt: 4 }}>
          {error}
        </Typography>
        <Box textAlign="center" sx={{ mt: 2 }}>
          <Button onClick={() => navigate('/dashboard')}>
            Back to Dashboard
          </Button>
        </Box>
      </Container>
    );
  }

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            onClick={() => navigate('/dashboard')}
          >
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            {portfolio.name}
          </Typography>
          <Button
            color="inherit"
            startIcon={<AddIcon />}
            onClick={() => navigate(`/portfolio/${portfolioId}/add-holding`)}
          >
            Add Holding
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        {/* Portfolio Summary */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h4" gutterBottom>
              Portfolio Summary
            </Typography>
            <Box display="flex" alignItems="center" gap={2}>
              <Typography variant="h5" color="primary">
                Total Value: {formatCurrency(portfolio.total_value)}
              </Typography>
              <Chip
                label={`${portfolio.holdings.length} Holdings`}
                color="primary"
                variant="outlined"
              />
            </Box>
          </CardContent>
        </Card>

        {/* Holdings Table */}
        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Holdings
            </Typography>
            
            {portfolio.holdings.length === 0 ? (
              <Box textAlign="center" sx={{ py: 4 }}>
                <Typography color="textSecondary" gutterBottom>
                  No holdings in this portfolio yet
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => navigate(`/portfolio/${portfolioId}/add-holding`)}
                >
                  Add Your First Holding
                </Button>
              </Box>
            ) : (
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell><strong>Symbol</strong></TableCell>
                      <TableCell align="right"><strong>Shares</strong></TableCell>
                      <TableCell align="right"><strong>Purchase Price</strong></TableCell>
                      <TableCell align="right"><strong>Current Price</strong></TableCell>
                      <TableCell align="right"><strong>Current Value</strong></TableCell>
                      <TableCell align="right"><strong>Day Change</strong></TableCell>
                      <TableCell align="center"><strong>Actions</strong></TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {portfolio.holdings.map((holding) => (
                      <TableRow key={holding.id} hover>
                        <TableCell>
                          <Box display="flex" alignItems="center" gap={1}>
                            <Typography variant="h6">
                              {holding.ticker_symbol}
                            </Typography>
                            {holding.change_percent !== null && (
                              holding.change_percent >= 0 ? 
                                <TrendingUpIcon color="success" fontSize="small" /> :
                                <TrendingDownIcon color="error" fontSize="small" />
                            )}
                          </Box>
                        </TableCell>
                        <TableCell align="right">
                          {holding.quantity.toLocaleString()}
                        </TableCell>
                        <TableCell align="right">
                          {formatCurrency(holding.purchase_price)}
                        </TableCell>
                        <TableCell align="right">
                          {formatCurrency(holding.current_price)}
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body1" fontWeight="medium">
                            {formatCurrency(holding.current_value)}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Chip
                            label={formatPercent(holding.change_percent)}
                            color={getPercentColor(holding.change_percent)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="center">
                          <IconButton
                            color="error"
                            onClick={() => handleDeleteHolding(holding)}
                            size="small"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </CardContent>
        </Card>

        {/* Actions */}
        <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => navigate(`/portfolio/${portfolioId}/add-holding`)}
          >
            Add Holding
          </Button>
          <Button
            variant="outlined"
            onClick={fetchPortfolio}
          >
            Refresh Prices
          </Button>
        </Box>
      </Container>

      {/* Delete Holding Confirmation Dialog */}
      <Dialog
        open={deleteDialog.open}
        onClose={cancelDeleteHolding}
      >
        <DialogTitle>Delete Holding</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete {deleteDialog.quantity} shares of {deleteDialog.ticker}? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={cancelDeleteHolding} color="primary">
            Cancel
          </Button>
          <Button onClick={confirmDeleteHolding} color="error" autoFocus>
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

export default Portfolio; 