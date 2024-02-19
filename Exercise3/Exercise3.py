from collections import defaultdict

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
    discrete_value_counts = defaultdict(int)

    for i in range(0, len(sample_list), 2):
        value, count = sample_list[i], sample_list[i + 1]

        if value:
            unit = value.split()[1].lower()
            unit_counts[unit] += count

            # Normalize to kg without considering count
            normalized_value = normalize_to_kg(*value.split())
            if normalized_value is not None:
                # Create a discrete value by rounding to two decimal places
                discrete_value = round(normalized_value, 3)  # Corrected to three decimal places
                if unit != 'l':
                    discrete_value_counts[(discrete_value, 'kg')] += count
                else:
                    discrete_value_counts[(discrete_value, unit)] += count

    return unit_counts, discrete_value_counts

def print_results(unit_counts, discrete_value_counts):
    print("Total counts for each unit:")
    for unit, count in unit_counts.items():
        print(f'Total count of {unit}: {count}')

    print("\nDiscrete value counts for each unit (normalized to kg):")
    for (value, unit), count in discrete_value_counts.items():
        print(f'Total count of {value} {unit}: {count}')