

def normalize_to_kg(value, unit):
    if unit == 'g':
        return float(value) / 1000
    elif unit == 'kg':
        return float(value)
    elif unit == 'l':
        # Assume 1 liter of water is approximately 1 kg
        return float(value)
    else:
        return None  # Handle other units as needed

def process_sample_list(sample_list):
    unit_counts = defaultdict(int)
    kg_counts = defaultdict(float)

    for i in range(0, len(sample_list), 2):
        value, count = sample_list[i], sample_list[i + 1]

        if value:
            unit = value.split()[1].lower()
            unit_counts[unit] += count

            # Normalize to kg without considering count
            normalized_value = normalize_to_kg(*value.split())
            if normalized_value is not None:
                kg_counts[unit] += normalized_value

    return unit_counts, kg_counts

def print_results(unit_counts, kg_counts):
    print("Total counts for each unit:")
    for unit, count in unit_counts.items():
        print(f'Total count of {unit}: {count}')

    print("\nTotal kg counts for each unit (normalized):")
    for unit, kg_count in kg_counts.items():
        print(f'Total kg count of {unit}: {kg_count:.3f} kg')

# Example usage