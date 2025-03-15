# Exoplanet Database

## Project Overview
The Exoplanet Database is an interactive web application that provides a comprehensive, visually rich exploration platform for exoplanets discovered throughout our galaxy. It aggregates data from NASA's Exoplanet Archive and enhances it with descriptions and imagery from Wikipedia, creating an engaging educational tool for astronomy enthusiasts and researchers.

## Key Features
- **Data Integration**: Automatically pulls the latest exoplanet data from NASA's official Exoplanet Archive
- **Rich Media Content**: Dynamically fetches images and descriptions for exoplanets from Wikipedia
- **Interactive Exploration**: Browse through hundreds of exoplanets with an intuitive, paginated interface
- **Detailed Information**: View comprehensive scientific data about each exoplanet's physical properties, discovery method, and host star
- **Search Functionality**: Easily find specific exoplanets by name or host star
- **Responsive Design**: Clean, modern UI that works across desktop and mobile devices

## Technical Implementation
- **Frontend**: HTML5, CSS3 with Bootstrap 4 for responsive design
- **Backend**: Python Flask web framework
- **Data Processing**: Pandas for efficient data manipulation
- **Database**: SQLite for local data storage
- **APIs**: Integrates with NASA Exoplanet Archive API and Wikipedia REST API
- **Concurrency**: Implements thread pooling for efficient API requests

## Data Pipeline
1. Downloads raw CSV data from NASA's Exoplanet Archive
2. Processes and cleans the data for consistency
3. Enriches entries with Wikipedia descriptions and imagery
4. Stores processed data in a SQLite database
5. Serves data through a Flask web application

## Potential Impact
This project demonstrates the power of integrating disparate data sources to create a unified, educational resource. It makes complex astronomical data accessible to the public while showcasing technical skills in:

- Full-stack web development
- Data integration and processing
- API design and consumption
- Concurrent programming
- User experience design

The Exoplanet Database could be extended to serve as a valuable educational tool for schools, museums, or astronomy enthusiasts, bridging the gap between complex scientific data and public understanding.

## Future Enhancements
- Implementation of interactive visualizations (orbital patterns, size comparisons)
- Integration with additional data sources (e.g., ESA exoplanet catalogs)
- Advanced filtering options (by planetary system, physical characteristics)
- User accounts for saving favorite exoplanets or custom lists
- API endpoints for other developers to access the enriched dataset

## Running the Application
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the data download script: `python src/download_data.py`
4. Set up the database: `python src/database_setup.py`
5. Import the data: `python src/data_import.py`
6. Start the application: `python src/app.py`
7. Access the application at http://127.0.0.1:5000/