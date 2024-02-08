import os
import json
import argparse

def fetch_resource_files(extraction_path):
    """
    Fetches a list of resource files in the extraction directory.

    Parameters:
    - extraction_path (str): Path to the extraction directory.

    Returns:
    - list: List of resource files.
    """
    try:
        resource_files = []
        for root, dirs, files in os.walk(extraction_path):
            for file in files:
                if file.endswith(".json") and "resources" in root:
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
    - dict: Mapping of target field with associated files and source fields.
    """
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            target_field = data.get('target_field', '')
            source_fields = data.get('source_field', [])
            return {target_field: source_fields}
    except Exception as e:
        print(f"Error extracting target fields from {file_path}: {e}")
        return {}

def main():
    parser = argparse.ArgumentParser(description="Script for extracting and auditing target fields in an extraction directory.")
    parser.add_argument("--find", type=str, help="Find a target field in the extraction directory.")
    parser.add_argument("--audit", action="store_true", help="Create a file with all target fields and their associated files and source fields.")
    args = parser.parse_args()

    extraction_path = '.'  # Set to the current working directory

    if args.find:
        target_field = args.find
        resource_files = fetch_resource_files(extraction_path)

        if not resource_files:
            print("No resource files found.")
            return

        result = {}
        for file_path in resource_files:
            result.update(extract_target_fields(file_path))

        if target_field in result:
            print(json.dumps({target_field: result[target_field]}, indent=4))
        else:
            print(f"No matching files found for target field: {target_field}")

    elif args.audit:
        resource_files = fetch_resource_files(extraction_path)

        if not resource_files:
            print("No resource files found.")
            return

        mapping = {}
        for file_path in resource_files:
            mapping.update(extract_target_fields(file_path))

        # Write the mapping to the output file
        with open('target_fields_mapping.json', 'w') as output_json:
            json.dump(mapping, output_json, indent=4)

        print("Audit completed. Check 'target_fields_mapping.json' for the results.")

if __name__ == '__main__':
    main()
