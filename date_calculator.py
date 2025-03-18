from datetime import date

# Define the date string
input_dates = "2023.02.02到2025.03.12"

# Split the dates into start and end
start_str, end_str = input_dates.split("到")

# Parse components of start and end dates
start_year, start_month, start_day = map(int, start_str.split('.'))
end_year, end_month, end_day = map(int, end_str.split('.'))

# Create date objects
start_date = date(start_year, start_month, start_day)
end_date = date(end_year, end_month, end_day)

# Calculate difference
delta = end_date - start_date
print(f"Days between: {delta.days}")