import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Tabs,
  Tab,
  CircularProgress,
  Chip,
  useTheme,
  Paper,
  Divider
} from '@mui/material';
import { Line, Bar } from 'react-chartjs-2';
import '../utils/chartSetup'; // Import to register chart components
import { ROBINHOOD_COLORS, getChartOptions } from '../utils/chartSetup';
import axios from 'axios';

function RiskVisualization({ portfolioData }) {
  const [tabValue, setTabValue] = useState(0);
  const [riskData, setRiskData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [monteCarloData, setMonteCarloData] = useState(null);
  const [correlationData, setCorrelationData] = useState(null);
  const theme = useTheme();

  useEffect(() => {
    if (portfolioData && portfolioData.holdings) {
      fetchRiskAnalysis();
    }
  }, [portfolioData]);

  const fetchRiskAnalysis = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      // Fetch portfolio risk analysis
      const riskResponse = await axios.post(
        'http://localhost:8000/analysis/risk/portfolio',
        portfolioData,
        { headers }
      );
      setRiskData(riskResponse.data);

      // Fetch Monte Carlo simulation
      const monteCarloResponse = await axios.post(
        'http://localhost:8000/analysis/risk/monte-carlo',
        portfolioData,
        { headers }
      );
      setMonteCarloData(monteCarloResponse.data);

      // Fetch correlation analysis
      const correlationResponse = await axios.post(
        'http://localhost:8000/analysis/risk/covariance',
        portfolioData,
        { headers }
      );
      setCorrelationData(correlationResponse.data);

    } catch (error) {
      console.error('Error fetching risk analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  // Risk Metrics Cards
  const RiskMetricsCards = () => {
    if (!riskData) return null;

    const metrics = [
      {
        title: 'Portfolio VaR (95%)',
        value: `${(riskData.risk_analysis.risk_metrics.var_95 * 100).toFixed(2)}%`,
        color: 'error',
        description: 'Maximum expected loss (95% confidence)'
      },
      {
        title: 'Volatility',
        value: `${(riskData.risk_analysis.risk_metrics.weighted_volatility * 100).toFixed(2)}%`,
        color: 'warning',
        description: 'Portfolio annualized volatility'
      },
      {
        title: 'Sharpe Ratio',
        value: riskData.risk_analysis.risk_metrics.sharpe_ratio?.toFixed(3) || 'N/A',
        color: 'success',
        description: 'Risk-adjusted return measure'
      },
      {
        title: 'Diversification Benefit',
        value: `${(riskData.risk_analysis.risk_metrics.diversification_benefit * 100).toFixed(1)}%`,
        color: 'info',
        description: 'Risk reduction from diversification'
      }
    ];

    return (
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {metrics.map((metric, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card sx={{ height: '100%', background: `linear-gradient(45deg, ${theme.palette[metric.color].light}15, ${theme.palette[metric.color].main}08)` }}>
              <CardContent>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  {metric.title}
                </Typography>
                <Typography variant="h4" color={`${metric.color}.main`} fontWeight="bold">
                  {metric.value}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {metric.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    );
  };

  // Probability Density Function Chart
  const ProbabilityChart = ({ ticker = 'PORTFOLIO' }) => {
    if (!riskData) return <CircularProgress />;

    // Create sample probability density data
    const pdfData = Array.from({ length: 100 }, (_, i) => {
      const x = -0.5 + (i / 99) * 1.0; // -50% to +50% returns
      const variance = Math.pow(riskData.risk_analysis.risk_metrics.weighted_volatility, 2);
      const pdf = Math.exp(-0.5 * Math.pow(x, 2) / variance) / Math.sqrt(2 * Math.PI * variance);
      return { x: x * 100, y: pdf };
    });

    const chartData = {
      labels: pdfData.map(point => `${point.x.toFixed(1)}%`),
      datasets: [
        {
          label: 'Probability Density',
          data: pdfData.map(point => point.y),
          borderColor: theme.palette.primary.main,
          backgroundColor: `${theme.palette.primary.main}20`,
          fill: true,
          tension: 0.4
        }
      ]
    };

    const options = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: 'Return Probability Distribution'
        },
        tooltip: {
          callbacks: {
            label: (context) => `Probability: ${context.parsed.y.toExponential(3)}`
          }
        }
      },
      scales: {
        x: {
          title: {
            display: true,
            text: 'Return (%)'
          }
        },
        y: {
          title: {
            display: true,
            text: 'Probability Density'
          }
        }
      }
    };

    return (
      <Box sx={{ height: 400 }}>
        <Line data={chartData} options={options} />
      </Box>
    );
  };

  // Monte Carlo Simulation Chart
  const MonteCarloChart = () => {
    if (!monteCarloData) return <CircularProgress />;

    // Create histogram data from Monte Carlo results
    const returns = monteCarloData.results.final_values || [];
    const bins = 30;
    const minValue = Math.min(...returns);
    const maxValue = Math.max(...returns);
    const binWidth = (maxValue - minValue) / bins;

    const histogram = Array(bins).fill(0);
    const labels = [];

    returns.forEach(value => {
      const binIndex = Math.min(Math.floor((value - minValue) / binWidth), bins - 1);
      histogram[binIndex]++;
    });

    for (let i = 0; i < bins; i++) {
      const binStart = minValue + i * binWidth;
      const binEnd = binStart + binWidth;
      labels.push(`${((binStart / 100000 - 1) * 100).toFixed(0)}%`);
    }

    const chartData = {
      labels,
      datasets: [
        {
          label: 'Frequency',
          data: histogram,
          backgroundColor: `${theme.palette.secondary.main}60`,
          borderColor: theme.palette.secondary.main,
          borderWidth: 1
        }
      ]
    };

    const options = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: 'Monte Carlo Simulation Results (10,000 simulations)'
        }
      },
      scales: {
        x: {
          title: {
            display: true,
            text: 'Portfolio Return (%)'
          }
        },
        y: {
          title: {
            display: true,
            text: 'Frequency'
          }
        }
      }
    };

    return (
      <Box sx={{ height: 400 }}>
        <Bar data={chartData} options={options} />
      </Box>
    );
  };

  // Risk Breakdown Component
  const RiskBreakdown = () => {
    if (!correlationData) return <CircularProgress />;

    const riskContributions = correlationData.covariance_analysis.risk_contributions || {};
    
    const chartData = {
      labels: Object.keys(riskContributions),
      datasets: [
        {
          label: 'Risk Contribution (%)',
          data: Object.values(riskContributions).map(val => val * 100),
          backgroundColor: [
            theme.palette.primary.main,
            theme.palette.secondary.main,
            theme.palette.success.main,
            theme.palette.warning.main,
            theme.palette.error.main,
            theme.palette.info.main
          ].slice(0, Object.keys(riskContributions).length),
          borderWidth: 2,
          borderColor: '#fff'
        }
      ]
    };

    const options = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        title: {
          display: true,
          text: 'Risk Contribution by Holding'
        },
        tooltip: {
          callbacks: {
            label: (context) => `${context.label}: ${context.parsed.y.toFixed(2)}%`
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Risk Contribution (%)'
          }
        }
      }
    };

    return (
      <Box sx={{ height: 400 }}>
        <Bar data={chartData} options={options} />
      </Box>
    );
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%' }}>
      {/* Risk Metrics Overview */}
      <RiskMetricsCards />

      {/* Risk Level Indicator */}
      {riskData && (
        <Paper sx={{ p: 2, mb: 3, background: `linear-gradient(45deg, ${theme.palette.primary.light}10, ${theme.palette.primary.main}05)` }}>
          <Grid container alignItems="center" spacing={2}>
            <Grid item xs={12} sm={8}>
              <Typography variant="h6">Overall Risk Assessment</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Based on portfolio composition, volatility, and correlation analysis
              </Typography>
            </Grid>
            <Grid item xs={12} sm={4} sx={{ textAlign: { xs: 'left', sm: 'right' } }}>
              <Chip
                label={riskData.summary.overall_risk_level}
                color={
                  riskData.summary.overall_risk_level === 'Low' ? 'success' :
                  riskData.summary.overall_risk_level === 'Medium' ? 'warning' : 'error'
                }
                size="large"
                sx={{ fontWeight: 'bold', fontSize: '1rem' }}
              />
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* Visualization Tabs */}
      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} variant="fullWidth">
            <Tab label="Probability Distribution" />
            <Tab label="Monte Carlo Simulation" />
            <Tab label="Risk Breakdown" />
          </Tabs>
        </Box>

        <CardContent>
          {tabValue === 0 && <ProbabilityChart />}
          {tabValue === 1 && <MonteCarloChart />}
          {tabValue === 2 && <RiskBreakdown />}
        </CardContent>
      </Card>

      {/* Additional Risk Insights */}
      {riskData && (
        <Grid container spacing={2} sx={{ mt: 2 }}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Risk Insights
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="primary">
                    Concentration Risk: {(riskData.summary.concentration_risk * 100).toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {riskData.summary.concentration_risk > 0.4 ? 
                      'High concentration detected. Consider diversifying.' :
                      'Well-diversified portfolio structure.'
                    }
                  </Typography>
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="primary">
                    Diversification Score: {(riskData.summary.diversification_score * 100).toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {riskData.summary.diversification_score > 0.7 ? 
                      'Excellent diversification benefits.' :
                      'Could benefit from additional diversification.'
                    }
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Performance Metrics
                </Typography>
                <Divider sx={{ mb: 2 }} />
                {monteCarloData && (
                  <>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" color="secondary">
                        Expected Return (1 Year)
                      </Typography>
                      <Typography variant="h6">
                        {((monteCarloData.results.expected_return || 0) * 100).toFixed(2)}%
                      </Typography>
                    </Box>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" color="secondary">
                        Worst Case (5th Percentile)
                      </Typography>
                      <Typography variant="h6" color="error.main">
                        {((monteCarloData.results.percentile_5 || 0) * 100).toFixed(2)}%
                      </Typography>
                    </Box>
                  </>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );
}

export default RiskVisualization;