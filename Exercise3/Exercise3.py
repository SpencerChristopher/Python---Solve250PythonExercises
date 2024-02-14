import json
import argparse
import os
import glob
from datetime import datetime

def fetch_resource_files(extraction_path, current_channel):
    """
    Fetches all extraction JSON files based on the specified channel.

    Args:
        extraction_path (str): The path to the extraction directory.
        current_channel (str): The channel for which to fetch extraction files.

    Returns:
        list: A list of paths to extraction JSON files.
    """
    try:
        extraction_files = []

        # Use glob to get all .json files from folders starting with 'resources'
        json_files_pattern = os.path.join(extraction_path, 'resources*', '*.json')
        all_json_files = glob.glob(json_files_pattern)

        # Loop through each file in all_json_files
        for file_path in all_json_files:
            try:
                # Open the JSON file and load its content
                with open(file_path, 'r') as json_file:
                    data = json.load(json_file)

                    # Check if current_channel is in the 'channel' array of the extraction JSON
                    if current_channel in data.get('channel', []):
                        extraction_files.append(file_path)
            except Exception as e:
                print(f"Error processing JSON file {file_path}: {e}")

        return extraction_files

    except Exception as e:
        print(f"Error fetching extraction files: {e}")
        return []


def extract_target_fields(file_path):
    """
    Extracts target fields, source fields, and title from an extraction JSON file.

    Args:
        file_path (str): The path to the extraction JSON file.

    Returns:
        tuple: A tuple containing target field, source fields, and title.
    """
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            target_field = data.get('target_field', '')
            source_fields = data.get('source_fields', [])
            title = data.get('title', os.path.splitext(os.path.basename(file_path))[0])
            return target_field, source_fields, title
    except Exception as e:
        print(f"Error extracting target fields from {file_path}: {e}")
        return None, None, None


def write_json_to_file(file_path, data, temp_folder=".temp"):
    try:
        # Ensure the temp folder exists
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)

        # Generate a filename with a timestamp, channel, and target field
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        channel = data[0].get('Channel', 'unknown_channel')
        target_field = data[0].get('Target Field', 'unknown_target_field')
        filename = f"output_{timestamp}_{channel}_{target_field}.json"

        # Check if the file already exists in the temp folder
        temp_file_path = os.path.join(temp_folder, filename)
        if os.path.exists(temp_file_path):
            user_input = input(f"The file '{temp_file_path}' already exists. Do you want to overwrite it? (y/n): ")
            if user_input.lower() != 'y':
                print("Operation aborted.")
                return

        # Write data to the original file_path with UTF-8 encoding and ensure ASCII is False
        with open(file_path, 'w', encoding='utf-8', errors='ignore') as output_json:
            json.dump(data, output_json, indent=4, ensure_ascii=False)

        print(f"Data written to {file_path}")

    except Exception as e:
        print(f"Error writing to file: {type(e).__name__} - {e}")



def update_result(result, title, source_fields, target_field, file_name, channels):
    """
    Updates the result dictionary with information from an extraction file.

    Args:
        result (dict): The result dictionary to update.
        title (str): The title of the extraction file.
        source_fields (list): The source fields from the extraction file.
        target_field (str): The target field from the extraction file.
        file_name (str): The name of the extraction file.
        channels (list): The channels from the extraction file.
    """
    if target_field not in result:
        result[target_field] = {
            "channels": set(),  # Use a set to avoid duplicates
            "details": {}
        }

    result[target_field]["channels"].update(channels)

    for channel in channels:
        if channel not in result[target_field]["details"]:
            result[target_field]["details"][channel] = {}

        result[target_field]["details"][channel][title] = {
            "source_fields": source_fields,
            "file_name": file_name,
        }


