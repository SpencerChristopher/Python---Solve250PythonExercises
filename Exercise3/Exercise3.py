from collections import defaultdict

def processraw(sample_list):
    unit_counts = defaultdict(int)

    # Iterate through the list and update the counts
    for i in range(0, len(sample_list), 2):
        value, count = sample_list[i], sample_list[i + 1]
        unit = value.split()[1].lower() if value else 'empty'
        unit_counts[unit] += count

    # Print the total counts for each unit
    for unit, count in unit_counts.items():
        print(f'Total count of {unit}: {count}')