from datetime import date

start_date_str = '2023.02.02'
end_date_str = '2025.03.12'

# Parse the date strings into date objects
start_date = date(*map(int, start_date_str.split('.')))
end_date = date(*map(int, end_date_str.split('.')))

# Calculate the difference between the two dates
delta = end_date - start_date

# Output the number of days
print(f"The number of days between {start_date_str} and {end_date_str} is {delta.days} days.")