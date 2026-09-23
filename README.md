# Aircraft Maintenance Analytics System

A comprehensive web-based system for tracking, analyzing, and predicting aircraft maintenance requirements. This system helps aviation maintenance teams manage aircraft fleets, schedule maintenance tasks, monitor component health, and predict potential failures using analytics.

## Features

- **Fleet Management**: Track all aircraft in your fleet with detailed information
- **Component Tracking**: Monitor individual components with usage metrics and limits
- **Maintenance Scheduling**: Schedule, track, and complete maintenance tasks
- **Alert System**: Real-time alerts for critical issues and upcoming maintenance
- **Predictive Analytics**: ML-based failure predictions and remaining useful life calculations
- **Dashboard**: Real-time overview of fleet status and maintenance metrics
- **Role-based Access**: Admin, technician, and viewer roles with appropriate permissions
- **REST API**: Full API support for integration with other systems

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │   Web UI    │  │  Dashboard   │  │   Charts    │  │  Forms &    │   │
│  │  (Jinja2)   │  │   Widgets   │  │  (Plotly)   │  │  Tables     │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          APPLICATION LAYER                              │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      Flask Application                           │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐ │   │
│  │  │   Routes   │  │   Models   │  │  Services  │  │   Utils    │ │   │
│  │  │  - auth    │  │  - User    │  │  - Analytics│ │  - Auth    │ │   │
│  │  │  - aircraft│  │  - Aircraft│  │  - Predictions│ │ - DB Utils│ │   │
│  │  │  - components│ │  - Component│ │            │  │            │ │   │
│  │  │  - maintenance│ │ - Maintenance│ │           │  │            │ │   │
│  │  │  - alerts   │  │  - Alert   │  │            │  │            │ │   │
│  │  │  - predictions│ │ - Prediction│ │           │  │            │ │   │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           DATA LAYER                                     │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    SQLite Database                               │   │
│  │  ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ ┌─────────┐ │   │
│  │  │  Users  │ │ Aircraft │ │Components│ │Records │ │ Alerts  │ │   │
│  │  └─────────┘ └──────────┘ └──────────┘ └────────┘ └─────────┘ │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐    │   │
│  │  │Predictions │ │ FlightData  │ │  Sample Data Generator  │    │   │
│  │  └─────────────┘ └─────────────┘ └─────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

## Technology Stack

- **Backend**: Flask 3.0.0
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: Flask-Login with Werkzeug password hashing
- **Frontend**: Bootstrap 5.3, Font Awesome 6.4, Jinja2 templates
- **Data Processing**: Pandas, NumPy
- **Machine Learning**: Scikit-learn (for prediction models)
- **Visualization**: Plotly.js (via CDN)
- **WSGI Server**: Gunicorn (production)

## Directory Structure

```
AIRCRAFT MAINTENANCE ANALYTICS SYSTEM/
├── main.py                      # Application entry point
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Configuration classes
│   ├── app_config.py            # App configuration
│   ├── models.py                # Database models
│   ├── requirements.txt         # Python dependencies
│   ├── aircraft_maintenance.db # SQLite database
│   ├── run.py                   # Alternative entry point
│   ├── Dockerfile               # Docker configuration
│   ├── README.md                # App README
│   │
│   ├── routes/                  # URL routes and controllers
│   │   ├── __init__.py
│   │   ├── auth.py             # Authentication routes
│   │   ├── aircraft.py         # Aircraft management routes
│   │   ├── components.py       # Component tracking routes
│   │   ├── maintenance.py      # Maintenance scheduling routes
│   │   ├── alerts.py           # Alert management routes
│   │   └── predictions.py      # Predictive analytics routes
│   │
│   ├── services/                # Business logic layer
│   │   ├── __init__.py
│   │   ├── analytics.py        # Analytics and reporting
│   │   ├── prediction_engine.py # ML prediction models
│   │   └── sample_data.py      # Sample data generator
│   │
│   ├── utils/                   # Utility functions
│   │   ├── __init__.py
│   │   ├── auth_utils.py       # Authentication decorators
│   │   └── db_utils.py         # Database utilities
│   │
│   └── superset/                # Superset integration (optional)
│
├── templates/                    # Jinja2 HTML templates
│   ├── base.html                # Base template
│   ├── index.html               # Dashboard
│   ├── auth/                    # Authentication templates
│   │   ├── login.html
│   │   ├── register.html
│   │   └── profile.html
│   ├── aircraft/               # Aircraft templates
│   │   ├── list.html
│   │   ├── detail.html
│   │   ├── add.html
│   │   └── edit.html
│   ├── components/              # Component templates
│   │   ├── list.html
│   │   ├── detail.html
│   │   ├── add.html
│   │   └── edit.html
│   ├── maintenance/             # Maintenance templates
│   │   ├── list.html
│   │   ├── detail.html
│   │   ├── add.html
│   │   ├── edit.html
│   │   └── calendar.html
│   ├── alerts/                  # Alert templates
│   │   ├── list.html
│   │   ├── detail.html
│   │   └── add.html
│   └── predictions/             # Prediction templates
│       ├── list.html
│       └── aircraft.html
│
├── static/                      # Static files (if needed)
└── data/                        # Sample datasets (to be created)
    ├── aircraft.csv
    ├── components.csv
    ├── maintenance_records.csv
    └── flight_data.csv
```

