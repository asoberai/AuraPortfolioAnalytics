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
  List,
  ListItem,
  ListItemText,
  Chip
} from '@mui/material';
import { Add as AddIcon, Logout as LogoutIcon, Assessment as AssessmentIcon } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

function Dashboard() {
  const [portfolios, setPortfolios] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchPortfolios();
  }, []);

  const fetchPortfolios = async () => {
    try {
      const response = await axios.get('/portfolios');
      setPortfolios(response.data);
    } catch (error) {
      console.error('Failed to fetch portfolios:', error);
    } finally {
      setLoading(false);
    }
  };

  const createPortfolio = async () => {
    try {
      const response = await axios.post('/portfolio/create', null, {
        params: { name: `Portfolio ${portfolios.length + 1}` }
      });
      fetchPortfolios(); // Refresh list
    } catch (error) {
      console.error('Failed to create portfolio:', error);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            AuraVest Dashboard
          </Typography>
          <IconButton color="inherit" onClick={handleLogout}>
            <LogoutIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Grid container spacing={3}>
          {/* Welcome Section */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h4" gutterBottom>
                  Welcome back!
                </Typography>
                <Typography variant="body1" color="textSecondary">
                  Email: {user?.email}
                </Typography>
                {user?.risk_profile && (
                  <Chip 
                    label={`Risk Profile: ${user.risk_profile}`} 
                    color="primary" 
                    sx={{ mt: 1 }}
                  />
                )}
                {!user?.risk_profile && (
                  <Box sx={{ mt: 2 }}>
                    <Button 
                      variant="outlined" 
                      startIcon={<AssessmentIcon />}
                      onClick={() => navigate('/risk-questionnaire')}
                    >
                      Complete Risk Assessment
                    </Button>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Portfolios Section */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="h5">
                    Your Portfolios
                  </Typography>
                  <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={createPortfolio}
                  >
                    Create Portfolio
                  </Button>
                </Box>

                {loading ? (
                  <Typography>Loading portfolios...</Typography>
                ) : portfolios.length === 0 ? (
                  <Typography color="textSecondary">
                    No portfolios yet. Create your first portfolio to get started!
                  </Typography>
                ) : (
                  <List>
                    {portfolios.map((portfolio) => (
                      <ListItem
                        key={portfolio.id}
                        button
                        onClick={() => navigate(`/portfolio/${portfolio.id}`)}
                        sx={{ border: 1, borderColor: 'divider', borderRadius: 1, mb: 1 }}
                      >
                        <ListItemText
                          primary={portfolio.name}
                          secondary={`Created: ${new Date(portfolio.created_at).toLocaleDateString()}`}
                        />
                      </ListItem>
                    ))}
                  </List>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Quick Actions */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Quick Actions
                </Typography>
                <Box display="flex" flexDirection="column" gap={1}>
                  <Button 
                    variant="outlined" 
                    onClick={() => navigate('/risk-questionnaire')}
                  >
                    Update Risk Profile
                  </Button>
                  <Button 
                    variant="outlined" 
                    onClick={createPortfolio}
                  >
                    Create New Portfolio
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* System Info */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  System Status
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  AuraVest MVP - Phase 1
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Features: Authentication, Risk Profiling, Portfolio Tracking
                </Typography>
                <Chip label="PRD Compliant" color="success" size="small" sx={{ mt: 1 }} />
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </>
  );
}

export default Dashboard; 