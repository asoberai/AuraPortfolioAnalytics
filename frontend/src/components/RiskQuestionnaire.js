import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Alert,
  Stepper,
  Step,
  StepLabel
} from '@mui/material';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const questions = [
  {
    id: 'investment_goals',
    label: 'What are your primary investment goals?',
    type: 'select',
    options: [
      'Capital preservation',
      'Income generation',
      'Balanced growth and income',
      'Long-term growth',
      'Aggressive growth'
    ]
  },
  {
    id: 'time_horizon',
    label: 'What is your investment time horizon (in years)?',
    type: 'number',
    min: 1,
    max: 50
  },
  {
    id: 'risk_comfort',
    label: 'How comfortable are you with investment risk?',
    type: 'select',
    options: [
      '1 - Very conservative',
      '2 - Conservative',
      '3 - Moderate',
      '4 - Aggressive',
      '5 - Very aggressive'
    ]
  },
  {
    id: 'market_experience',
    label: 'How would you describe your investment experience?',
    type: 'select',
    options: [
      'No experience',
      'Limited experience',
      'Moderate experience',
      'Experienced investor',
      'Very experienced investor'
    ]
  },
  {
    id: 'reaction_to_loss',
    label: 'If your portfolio lost 20% in a month, you would:',
    type: 'select',
    options: [
      'Sell everything immediately',
      'Sell some positions',
      'Do nothing',
      'Hold and wait for recovery',
      'Buy more at lower prices'
    ]
  },
  {
    id: 'income_stability',
    label: 'How stable is your income?',
    type: 'select',
    options: [
      'Very unstable',
      'Somewhat unstable',
      'Stable',
      'Very stable',
      'Multiple stable sources'
    ]
  },
  {
    id: 'investment_knowledge',
    label: 'How would you rate your investment knowledge?',
    type: 'select',
    options: [
      'Beginner',
      'Basic',
      'Intermediate',
      'Advanced',
      'Expert'
    ]
  }
];

function RiskQuestionnaire() {
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const { token } = useAuth();
  const navigate = useNavigate();

  const handleAnswer = (questionId, value) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: value
    }));
  };

  const handleNext = () => {
    if (currentStep < questions.length - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      submitQuestionnaire();
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const submitQuestionnaire = async () => {
    setLoading(true);
    setError('');

    try {
      // Convert answers to API format
      const payload = {
        investment_goals: answers.investment_goals,
        time_horizon: parseInt(answers.time_horizon),
        risk_comfort: parseInt(answers.risk_comfort?.charAt(0) || '3'),
        market_experience: answers.market_experience,
        reaction_to_loss: answers.reaction_to_loss,
        income_stability: answers.income_stability,
        investment_knowledge: answers.investment_knowledge
      };

      const response = await axios.post('http://localhost:8000/profile/risk-questionnaire', payload, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      setResult(response.data);
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to submit questionnaire');
    } finally {
      setLoading(false);
    }
  };

  const currentQuestion = questions[currentStep];
  const isLastStep = currentStep === questions.length - 1;
  const canProceed = answers[currentQuestion?.id] !== undefined;

  if (result) {
    return (
      <Container component="main" maxWidth="sm">
        <Box sx={{ marginTop: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <Paper elevation={3} sx={{ padding: 4, width: '100%', textAlign: 'center' }}>
            <Typography variant="h4" gutterBottom color="primary">
              Risk Assessment Complete!
            </Typography>
            
            <Box sx={{ my: 3 }}>
              <Typography variant="h5" gutterBottom>
                Your Risk Profile: {result.risk_category}
              </Typography>
              <Typography variant="body1" color="textSecondary">
                Risk Score: {result.risk_score}/1.0
              </Typography>
            </Box>

            <Alert severity="success" sx={{ mb: 3 }}>
              {result.message}
            </Alert>

            <Typography variant="body2" sx={{ mb: 3 }}>
              This profile will be used to provide personalized investment recommendations
              and portfolio suggestions tailored to your risk tolerance.
            </Typography>

            <Button
              variant="contained"
              size="large"
              onClick={() => navigate('/dashboard')}
            >
              Continue to Dashboard
            </Button>
          </Paper>
        </Box>
      </Container>
    );
  }

  return (
    <Container component="main" maxWidth="md">
      <Box sx={{ marginTop: 4, marginBottom: 4 }}>
        <Paper elevation={3} sx={{ padding: 4 }}>
          <Typography variant="h4" align="center" gutterBottom>
            Risk Assessment Questionnaire
          </Typography>
          <Typography variant="body1" align="center" color="textSecondary" sx={{ mb: 4 }}>
            Help us understand your investment preferences and risk tolerance
          </Typography>

          <Stepper activeStep={currentStep} sx={{ mb: 4 }}>
            {questions.map((_, index) => (
              <Step key={index}>
                <StepLabel />
              </Step>
            ))}
          </Stepper>

          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

          <Box sx={{ mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              Question {currentStep + 1} of {questions.length}
            </Typography>
            <Typography variant="body1" sx={{ mb: 3 }}>
              {currentQuestion.label}
            </Typography>

            {currentQuestion.type === 'select' ? (
              <FormControl fullWidth>
                <InputLabel>Select an option</InputLabel>
                <Select
                  value={answers[currentQuestion.id] || ''}
                  onChange={(e) => handleAnswer(currentQuestion.id, e.target.value)}
                  label="Select an option"
                >
                  {currentQuestion.options.map((option) => (
                    <MenuItem key={option} value={option}>
                      {option}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            ) : (
              <TextField
                fullWidth
                type="number"
                label="Years"
                value={answers[currentQuestion.id] || ''}
                onChange={(e) => handleAnswer(currentQuestion.id, e.target.value)}
                inputProps={{
                  min: currentQuestion.min,
                  max: currentQuestion.max
                }}
              />
            )}
          </Box>

          <Box display="flex" justifyContent="space-between">
            <Button
              variant="outlined"
              onClick={handleBack}
              disabled={currentStep === 0}
            >
              Back
            </Button>
            <Button
              variant="contained"
              onClick={handleNext}
              disabled={!canProceed || loading}
            >
              {loading ? 'Submitting...' : isLastStep ? 'Submit' : 'Next'}
            </Button>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
}

export default RiskQuestionnaire; 