## Database Models

### User
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email address
- `password_hash`: Hashed password
- `role`: User role (admin, technician)
- `created_at`: Account creation timestamp

### Aircraft
- `id`: Primary key
- `registration_number`: Unique tail number
- `aircraft_type`: Type code (B737, A320, etc.)
- `model`: Specific model
- `manufacturer`: Boeing, Airbus, etc.
- `year_manufactured`: Manufacturing year
- `total_flight_hours`: Accumulated flight hours
- `total_cycles`: Accumulated flight cycles
- `status`: active, maintenance, parked, retired

### Component
- `id`: Primary key
- `aircraft_id`: Foreign key to Aircraft
- `part_number`: Manufacturer part number
- `serial_number`: Unique serial number
- `component_type`: Engine, Landing Gear, etc.
- `description`: Component description
- `installation_date`: When component was installed
- `current_hours`: Hours used since installation
- `current_cycles`: Cycles since installation
- `max_hours`: Maximum allowable hours
- `max_cycles`: Maximum allowable cycles
- `status`: serviceable, limited, unserviceable

### MaintenanceRecord
- `id`: Primary key
- `aircraft_id`: Foreign key to Aircraft
- `component_id`: Optional foreign key to Component
- `maintenance_type`: inspection, repair, replacement, etc.
- `description`: Task description
- `work_order_number`: Work order reference
- `performed_by`: Technician name
- `scheduled_date`: Planned date
- `completed_date`: Actual completion date
- `labor_hours`: Hours worked
- `parts_cost`: Parts cost
- `labor_cost`: Labor cost
- `total_cost`: Total cost
- `status`: scheduled, in_progress, completed, cancelled
- `priority`: low, medium, high, critical

### Alert
- `id`: Primary key
- `aircraft_id`: Foreign key to Aircraft
- `component_id`: Optional foreign key to Component
- `alert_type`: Type of alert
- `title`: Alert title
- `message`: Alert message
- `severity`: low, medium, high, critical
- `is_active`: Active status
- `acknowledged`: Acknowledged status
- `acknowledged_by`: Who acknowledged
- `acknowledged_at`: When acknowledged
- `due_date`: Due date

### Prediction
- `id`: Primary key
- `aircraft_id`: Foreign key to Aircraft
- `component_id`: Foreign key to Component
- `prediction_type`: Type of prediction
- `model_version`: Model version used
- `current_value`: Current health value
- `predicted_value`: Predicted failure probability
- `confidence_score`: Model confidence
- `estimated_remaining_hours`: Estimated hours until failure
- `created_at`: Prediction timestamp

### FlightData
- `id`: Primary key
- `aircraft_id`: Foreign key to Aircraft
- `flight_date`: Date of flight
- `flight_number`: Flight number
- `origin`: Departure airport
- `destination`: Arrival airport
- `flight_hours`: Duration in hours
- `flight_cycles`: Number of cycles
- `takeoffs`: Number of takeoffs
- `landings`: Number of landings
- `fuel_burned`: Fuel consumed

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Step 1: Clone or Download the Project

