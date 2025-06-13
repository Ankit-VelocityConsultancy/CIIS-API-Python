import re

# Specify the path to your SQL file
input_file_path = r"C:\Ankit\online_exam_portal_12-06-2025-10.55 am.sql"
output_file_path = r"C:\Ankit\cleaned_sql_file.sql"

# Open the original SQL file with utf-8 encoding
with open(input_file_path, "r", encoding="utf-8") as file:
    sql_data = file.read()

# Regular expression to match CREATE TABLE queries and remove them
sql_data_cleaned = re.sub(r"CREATE TABLE.*?;\n", "", sql_data, flags=re.DOTALL)

# Write the cleaned SQL data back to a new file
with open(output_file_path, "w", encoding="utf-8") as cleaned_file:
    cleaned_file.write(sql_data_cleaned)

print("The cleaned SQL file has been saved as 'cleaned_sql_file.sql' at C:\\Ankit")
