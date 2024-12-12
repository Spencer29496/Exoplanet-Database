from database_setup import create_database
from data_import import import_data
from download_data import download_nasa
from queries import get_all_exoplanets

if __name__ == "__main__":
    create_database()
    download_nasa()
    import_data()

    print("Displaying all exoplanets:")
    get_all_exoplanets()