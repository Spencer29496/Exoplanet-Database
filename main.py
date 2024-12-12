from database_setup import create_database
from data_import import import_data

if __name__ == "__main__":
    create_database()
    import_data('exoplanet_data.csv')