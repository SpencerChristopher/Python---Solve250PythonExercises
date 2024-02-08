import os
import json
import argparse

import os
import json
import argparse

def fetch_resource_files(extraction_path, channel):
    """
    Fetches a list of resource files in the extraction directory based on the specified channel.

    Parameters:
    - extraction_path (str): Path to the extraction directory.
    - channel (str): The channel or channels to access.

    Returns:
    - list: List of resource files.
    """
    try:
        resource_files = []

        if not channel or channel.lower() == 'global':
            # Include global resources folder
            resource_files += [os.path.join(root, file) for root, dirs, files in os.walk(os.path.join(extraction_path, 'resources')) for file in files if file.endswith(".json")]

        if channel:
            # Include channel-specific resources folders based on the provided channels
            channels = [c.strip().upper() for c in channel.split(',')]
            for ch in channels:
                if ch == 'DE':
                    # For 'DE' without a specific channel folder, include 'resources' folder
                    resource_files += [os.path.join(root, file) for root, dirs, files in os.walk(os.path.join(extraction_path, 'resources')) for file in files if file.endswith(".json")]
                else:
                    # Include channel-specific resources folders based on the provided channels
                    channel_folder = os.path.join(extraction_path, f"resources_{ch}")
                    resource_files += [os.path.join(root, file) for root, dirs, files in os.walk(channel_folder) for file in files if file.endswith(".json")]

        return resource_files
    except Exception as e:
        print(f"Error fetching resource files: {e}")
        return []

def extract_target_fields_in_channel(file_path):
    """
    Extracts target fields and associated source fields from a JSON file.

    Parameters:
    - file_path (str): Path to the JSON file.

    Returns:
    - tuple: Tuple containing target field and source fields.
    """
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            target_field = data.get('target_field', '')
            source_fields = data.get('source_field', [])
            return target_field, source_fields
    except Exception as e:
        print(f"Error extracting target fields from {file_path}: {e}")
        return None, None

def get_channel_files(extraction_path, channel):
    """
    Returns a list of resource files based on the specified channel or channels.

    Parameters:
    - extraction_path (str): Path to the extraction directory.
    - channel (str): The channel or channels to access.

    Returns:
    - list: List of resource files.
    """
    return fetch_resource_files(extraction_path, channel)

def main():
    """
    Main function for extracting and auditing target fields in an extraction directory.
    """
    parser = argparse.ArgumentParser(description="Script for extracting and auditing target fields in an extraction directory.")
    parser.add_argument("--find", type=str, help="Find a target field in the extraction directory. Example: --find prod_feat1234")
    parser.add_argument("--audit", action="store_true", help="Create a file with all target fields and their associated files and source fields.")
    parser.add_argument("--channel", type=str, help="Specify the channel or channels to access. Multiple channels should be comma-separated. Example: --channel DE,ES")
    args = parser.parse_args()

    extraction_path = '.'  # Set to the current working directory

    target_field = args.find
    channel = args.channel or 'global'

    resource_files = get_channel_files(extraction_path, channel)

    if not resource_files:
        print(f"No resource files found for channel: {channel}")
        return

    result = {}
    for file_path in resource_files:
        current_target, source_fields = extract_target_fields_in_channel(file_path)
        if current_target == target_field:
            result[file_path] = result.get(file_path, []) + source_fields

    if result:
        print(json.dumps({target_field: result}, indent=4))
    else:
        print(f"No matching files found for target field: {target_field}")

if __name__ == '__main__':
    main()
