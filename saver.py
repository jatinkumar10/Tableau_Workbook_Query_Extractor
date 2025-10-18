# Saver module for SQL query files

import os
from datetime import datetime
from config import SQL_OUTPUT_DIRECTORY

def save_sql_queries(queries, workbook_name):
    """
    Save extracted SQL queries to individual .sql files.
    
    Args:
        queries (list): List of SQL query strings
        workbook_name (str): Name of the workbook for file naming
        
    Returns:
        list: List of file paths where SQL queries were saved
    """
    print(f"💾 Saving {len(queries)} SQL queries for workbook: {workbook_name}")
    
    # Create SQL output directory if it doesn't exist
    os.makedirs(SQL_OUTPUT_DIRECTORY, exist_ok=True)
    
    saved_files = []
    
    # Get current date for filename
    current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for i, query in enumerate(queries, 1):
        # Create filename for this query with date
        filename = f"{workbook_name}_{current_date}_query_{i:02d}.sql"
        file_path = os.path.join(SQL_OUTPUT_DIRECTORY, filename)
        
        # Write the SQL query to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(query)
        
        saved_files.append(file_path)
        print(f"✅ Saved query {i}: {filename}")
    
    print(f"🎉 All SQL queries saved to: {SQL_OUTPUT_DIRECTORY}")
    
    return saved_files