# Hospital Management System

A comprehensive web-based hospital management system built with React, TypeScript, and Flask.

## Features

- Multi-role authentication (Admin, Doctor, Patient)
- Appointment scheduling and management
- Medical records management
- Department administration
- User profile management
- Real-time updates
- Responsive design

## Tech Stack

### Frontend
- React 18
- TypeScript
- Material-UI
- React Router
- Axios
- Date-fns

### Backend
- Flask
- SQLAlchemy
- PostgreSQL
- JWT Authentication
- RESTful API

## Getting Started

### Prerequisites
- Node.js (v14+)
- Python (v3.8+)
- PostgreSQL

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/hospital-management-system.git
cd hospital-management-system
```

2. Backend Setup:
```bash
cd Phase-2
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python database_setup.py
python create_dummy_data.py
python app.py
```

3. Frontend Setup:
```bash
cd ../Phase-3/hospital-ui
npm install
npm start
```

4. Create a .env file in the frontend directory:
```
REACT_APP_API_URL=http://localhost:5000/api
```

## Project Structure

```
hospital-management-system/
├── Phase-1/                 # Documentation & Planning
├── Phase-2/                 # Backend
│   ├── resources/          # API Resources
│   ├── models.py           # Database Models
│   └── app.py             # Main Application
└── Phase-3/                # Frontend
    └── hospital-ui/
        ├── src/
        │   ├── components/ # Reusable Components
        │   ├── pages/      # Page Components
        │   ├── contexts/   # React Contexts
        │   ├── services/   # API Services
        │   └── types/      # TypeScript Types
        └── public/         # Static Assets
```

## API Documentation

### Authentication
- POST /api/auth/login
- POST /api/auth/register
- GET /api/auth/profile

### Users
- GET /api/users
- POST /api/users
- PUT /api/users/:id
- DELETE /api/users/:id

### Departments
- GET /api/departments
- POST /api/departments
- PUT /api/departments/:id
- DELETE /api/departments/:id

### Appointments
- GET /api/appointments
- POST /api/appointments
- PUT /api/appointments/:id
- DELETE /api/appointments/:id

### Medical Records
- GET /api/medical-records
- POST /api/medical-records
- PUT /api/medical-records/:id
- DELETE /api/medical-records/:id

## Environment Variables

### Backend
```
FLASK_APP=app.py
FLASK_ENV=development
DATABASE_URL=postgresql://username:password@localhost:5432/hospital_db
JWT_SECRET_KEY=your-secret-key
```

### Frontend
```
REACT_APP_API_URL=http://localhost:5000/api
```

## Deployment

### Backend Deployment (Example using Heroku)
1. Create a Heroku account
2. Install Heroku CLI
3. Login to Heroku
4. Create a new app
5. Push to Heroku

```bash
heroku login
heroku create your-app-name
git push heroku main
```

### Frontend Deployment (Example using Netlify)
1. Create a Netlify account
2. Connect your GitHub repository
3. Configure build settings:
   - Build command: `npm run build`
   - Publish directory: `build`
4. Deploy

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