def find_target_field(extraction_path, target_field, channel, output_to_terminal=True):
    """
    Finds and prints or writes to a file information about a target field in the extraction directory.

    Args:
        extraction_path (str): The path to the extraction directory.
        target_field (str): The target field to search for.
        channel (str): The channel or channels to access.
        output_to_terminal (bool): Whether to output to the terminal.

    Returns:
        None
    """
    result = {}
    channels = channel.split(',')
    found_target = False

    for current_channel in channels:
        extraction_files = fetch_resource_files(extraction_path, current_channel)

        if not extraction_files:
            print(f"No extraction files found for channel: {current_channel}")
            continue

        for file_path in extraction_files:
            current_target, source_fields, title = extract_target_fields(file_path)
            if current_target == target_field:
                update_result(result, title, source_fields, target_field, file_path)
                found_target = True

    if not found_target and output_to_terminal:
        print(f"No matching files found for target field: {target_field}")
        exit()

    if output_to_terminal:
        formatted_output = format_target_field_results(result)
        for line in formatted_output:
            print(line)
    else:
        write_json_to_file(f'target_fields_mapping_{channel}.json', result)


def audit_target_fields(extraction_path, channel, output_to_terminal=True):
    """
    Audits and prints or writes to a file information about all target fields in the extraction directory.

    Args:
        extraction_path (str): The path to the extraction directory.
        channel (str): The channel or channels to access.
        output_to_terminal (bool): Whether to output to the terminal.

    Returns:
        None
    """
    result = {}
    channels = channel.split(',')
    found_target = False

    for current_channel in channels:
        extraction_files = fetch_resource_files(extraction_path, current_channel)

        if not extraction_files:
            print(f"No extraction files found for channel: {current_channel}")
            continue

        for file_path in extraction_files:
            current_target, source_fields, title = extract_target_fields(file_path)
            if current_target:
                update_result(result, title, source_fields, current_target, file_path)
                found_target = True

    if not found_target and output_to_terminal:
        print("No matching files found.")
        exit()

    if output_to_terminal:
        formatted_output = format_target_field_results(result)
        for line in formatted_output:
            print(line)
    else:
        write_json_to_file(f'target_fields_mapping_{channel}.json', result)


def format_target_field_results(result):
    """
    Formats the target field results for output.

    Args:
        result (dict): The result dictionary.

    Returns:
        list: A list of formatted output lines.
    """
    formatted_output = []

    for target_field, details in result.items():
        for channel, entries in details.get("details", {}).items():
            formatted_output.append(f"========================================")
            formatted_output.append(f"  Channel: {channel}")
            formatted_output.append(f"========================================")
            for entry in entries.values():
                formatted_output.append(f"    Title: {entry['title']}")
                formatted_output.append(f"    Source Fields: {', '.join(entry['source_fields'])}")
                formatted_output.append(f"    File Name: {entry['file_name']}")
                formatted_output.append(f"    ----------------------------------------")

    return formatted_output


def main():
    """
    Main function to handle command-line arguments.

    Returns:
        None
    """
    parser = argparse.ArgumentParser(description="Script for extracting and auditing target fields in an extraction directory.")
    parser.add_argument("--find", type=str, help="Find a target field in the extraction directory. Example: --find prod_feat1234")
    parser.add_argument("--audit", action="store_true", help="Create a file with all target fields and their associated files and source fields.")
    parser.add_argument("--channel", type=str, help="Specify the channel or channels to access. Multiple channels should be comma-separated. Example: --channel DE,ES")
    parser.add_argument("--output", choices=["terminal", "file"], default="terminal", help="Specify whether to output to terminal or file. Default: terminal")
    args = parser.parse_args()

    extraction_path = '.'  # Set to the current working directory
    target_field = args.find
    channels = args.channel.split(',') if args.channel and args.channel.lower() != 'all' else []

    if args.find:
        if not channels:
            channels = ['global']
        for current_channel in channels:
            find_target_field(extraction_path, target_field, current_channel, args.output == 'terminal')

    elif args.audit:
        if not channels:
            channels = ['global']
        for current_channel in channels:
            audit_target_fields(extraction_path, current_channel, args.output == 'terminal')


if __name__ == '__main__':
    main()