```bash
git clone <repository-url>
cd "AIRCRAFT MAINTENANCE ANALYTICS SYSTEM"
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r app/requirements.txt
```

### Step 4: Run the Application

```bash
python main.py
```

The application will:
1. Create the SQLite database
2. Initialize default users (admin/tech1)
3. Generate sample data (5 aircraft, 70 components, 65 maintenance records, 22 alerts)
4. Start the Flask development server

### Step 5: Access the Application

Open your browser and navigate to:
- **URL**: http://127.0.0.1:5000
- **Admin Login**: admin / admin123
- **Technician Login**: tech1 / tech123

## Docker Deployment

### Build and Run with Docker

```bash
# Build the Docker image
cd app
docker build -t aircraft-maintenance-system .

# Run the container
docker run -p 5000:5000 aircraft-maintenance-system
```

### Docker Compose (Recommended)

Create a `docker-compose.yml` file:

```yaml
version: '3.8'
services:
  web:
    build: ./app
    ports:
      - "5000:5000"
    volumes:
      - .:/app
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=your-secure-secret-key
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

## Production Deployment

### Using Gunicorn

```bash
cd app
gunicorn -w 4 -b 0.0.0.0:5000 "main:create_app('production')" --timeout 120
```

### Using Nginx + Gunicorn

1. Install Gunicorn and configure as a systemd service
2. Set up Nginx as a reverse proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment mode | development |
| `SECRET_KEY` | Session encryption key | (auto-generated) |
| `DATABASE_URL` | Database connection string | SQLite local file |

### Configuration Modes

- **development**: Debug mode enabled, auto-reload
- **production**: Debug disabled, optimized settings
- **testing**: In-memory database for tests

## API Documentation

### Authentication Endpoints

```
POST /auth/login          - User login
POST /auth/register       - User registration
GET  /auth/logout         - User logout
GET  /auth/profile         - User profile
POST /auth/api/login       - API login
POST /auth/api/logout      - API logout
GET  /auth/api/current_user - Current user info
```

### Aircraft Endpoints

```
GET  /aircraft/              - List all aircraft
GET  /aircraft/<id>         - Aircraft details
POST /aircraft/add           - Add aircraft (admin)
PUT  /aircraft/<id>/edit     - Edit aircraft (admin)
DELETE /aircraft/<id>/delete - Delete aircraft (admin)
GET  /aircraft/api/list      - API: List aircraft
GET  /aircraft/api/<id>      - API: Aircraft details
```

### Component Endpoints

```
GET  /components/              - List components
GET  /components/<id>         - Component details
POST /components/add           - Add component (admin)
PUT  /components/<id>/edit    - Edit component (admin)
DELETE /components/<id>/delete - Delete component (admin)
GET  /components/api/list      - API: List components
GET  /components/api/<id>/health - API: Health data
```

### Maintenance Endpoints

```
GET  /maintenance/              - List maintenance records
GET  /maintenance/<id>          - Record details
POST /maintenance/add            - Add record (technician)
PUT  /maintenance/<id>/edit      - Edit record (technician)
DELETE /maintenance/<id>/delete  - Delete record (admin)
GET  /maintenance/calendar       - Maintenance calendar
GET  /maintenance/api/list       - API: List records
GET  /maintenance/api/stats      - API: Statistics
```

### Alert Endpoints

```
GET  /alerts/              - List alerts
GET  /alerts/<id>         - Alert details
POST /alerts/add           - Create alert (technician)
POST /alerts/<id>/acknowledge - Acknowledge alert
POST /alerts/<id>/resolve  - Resolve alert
DELETE /alerts/<id>/delete - Delete alert (admin)
GET  /alerts/api/list      - API: List alerts
GET  /alerts/api/stats     - API: Statistics
```

### Prediction Endpoints

```
GET  /predictions/                        - List predictions
GET  /predictions/aircraft/<id>           - Aircraft predictions
POST /predictions/generate                - Generate predictions (admin)
GET  /predictions/api/list                - API: List predictions
GET  /predictions/api/aircraft/<id>       - API: Aircraft predictions
GET  /predictions/api/high-risk           - API: High risk predictions
```

## Sample Data

The system automatically generates sample data on first run:

- **5 Aircraft**: Boeing 737 and 737 MAX, Airbus A320 and A320neo, Embraer E190-E2
- **70 Components**: Engines, landing gear, avionics, APU, hydraulics
- **65 Maintenance Records**: Mix of completed and scheduled tasks
- **22 Alerts**: Various severity levels for component limits and inspections
- **150 Flight Records**: Historical flight data for analysis

### Loading Sample Data

The sample data is automatically loaded when the database is empty. To reset:

1. Delete `app/aircraft_maintenance.db`
2. Restart the application

### Exporting/Importing Data

Use the API to export data:

```bash
# Export aircraft data
curl http://localhost:5000/aircraft/api/list > aircraft.json

