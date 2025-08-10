import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  RadioGroup,
  FormControlLabel,
  Radio,
  LinearProgress,
  Paper,
  Stepper,
  Step,
  StepLabel,
  Chip,
  Divider,
  useTheme,
  alpha,
  Fade,
  Slide
} from '@mui/material';
import {
  Security as SecurityIcon,
  TrendingUp as TrendingUpIcon,
  Speed as SpeedIcon,
  Psychology as PsychologyIcon,
  AccountBalance as AccountBalanceIcon,
  Timeline as TimelineIcon,
  School as SchoolIcon
} from '@mui/icons-material';
import { Doughnut, Radar } from 'react-chartjs-2';
import '../utils/chartSetup'; // Import to register chart components
import axios from 'axios';

const riskQuestions = [
  {
    id: 'investment_goals',
    title: 'Primary Investment Goal',
    icon: <TrendingUpIcon />,
    question: 'What is your primary investment objective?',
    options: [
      { value: 'preservation', label: 'Capital Preservation (Safety first)', weight: 1 },
      { value: 'income', label: 'Regular Income Generation', weight: 2 },
      { value: 'balanced', label: 'Balanced Growth and Income', weight: 3 },
      { value: 'growth', label: 'Long-term Capital Growth', weight: 4 },
      { value: 'aggressive', label: 'Maximum Growth Potential', weight: 5 }
    ]
  },
  {
    id: 'time_horizon',
    title: 'Investment Timeline',
    icon: <TimelineIcon />,
    question: 'How long do you plan to invest before needing the money?',
    options: [
      { value: '1', label: 'Less than 2 years', weight: 1 },
      { value: '3', label: '2-5 years', weight: 2 },
      { value: '7', label: '5-10 years', weight: 3 },
      { value: '15', label: '10-20 years', weight: 4 },
      { value: '25', label: 'More than 20 years', weight: 5 }
    ]
  },
  {
    id: 'risk_comfort',
    title: 'Risk Tolerance',
    icon: <SpeedIcon />,
    question: 'How comfortable are you with investment risk?',
    options: [
      { value: '1', label: 'I prefer guaranteed returns, even if lower', weight: 1 },
      { value: '2', label: 'I can accept small fluctuations for modest returns', weight: 2 },
      { value: '3', label: 'I can handle moderate swings for good returns', weight: 3 },
      { value: '4', label: 'I\'m comfortable with high volatility for high returns', weight: 4 },
      { value: '5', label: 'I seek maximum returns despite high risk', weight: 5 }
    ]
  },
  {
    id: 'market_experience',
    title: 'Investment Experience',
    icon: <SchoolIcon />,
    question: 'What is your level of investment experience?',
    options: [
      { value: 'beginner', label: 'Beginner (less than 1 year)', weight: 1 },
      { value: 'some', label: 'Some experience (1-3 years)', weight: 2 },
      { value: 'moderate', label: 'Moderate experience (3-7 years)', weight: 3 },
      { value: 'experienced', label: 'Experienced (7-15 years)', weight: 4 },
      { value: 'expert', label: 'Expert (15+ years)', weight: 5 }
    ]
  },
  {
    id: 'reaction_to_loss',
    title: 'Loss Reaction',
    icon: <PsychologyIcon />,
    question: 'If your portfolio lost 20% in a month, you would:',
    options: [
      { value: 'sell_all', label: 'Sell everything immediately to prevent further losses', weight: 1 },
      { value: 'sell_some', label: 'Sell some investments to reduce risk', weight: 2 },
      { value: 'hold', label: 'Hold and wait for recovery', weight: 3 },
      { value: 'buy_some', label: 'Buy more while prices are low', weight: 4 },
      { value: 'buy_aggressive', label: 'Invest significantly more at lower prices', weight: 5 }
    ]
  },
  {
    id: 'income_stability',
    title: 'Income Stability',
    icon: <AccountBalanceIcon />,
    question: 'How stable is your current income?',
    options: [
      { value: 'unstable', label: 'Highly variable or uncertain', weight: 1 },
      { value: 'somewhat', label: 'Somewhat stable with occasional changes', weight: 2 },
      { value: 'stable', label: 'Generally stable with predictable income', weight: 3 },
      { value: 'very_stable', label: 'Very stable with guaranteed income', weight: 4 },
      { value: 'growing', label: 'Stable and growing consistently', weight: 5 }
    ]
  },
  {
    id: 'investment_knowledge',
    title: 'Financial Knowledge',
    icon: <SecurityIcon />,
    question: 'How would you rate your financial market knowledge?',
    options: [
      { value: 'basic', label: 'Basic - I understand savings accounts', weight: 1 },
      { value: 'limited', label: 'Limited - I understand stocks and bonds', weight: 2 },
      { value: 'moderate', label: 'Moderate - I understand portfolio diversification', weight: 3 },
      { value: 'good', label: 'Good - I understand options and derivatives', weight: 4 },
      { value: 'expert', label: 'Expert - I understand complex strategies', weight: 5 }
    ]
  }
];

