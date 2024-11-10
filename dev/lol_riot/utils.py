import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_env_variable(name: str) -> str:
    """Retrieve environment variable value by name."""
    value = os.getenv(name)
    if value is None:
        raise ValueError(f"Environment variable '{name}' not found")
    return value

def log_error(error_message: str):
    """Log error messages to a file or standard error output."""
    # This is a placeholder for a more sophisticated error logging mechanism
    # For now, we'll just print the errors
    print(f"ERROR: {error_message}")

def log_info(info_message: str):
    """Log informational messages to a file or standard output."""
    # This is a placeholder for a more sophisticated info logging mechanism
    # For now, we'll just print the info messages
    print(f"INFO: {info_message}")

def format_summoner_data(summoner_data: dict) -> dict:
    """Format summoner data for database insertion or API response."""
    # Assuming summoner_data is a dictionary returned from RiotAPIWrapper
    # This function can be expanded based on specific formatting needs
    formatted_data = {
        "summoner_name": summoner_data.get("name"),
        "region": summoner_data.get("region"),
        "profile_icon_id": summoner_data.get("profileIconId"),
        "summoner_level": summoner_data.get("summonerLevel"),
    }
    return formatted_data

def format_champion_mastery_data(mastery_data: dict) -> dict:
    """Format champion mastery data for database insertion or API response."""
    # Assuming mastery_data is a dictionary returned from RiotAPIWrapper
    # This function can be expanded based on specific formatting needs
    formatted_data = {
        "summoner_id": mastery_data.get("summonerId"),
        "champion_id": mastery_data.get("championId"),
        "mastery_level": mastery_data.get("championLevel"),
        "mastery_points": mastery_data.get("championPoints"),
    }
    return formatted_data

# Additional utility functions can be added here as needed for the project