# Export maintenance records
curl http://localhost:5000/maintenance/api/list > maintenance.json
```

## Predictive Analytics

The system includes ML-based predictions:

### Health Score Calculation
- Based on component usage vs. maximum limits
- Considers both hours and cycles usage
- Returns score from 0-100

### Failure Probability
- Uses historical maintenance data
- Calculates days until component reaches limits
- Considers usage rate trends

### Remaining Useful Life (RUL)
- Estimates days until component replacement needed
- Based on average flight data patterns
- Updates with each new flight record

## Security

### Password Security
- Passwords hashed using Werkzeug's secure hashing
- Each hash includes unique salt
- Never stores plain text passwords

### Session Management
- Flask-Login for session management
- 7-day session lifetime
- Secure session cookies

### Role-Based Access Control
- **Admin**: Full access to all features
- **Technician**: Can view, add, and edit records
- **Viewer**: Can only view data (if implemented)

## Troubleshooting

### Common Issues

**Database Errors**
```bash
# Delete the database and restart
rm app/aircraft_maintenance.db
python main.py
```

**Port Already in Use**
```bash
# Find and kill the process using port 5000
# Windows
netstat -ano | findstr :5000
taskkill /PID <pid> /F

# Linux/Mac
lsof -i :5000
kill -9 <pid>
```

**Module Import Errors**
```bash
# Reinstall dependencies
pip install -r app/requirements.txt --force-reinstall
```

### Debug Mode

Enable detailed error pages:
```bash
FLASK_ENV=development python main.py
```

### Logging

Check console output for:
- Database initialization
- Sample data generation
- Request logging
- Error traces

## Development

### Adding New Features

1. **Models**: Add to `app/models.py`
2. **Routes**: Create new blueprint in `app/routes/`
3. **Services**: Add business logic in `app/services/`
4. **Templates**: Create HTML in `templates/`
5. **Tests**: Add tests in appropriate test file

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-flask

# Run tests
pytest app/tests/
```

## License

This project is provided as-is for educational and commercial use.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Check Flask and SQLAlchemy documentation
4. Open an issue in the repository

## Credits

Built with:
- Flask Framework
- SQLAlchemy ORM
- Bootstrap 5
- Font Awesome
- Plotly.js
- Scikit-learn

---

**Version**: 1.0.0  
**Last Updated**: April 2026

## Troubleshooting

### Common Template Errors

If you encounter `UndefinedError: 'X object' has no attribute 'id'` errors:

- **Aircraft**: Use `aircraft_id` instead of `id`
- **Component**: Use `component_id` instead of `id`
- **MaintenanceRecord**: Use `record_id` instead of `id`
- **Alert**: Use `alert_id` instead of `id`
- **FailurePrediction**: Use `failure_probability`, `risk_level`, `confidence_score` (these are dictionary keys returned by PredictionEngine, not model attributes)

### Quick Fix for Database Reset

If you need to reset all data:

```bash
# Delete the database file
del app\aircraft_maintenance.db

# Restart the application
python main.py
```

### Running in Development

```bash
# Activate virtual environment (Windows)
venv\Scripts\activate

# Run the application
python main.py
```

The application will:
1. Create the SQLite database
2. Initialize default users (admin/tech1)
3. Generate sample data
4. Start on http://127.0.0.1:5000