function PersonalizedRiskProfile({ onComplete }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [riskScore, setRiskScore] = useState(0);
  const [riskCategory, setRiskCategory] = useState('');
  const [showResults, setShowResults] = useState(false);
  const [loading, setLoading] = useState(false);
  const theme = useTheme();

  const calculateRiskScore = (currentAnswers) => {
    let totalScore = 0;
    let answeredQuestions = 0;

    riskQuestions.forEach(question => {
      const answer = currentAnswers[question.id];
      if (answer) {
        const option = question.options.find(opt => opt.value === answer);
        if (option) {
          totalScore += option.weight;
          answeredQuestions++;
        }
      }
    });

    const avgScore = answeredQuestions > 0 ? totalScore / answeredQuestions : 0;
    return avgScore;
  };

  const getRiskCategory = (score) => {
    if (score <= 1.5) return 'Conservative';
    if (score <= 2.5) return 'Moderate Conservative';
    if (score <= 3.5) return 'Moderate';
    if (score <= 4.5) return 'Moderate Aggressive';
    return 'Aggressive';
  };

  const getRiskColor = (category) => {
    switch (category) {
      case 'Conservative': return theme.palette.success.main;
      case 'Moderate Conservative': return theme.palette.info.main;
      case 'Moderate': return theme.palette.warning.main;
      case 'Moderate Aggressive': return theme.palette.orange?.main || theme.palette.warning.dark;
      case 'Aggressive': return theme.palette.error.main;
      default: return theme.palette.grey[500];
    }
  };

  const handleAnswer = (questionId, value) => {
    const newAnswers = { ...answers, [questionId]: value };
    setAnswers(newAnswers);
    
    const score = calculateRiskScore(newAnswers);
    setRiskScore(score);
    setRiskCategory(getRiskCategory(score));
  };

  const handleNext = () => {
    if (currentStep < riskQuestions.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleSubmit();
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      await axios.post('http://localhost:8000/profile/risk-questionnaire', answers, { headers });
      setShowResults(true);
      
      if (onComplete) {
        onComplete({ riskScore, riskCategory });
      }
    } catch (error) {
      console.error('Failed to submit risk questionnaire:', error);
    } finally {
      setLoading(false);
    }
  };

  // Risk Profile Visualization
  const RiskRadarChart = () => {
    const categories = [
      'Risk Tolerance',
      'Time Horizon', 
      'Experience',
      'Knowledge',
      'Loss Reaction',
      'Income Stability',
      'Growth Focus'
    ];

    const scores = [
      answers.risk_comfort ? riskQuestions.find(q => q.id === 'risk_comfort').options.find(o => o.value === answers.risk_comfort)?.weight || 0 : 0,
      answers.time_horizon ? parseInt(answers.time_horizon) / 5 : 0,
      answers.market_experience ? riskQuestions.find(q => q.id === 'market_experience').options.find(o => o.value === answers.market_experience)?.weight || 0 : 0,
      answers.investment_knowledge ? riskQuestions.find(q => q.id === 'investment_knowledge').options.find(o => o.value === answers.investment_knowledge)?.weight || 0 : 0,
      answers.reaction_to_loss ? riskQuestions.find(q => q.id === 'reaction_to_loss').options.find(o => o.value === answers.reaction_to_loss)?.weight || 0 : 0,
      answers.income_stability ? riskQuestions.find(q => q.id === 'income_stability').options.find(o => o.value === answers.income_stability)?.weight || 0 : 0,
      answers.investment_goals ? riskQuestions.find(q => q.id === 'investment_goals').options.find(o => o.value === answers.investment_goals)?.weight || 0 : 0
    ];

    const data = {
      labels: categories,
      datasets: [
        {
          label: 'Your Risk Profile',
          data: scores,
          backgroundColor: alpha(getRiskColor(riskCategory), 0.2),
          borderColor: getRiskColor(riskCategory),
          borderWidth: 2,
          pointBackgroundColor: getRiskColor(riskCategory),
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
          pointRadius: 6
        }
      ]
    };

    const options = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        r: {
          beginAtZero: true,
          max: 5,
          ticks: {
            stepSize: 1
          },
          grid: {
            color: alpha(theme.palette.text.primary, 0.1)
          }
        }
      }
    };

    return (
      <Box sx={{ height: 300 }}>
        <Radar data={data} options={options} />
      </Box>
    );
  };

  // Risk Score Gauge
  const RiskScoreGauge = () => {
    const scorePercent = (riskScore / 5) * 100;
    
    return (
      <Box sx={{ textAlign: 'center' }}>
        <Box sx={{ position: 'relative', display: 'inline-flex', mb: 2 }}>
          <Box 
            sx={{ 
              width: 120, 
              height: 120, 
              borderRadius: '50%', 
              background: `conic-gradient(${getRiskColor(riskCategory)} ${scorePercent * 3.6}deg, ${alpha(theme.palette.grey[300], 0.3)} 0deg)`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <Box 
              sx={{ 
                width: 80, 
                height: 80, 
                borderRadius: '50%', 
                backgroundColor: theme.palette.background.paper,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexDirection: 'column'
              }}
            >
              <Typography variant="h4" fontWeight="bold" color={getRiskColor(riskCategory)}>
                {riskScore.toFixed(1)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                /5.0
              </Typography>
            </Box>
          </Box>
        </Box>
        <Typography variant="h6" gutterBottom>
          Risk Score
        </Typography>
        <Chip 
          label={riskCategory} 
          sx={{ 
            backgroundColor: getRiskColor(riskCategory),
            color: 'white',
            fontWeight: 'bold'
          }} 
        />
      </Box>
    );
  };

  if (showResults) {
    return (
      <Fade in={showResults} timeout={800}>
        <Card sx={{ maxWidth: 800, mx: 'auto', mt: 4 }}>
          <CardContent sx={{ p: 4 }}>
            <Typography variant="h4" gutterBottom textAlign="center" color="primary.main">
              Your Personal Risk Profile
            </Typography>
            
            <Grid container spacing={4} sx={{ mt: 2 }}>
              <Grid item xs={12} md={6}>
                <RiskScoreGauge />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Profile Analysis
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Investment Style
                  </Typography>
                  <Typography variant="body1">
                    {riskCategory} Investor
                  </Typography>
                </Box>
                
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Recommended Allocation
                  </Typography>
                  <Typography variant="body1">
                    {riskScore <= 2 ? '70% Bonds, 30% Stocks' :
                     riskScore <= 3 ? '50% Bonds, 50% Stocks' :
                     riskScore <= 4 ? '30% Bonds, 70% Stocks' :
                     '10% Bonds, 90% Stocks'}
                  </Typography>
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Risk Characteristics
                  </Typography>
                  <Typography variant="body2">
                    {riskCategory === 'Conservative' && 'Focuses on capital preservation with minimal risk tolerance.'}
                    {riskCategory === 'Moderate Conservative' && 'Balanced approach with slight preference for safety.'}
                    {riskCategory === 'Moderate' && 'Balanced risk-return profile with growth focus.'}
                    {riskCategory === 'Moderate Aggressive' && 'Growth-oriented with higher risk tolerance.'}
                    {riskCategory === 'Aggressive' && 'Maximum growth potential with high risk acceptance.'}
                  </Typography>
                </Box>
              </Grid>

              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom textAlign="center">
                  Risk Profile Breakdown
                </Typography>
                <RiskRadarChart />
              </Grid>
            </Grid>

            <Box sx={{ textAlign: 'center', mt: 4 }}>
              <Button
                variant="contained"
                size="large"
                onClick={() => window.location.reload()}
                sx={{
                  background: `linear-gradient(45deg, ${theme.palette.primary.main} 30%, ${theme.palette.secondary.main} 90%)`,
                }}
              >
                Continue to Dashboard
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Fade>
    );
  }

  const currentQuestion = riskQuestions[currentStep];
  const progress = ((currentStep + 1) / riskQuestions.length) * 100;

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', mt: 4 }}>
      {/* Progress Header */}
      <Paper sx={{ p: 3, mb: 3, background: `linear-gradient(45deg, ${alpha(theme.palette.primary.main, 0.1)} 30%, ${alpha(theme.palette.secondary.main, 0.1)} 90%)` }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">Risk Assessment</Typography>
          <Chip label={`${currentStep + 1} of ${riskQuestions.length}`} color="primary" />
        </Box>
        <LinearProgress 
          variant="determinate" 
          value={progress} 
          sx={{ 
            height: 8, 
            borderRadius: 4,
            backgroundColor: alpha(theme.palette.grey[300], 0.3),
            '& .MuiLinearProgress-bar': {
              background: `linear-gradient(45deg, ${theme.palette.primary.main} 30%, ${theme.palette.secondary.main} 90%)`,
              borderRadius: 4
            }
          }} 
        />
        
        {riskScore > 0 && (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', mt: 2 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mr: 2 }}>
              Current Risk Score:
            </Typography>
            <Chip 
              label={`${riskScore.toFixed(1)} - ${riskCategory}`}
              sx={{ 
                backgroundColor: getRiskColor(riskCategory),
                color: 'white'
              }}
            />
          </Box>
        )}
      </Paper>

      {/* Question Card */}
      <Slide direction="left" in={true} timeout={500} key={currentStep}>
        <Card sx={{ mb: 3 }}>
          <CardContent sx={{ p: 4 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <Box 
                sx={{ 
                  p: 2, 
                  borderRadius: '50%', 
                  backgroundColor: alpha(theme.palette.primary.main, 0.1),
                  color: theme.palette.primary.main,
                  mr: 2
                }}
              >
                {currentQuestion.icon}
              </Box>
              <Box>
                <Typography variant="h5" gutterBottom>
                  {currentQuestion.title}
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  {currentQuestion.question}
                </Typography>
              </Box>
            </Box>

            <RadioGroup
              value={answers[currentQuestion.id] || ''}
              onChange={(e) => handleAnswer(currentQuestion.id, e.target.value)}
            >
              {currentQuestion.options.map((option, index) => (
                <FormControlLabel
                  key={index}
                  value={option.value}
                  control={<Radio />}
                  label={
                    <Box sx={{ py: 1 }}>
                      <Typography variant="body1">
                        {option.label}
                      </Typography>
                    </Box>
                  }
                  sx={{
                    mb: 1,
                    p: 2,
                    border: answers[currentQuestion.id] === option.value ? 
                      `2px solid ${theme.palette.primary.main}` : 
                      `1px solid ${alpha(theme.palette.grey[400], 0.5)}`,
                    borderRadius: 2,
                    backgroundColor: answers[currentQuestion.id] === option.value ? 
                      alpha(theme.palette.primary.main, 0.05) : 
                      'transparent',
                    transition: 'all 0.3s ease'
                  }}
                />
              ))}
            </RadioGroup>
          </CardContent>
        </Card>
      </Slide>

      {/* Navigation */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 4 }}>
        <Button
          variant="outlined"
          onClick={handleBack}
          disabled={currentStep === 0}
        >
          Previous
        </Button>
        
        <Button
          variant="contained"
          onClick={handleNext}
          disabled={!answers[currentQuestion.id] || loading}
          sx={{
            background: `linear-gradient(45deg, ${theme.palette.primary.main} 30%, ${theme.palette.secondary.main} 90%)`,
          }}
        >
          {loading ? 'Submitting...' : (currentStep === riskQuestions.length - 1 ? 'Complete Assessment' : 'Next')}
        </Button>
      </Box>
    </Box>
  );
}

export default PersonalizedRiskProfile;