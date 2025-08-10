# AuraVest - Advanced Portfolio Analytics Platform

## Project Overview
AuraVest is a comprehensive financial portfolio management and analytics platform that allows users to:
- Add positions from any date since 2000
- Visualize current returns and performance
- Analyze risk metrics and correlations
- Run Monte Carlo simulations
- View future projections and scenarios

## Architecture
- **Backend**: FastAPI (Python) with JWT authentication
- **Frontend**: React with Material-UI and Chart.js
- **Data**: Yahoo Finance API for market data
- **Analytics**: Advanced risk models and quantitative analysis

## Security Guidelines

### Authentication & Authorization
- Always validate JWT tokens on protected endpoints
- Never expose sensitive user data without proper authentication
- Use secure password hashing (currently demo mode with simple passwords)
- Implement proper session management

### Data Security
- Never log sensitive information (passwords, tokens, personal data)
- Validate all input data before processing
- Sanitize outputs to prevent XSS attacks
- Use parameterized queries for database operations (when implemented)

### API Security
- Always validate request data types and ranges
- Implement rate limiting for API endpoints
- Use HTTPS in production
- Never expose internal system details in error messages
- Sanitize all user inputs and file paths

### Financial Data Security
- Never store actual financial credentials
- Use read-only APIs for market data
- Implement proper audit logging for financial transactions
- Ensure data privacy compliance (GDPR, etc.)

### Code Security
- Never commit secrets, API keys, or passwords to version control
- Use environment variables for sensitive configuration
- Implement proper error handling without exposing system internals
- Regularly update dependencies to patch security vulnerabilities

## Development Guidelines

### Running the Application
```bash
# Backend
python main.py

# Frontend
cd frontend && npm start
```

### Environment Setup
- Python 3.10+ required
- Node.js 16+ for frontend
- Install dependencies: `pip install -r requirements.txt`
- Install frontend deps: `cd frontend && npm install`

### Demo Authentication
- Demo User: demo@auravest.com / demo123
- Admin User: admin@auravest.com / admin123

### API Endpoints
- `/auth/login` - User authentication
- `/auth/register` - User registration
- `/portfolios` - List user portfolios
- `/portfolio/{id}` - Portfolio details with analytics
- `/portfolio/{id}/holdings` - Add holdings to portfolio
- `/market/historical/{ticker}?date=YYYY-MM-DD` - Historical prices
- `/analysis/risk/*` - Risk analysis endpoints

### Frontend Routes
- `/dashboard` - Main dashboard
- `/portfolio/{id}` - Standard portfolio view
- `/portfolio/{id}/robinhood` - Robinhood-style view
- `/portfolio/{id}/analytics` - Advanced analytics dashboard
- `/portfolio/{id}/add-holding` - Add new positions

### Key Features
1. **Historical Position Entry**: Add positions from any date since 2000
2. **Real-time Analytics**: Current portfolio values and performance
3. **Risk Analysis**: Comprehensive risk metrics and visualizations
4. **Multiple Views**: Standard, Robinhood-style, and advanced analytics
5. **Future Projections**: Monte Carlo simulations and scenario analysis

### Security Rules for AI Development

1. **Never Create Malicious Code**
   - Do not create code that could be used for hacking, data theft, or system compromise
   - Refuse requests to create backdoors, keyloggers, or malicious scripts
   - Always prioritize defensive security measures

2. **Data Protection**
   - Never create code that exposes sensitive user data
   - Implement proper input validation and sanitization
   - Use secure authentication and authorization patterns

3. **Financial Security**
   - Never create fake financial data for deception
   - Implement proper audit trails for financial operations
   - Ensure all financial calculations are accurate and transparent

4. **Code Quality**
   - Follow secure coding practices
   - Implement proper error handling
   - Use parameterized queries and prepared statements
   - Validate all inputs and outputs

5. **Privacy Compliance**
   - Respect user privacy and data protection laws
   - Implement proper data retention policies
   - Provide clear privacy disclosures

## Testing
- Backend: `python -m pytest tests/` (when implemented)
- Frontend: `cd frontend && npm test`
- Integration: `python integration_test.py`

## Deployment
- Use environment variables for production configuration
- Enable HTTPS and proper SSL certificates
- Configure proper CORS policies
- Set up proper logging and monitoring
- Use secure database connections (when implemented)

## Contributing
- Follow security guidelines above
- Test all changes thoroughly
- Document new features and APIs
- Use proper git commit messages
- Never commit sensitive information

## License
This is a personal portfolio project for educational and demonstration purposes.