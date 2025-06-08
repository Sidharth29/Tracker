# Project Name: Tracker

## Overview

**Tracker** is a project designed to streamline and automate an ELT pipeline to fetch personal health and content consumption data from APIs, stage them in a central db (POSTGRES) and perform necessary transformations to extract stats/trends to display on a simple dashboardss efficiently.


## Tools and Their Purpose

- **Python**: Core programming language used for backend logic and data processing.
- **Flask/Django**: Framework for building the web application and API endpoints.
- **SQLite/PostgreSQL**: Database for storing and managing data.
- **HTML/CSS/JavaScript**: Frontend technologies for creating a responsive user interface.
- **Docker**: Containerization tool to ensure consistent development and deployment environments.
- **Git**: Version control system for tracking changes and collaboration.

## File Structure

```
Tracker/
├── README.md          # Project documentation
├── app/
│   ├── __init__.py    # Application initialization
│   ├── routes.py      # API routes and endpoints
│   ├── models.py      # Database models
│   ├── templates/     # HTML templates for the frontend
│   └── static/        # Static files (CSS, JS, images)
├── config/
│   ├── config.py      # Configuration settings
├── tests/
│   ├── test_app.py    # Unit tests for the application
├── requirements.txt   # Python dependencies
├── Dockerfile         # Docker configuration
└── .gitignore         # Files and directories to ignore in Git
```

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/tracker.git
   cd tracker
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Access the application at `http://localhost:5000`.

## Todo

Things to fix:
- Make fitbit module to a class
- Explore Fitbit Endpoints and pick any other ones to use
- Remove dependence on csvs as an interim, use Xcom instead or other ephemeral option
- Backup to S3 periodically
- Pydantic for API response 
- Runs fetch picks up a range not a specific date


Ideas for data processing
- Find resting heartrate
- Duration watch worn
- Time spent in each zone

#### Visualize Pipeline

Visualize the daily pipeline, the process flow and the end result



#### Auto Initialize Database

- In the docker build process, include a step to
    - Create the schema and tables
    - Populate them with data from S3
- CHeck if it's the very first run (if the database tables exist)

-Create the main schemas (heartrate,runs and heartrate_silver) and tables (heartrate_data and all_runs) during docker build

#### Archival DAG
- Option to backup data on S3 
- S3: Lifecycle policy to move data older than X months to Cheapest form of Glacier - Deep Archive



### Versions

V1:
- Dockerized postgres + airflow
- Single DAG which pulls heartrate data and sticks it into POSTGRES table

V2:
- Separate fitbit module that contains code to pull in heartrate data
    Talk about benefits of using try and except statements to control error prompting
- Another method to pull data for runs

V3:
- Another schema called heartrate_silver to integrate data from two tables using dbt
- Add SQL steps to perform the processing steps

Vx:
- Add sensor to check for internet connection
- Off load API data validation and the data type conversion to Pydantic

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description of your changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact

For questions or feedback, please reach out to [sidharthchandrasekar@gmail.com].


