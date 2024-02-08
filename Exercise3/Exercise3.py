import os
import json
import argparse

def fetch_resource_files(extraction_path, channel):
    """
    Fetches a list of resource files in the extraction directory.

    Parameters:
    - extraction_path (str): Path to the extraction directory.
    - channel (str): Channel prefix.

    Returns:
    - list: List of resource files.
    """
    try:
        resource_files = []
        for root, dirs, files in os.walk(extraction_path):
            for file in files:
                if file.endswith(".json") and f"resources_{channel.upper()}" in root:
                    resource_files.append(os.path.join(root, file))
        return resource_files
    except Exception as e:
        print(f"Error fetching resource files: {e}")
        return []

def extract_target_fields(file_path):
    """
    Extracts target fields and associated source fields from a JSON file.

    Parameters:
    - file_path (str): Path to the JSON file.

    Returns:
    - tuple: Target field and list of source fields.
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
    Fetches a list of resource files in the extraction directory based on the specified channel.

    Parameters:
    - extraction_path (str): Path to the extraction directory.
    - channel (str): Channel prefix.

    Returns:
    - list: List of resource files.
    """
    return fetch_resource_files(extraction_path, channel)

def generate_json_object(title, source_fields, target_field, file_name):
    """
    Generates a JSON object based on the specified parameters.

    Parameters:
    - title (str): Title for the JSON object.
    - source_fields (list): List of source fields.
    - target_field (str): Target field.
    - file_name (str): Name of the extraction.json file.

    Returns:
    - dict: JSON object with the specified format.
    """
    json_object = {
        "title": title,
        "source_fields": source_fields,
        "target_field": target_field,
        "file_name": file_name,
    }
    return {target_field: {title: json_object}}

def find_target_field(extraction_path, target_field, channel, output_to_terminal=True):
    """
    Finds the associated files and source fields for a given target field in the extraction directory.

    Parameters:
    - extraction_path (str): Path to the extraction directory.
    - target_field (str): Target field to search for.
    - channel (str): Channel prefix.
    - output_to_terminal (bool): Whether to print the result to the terminal.

    Returns:
    - dict: Mapping of target field with associated files and source fields.
    """
    result = {}
    resource_files = get_channel_files(extraction_path, channel)

    if not resource_files:
        print(f"No resource files found for channel: {channel}")
        return result

    for file_path in resource_files:
        current_target, source_fields = extract_target_fields(file_path)
        if current_target == target_field:
            title = os.path.splitext(os.path.basename(file_path))[0]
            result.update(generate_json_object(title, source_fields, target_field, file_path))

    if output_to_terminal:
        if result:
            print(json.dumps(result, indent=4))
        else:
            print(f"No matching files found for target field: {target_field}")
    else:
        return result

def audit_target_fields(extraction_path, channel, output_to_terminal=True):
    """
    Creates a file with all target fields and their associated files and source fields in the extraction directory.

    Parameters:
    - extraction_path (str): Path to the extraction directory.
    - channel (str): Channel prefix.
    - output_to_terminal (bool): Whether to print the result to the terminal.
    """
    result = {}
    resource_files = get_channel_files(extraction_path, channel)

    if not resource_files:
        print(f"No resource files found for channel: {channel}")
        return

    for file_path in resource_files:
        current_target, source_fields = extract_target_fields(file_path)
        if current_target:
            title = os.path.splitext(os.path.basename(file_path))[0]
            result.update(generate_json_object(title, source_fields, current_target, file_path))

    if output_to_terminal:
        if result:
            print(json.dumps(result, indent=4))
        else:
            print("No matching files found.")
    else:
        with open('target_fields_mapping.json', 'w') as output_json:
            json.dump(result, output_json, indent=4)
        print("Audit completed. Check 'target_fields_mapping.json' for the results.")

def main():
    """
    Main function to parse command line arguments and execute the specified operation.
    """
    parser = argparse.ArgumentParser(description="Script for extracting and auditing target fields in an extraction directory.")
    parser.add_argument("--find", type=str, help="Find a target field in the extraction directory. Example: --find prod_feat1234")
    parser.add_argument("--audit", action="store_true", help="Create a file with all target fields and their associated files and source fields.")
    parser.add_argument("--channel", type=str, help="Specify the channel or channels to access. Multiple channels should be comma-separated. Example: --channel DE,ES")
    parser.add_argument("--output", choices=["terminal", "file"], default="terminal", help="Specify whether to output to terminal or file. Default: terminal")
    args = parser.parse_args()

    extraction_path = '.'  # Set to the current working directory

    target_field = args.find
    channel = args.channel or 'global'
    output_to_terminal = args.output.lower() == "terminal"

    if args.find:
        find_target_field(extraction_path, target_field, channel, output_to_terminal)

    elif args.audit:
        audit_target_fields(extraction_path, channel, output_to_terminal)

if __name__ == '__main__':
    main()
