#!/usr/bin/env python3
"""
Script to analyze SQL queries and extract table names and MD5 usage information.
Creates a CSV file with workbook name, query, full_query, tables_used, and md5_used_or_not columns.
"""

import os
import re
import csv
import glob
from pathlib import Path

def extract_table_names(sql_content):
    """
    Extract table names from SQL query content using advanced parsing logic.
    
    Args:
        sql_content (str): SQL query content
        
    Returns:
        set: Set of unique table names found in the query
    """
    # Function to check if an identifier was quoted in the original query
    def was_quoted(identifier):
        return f'"{identifier}"' in sql_content or f'"{identifier.upper()}"' in sql_content or f'"{identifier.lower()}"' in sql_content
    
    # Clean the content while preserving structure
    content = re.sub(r'--.*?\n|/\*.*?\*/|[\n\r\t]+', ' ', sql_content, flags=re.DOTALL)
    content = re.sub(r'\\+[tnr]', ' ', content)
    content = re.sub(r'\s+', ' ', content)
    content = re.sub(r'\\+n', ' ', content)
    content = content.strip()
    original_content = content
    
    # Extract all individual SQL statements
    queries = []
    current_query = ""
    in_quotes = False
    quote_char = None
    
    for char in original_content:
        if char in ['"', "'"]:
            if not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char:
                in_quotes = False
                quote_char = None
        
        current_query += char
        
        if char == ';' and not in_quotes:
            queries.append(current_query.strip())
            current_query = ""
    
    if current_query.strip():
        queries.append(current_query.strip())
    
    # Track the current default database and schema context
    current_db = None
    current_schema = None
    
    # Table references to return
    tables = set()
    
    # Extract CTE names to exclude them
    cte_pattern = re.compile(r'([a-zA-Z0-9_]+)\s+AS\s*\(', re.IGNORECASE)
    cte_name_pattern = re.compile(r'([a-zA-Z0-9_]+)', re.IGNORECASE)
    
    # Extract subquery aliases to exclude them
    subquery_pattern = re.compile(r'\(\s*SELECT.*?\)\s*(?:AS\s*)?([a-zA-Z0-9_"]+)', re.IGNORECASE | re.DOTALL)
    
    # Extract temporary tables created in the script to exclude them
    temp_table_pattern = re.compile(r'CREATE\s+(?:LOCAL\s+)?TEMP(?:ORARY)?\s+TABLE\s+([a-zA-Z0-9_"]+)', re.IGNORECASE)
    
    # List to store temporary table names
    temp_tables = []
    subquery_aliases = []
    
    # List of SQL keywords that should never be considered as table names
    sql_keywords = ['SET', 'WHERE', 'GROUP', 'ORDER', 'HAVING', 'LIMIT', 'OFFSET', 'UNION', 'INTERSECT', 
                    'EXCEPT', 'ALL', 'DISTINCT', 'INTO', 'VALUES', 'AS', 'ON', 'USING', 'WITH', 'INNER']
    
    for query in queries:
        # Check for USE DATABASE statement
        use_db_match = re.search(r'USE\s+DATABASE\s+([a-zA-Z0-9_"]+)', query, re.IGNORECASE)
        if use_db_match:
            current_db = use_db_match.group(1).strip('"')
            continue
            
        # Check for USE SCHEMA statement
        use_schema_match = re.search(r'USE\s+SCHEMA\s+([a-zA-Z0-9_"]+)', query, re.IGNORECASE)
        if use_schema_match:
            current_schema = use_schema_match.group(1).strip('"')
            continue
            
        # Check for USE db.schema statement
        use_db_schema_match = re.search(r'USE\s+([a-zA-Z0-9_"]+)\.([a-zA-Z0-9_"]+)', query, re.IGNORECASE)
        if use_db_schema_match:
            current_db = use_db_schema_match.group(1).strip('"')
            current_schema = use_db_schema_match.group(2).strip('"')
            continue
        
        # Collect temporary tables
        temp_matches = temp_table_pattern.findall(query)
        for temp_table in temp_matches:
            temp_tables.append(temp_table.strip('"'))
        
        # Extract CTEs to exclude them
        cte_names = []
        cte_sections = cte_pattern.findall(query)
        for cte_section in cte_sections:
            cte_parts = cte_section.split(',')
            for part in cte_parts:
                cte_match = cte_name_pattern.search(part.strip())
                if cte_match:
                    cte_names.append(cte_match.group(1).strip('"'))
        
        # Extract subquery aliases
        for match in subquery_pattern.finditer(query):
            alias = match.group(1).strip('"')
            subquery_aliases.append(alias)
        
        # Extract FROM clauses
        from_pattern = re.compile(r'FROM\s+([^\s();,]+)', re.IGNORECASE)
        from_matches = from_pattern.findall(query)
        
        # Extract JOIN clauses
        join_pattern = re.compile(r'JOIN\s+([^\s();,]+)', re.IGNORECASE)
        join_matches = join_pattern.findall(query)
        
        # Extract INSERT INTO
        insert_pattern = re.compile(r'INSERT\s+INTO\s+([^\s();,]+)', re.IGNORECASE)
        insert_matches = insert_pattern.findall(query)
        
        # Extract UPDATE
        update_pattern = re.compile(r'UPDATE\s+(?!SET\s)([^\s();,]+)', re.IGNORECASE)
        update_matches = update_pattern.findall(query)
        
        # Extract MERGE INTO
        merge_pattern = re.compile(r'MERGE\s+INTO\s+([^\s();,]+)', re.IGNORECASE)
        merge_matches = merge_pattern.findall(query)
        
        # Extract DELETE FROM
        delete_pattern = re.compile(r'DELETE\s+FROM\s+([^\s();,]+)', re.IGNORECASE)
        delete_matches = delete_pattern.findall(query)
        
        # Extract ALTER TABLE
        alter_pattern = re.compile(r'ALTER\s+TABLE\s+([^\s();,]+)', re.IGNORECASE)
        alter_matches = alter_pattern.findall(query)
        
        # Extract TRUNCATE TABLE
        truncate_pattern = re.compile(r'TRUNCATE\s+TABLE\s+([^\s();,]+)', re.IGNORECASE)
        truncate_matches = truncate_pattern.findall(query)

        # Extract OVERWRITE INTO
        overwrite_pattern = re.compile(r'OVERWRITE\s+INTO\s+([^\s();,]+)', re.IGNORECASE)
        overwrite_matches = overwrite_pattern.findall(query)
        
        # Extract CREATE TABLE ... LIKE
        create_like_pattern = re.compile(r'CREATE\s+TABLE\s+[^\s();,]+\s+LIKE\s+([^\s();,]+)', re.IGNORECASE)
        create_like_matches = create_like_pattern.findall(query)
        
        # Extract DROP TABLE statements
        drop_pattern = re.compile(r'DROP\s+TABLE\s+(?:IF\s+EXISTS\s+)?([^\s();,]+)', re.IGNORECASE)
        drop_matches = drop_pattern.findall(query)
        
        # Combine all table references
        all_refs = from_matches + join_matches + insert_matches + update_matches + merge_matches + \
                   delete_matches + alter_matches + truncate_matches + create_like_matches + drop_matches + overwrite_matches
        
        for table_ref in all_refs:
            # Skip SQL keywords, CTE references, subquery aliases, and temp tables
            if (table_ref.strip('"').upper() in sql_keywords or
                table_ref.strip('"') in cte_names or 
                table_ref.strip('"') in subquery_aliases or 
                table_ref.strip('"') in temp_tables):
                continue
            
            # Handle quoted identifiers and parse table references
            parts = []
            current_part = ""
            in_quotes = False
            
            for char in table_ref:
                if char == '"':
                    in_quotes = not in_quotes
                    current_part += char
                elif char == '.' and not in_quotes:
                    parts.append(current_part)
                    current_part = ""
                else:
                    current_part += char
            
            if current_part:
                parts.append(current_part)
            
            # Process parts based on how many we found - preserve full table reference
            if len(parts) == 3:  # db.schema.table
                full_table_name = f"{parts[0].strip(chr(34))}.{parts[1].strip(chr(34))}.{parts[2].strip(chr(34))}"
                table_name = parts[2].strip('"')
            elif len(parts) == 2:  # schema.table
                full_table_name = f"{parts[0].strip(chr(34))}.{parts[1].strip(chr(34))}"
                table_name = parts[1].strip('"')
            elif len(parts) == 1:  # just table
                full_table_name = parts[0].strip('"')
                table_name = parts[0].strip('"')
            else:
                continue
            
            # Add to results if it's a valid table name - use full table reference
            if table_name and table_name.upper() not in sql_keywords:
                tables.add(full_table_name)
    
    return tables

def detect_md5_usage(sql_content):
    """
    Detect if MD5 function is used in the SQL query.
    MD5 is typically used for joining when one column is hashed and the other is not.
    
    Args:
        sql_content (str): SQL query content
        
    Returns:
        bool: True if MD5 function is used, False otherwise
    """
    sql_lower = sql_content.lower()
    
    # Look for MD5 function usage
    md5_patterns = [
        r'\bmd5\s*\(',
        r'\bhash\s*\(',
        r'\bhash_md5\s*\(',
        r'\bdigest\s*\(',
    ]
    
    for pattern in md5_patterns:
        if re.search(pattern, sql_lower):
            return True
    
    return False

def extract_workbook_name_from_filename(filename):
    """
    Extract workbook name from SQL filename.
    
    Args:
        filename (str): SQL filename
        
    Returns:
        str: Workbook name
    """
    # Remove the timestamp and query number from filename
    # Format: WorkbookName_YYYYMMDD_HHMMSS_query_XX.sql
    base_name = os.path.basename(filename)
    
    # Remove .sql extension
    name_without_ext = base_name.replace('.sql', '')
    
    # Split by underscore and remove the last 3 parts (timestamp and query number)
    parts = name_without_ext.split('_')
    if len(parts) >= 4:
        # Remove the last 3 parts: timestamp (2 parts) and query number (1 part)
        workbook_parts = parts[:-3]
        workbook_name = '_'.join(workbook_parts)
    else:
        workbook_name = name_without_ext
    
    return workbook_name

def extract_query_number_from_filename(filename):
    """
    Extract query number from SQL filename.
    
    Args:
        filename (str): SQL filename
        
    Returns:
        str: Query identifier
    """
    base_name = os.path.basename(filename)
    name_without_ext = base_name.replace('.sql', '')
    
    # Extract the query number part
    parts = name_without_ext.split('_')
    if len(parts) >= 2:
        query_part = parts[-1]  # Last part should be the query number
        return f"query-{query_part}"
    else:
        return "query-1"

def analyze_sql_files(sql_output_dir):
    """
    Analyze all SQL files in the output directory.
    
    Args:
        sql_output_dir (str): Path to the SQL output directory
        
    Returns:
        list: List of dictionaries containing analysis results
    """
    results = []
    
    # Get all SQL files
    sql_files = glob.glob(os.path.join(sql_output_dir, "*.sql"))
    
    print(f"Found {len(sql_files)} SQL files to analyze...")
    
    for sql_file in sql_files:
        try:
            # Read SQL content
            with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
                sql_content = f.read()
            
            # Extract information
            workbook_name = extract_workbook_name_from_filename(sql_file)
            query_id = extract_query_number_from_filename(sql_file)
            tables = extract_table_names(sql_content)
            md5_used = detect_md5_usage(sql_content)
            
            # Create one row for each table used by this query
            if tables:
                for table_name in sorted(tables):
                    result = {
                        'workbook_name': workbook_name,
                        'query': query_id,
                        'table_name': table_name,
                        'md5_used_or_not': 'yes' if md5_used else 'no'
                    }
                    results.append(result)
            else:
                # If no tables found, still create one row
                result = {
                    'workbook_name': workbook_name,
                    'query': query_id,
                    'table_name': '',
                    'md5_used_or_not': 'yes' if md5_used else 'no'
                }
                results.append(result)
            
            print(f"Analyzed: {workbook_name} - {query_id} - {len(tables)} tables - MD5: {'yes' if md5_used else 'no'}")
            
        except Exception as e:
            print(f"Error analyzing {sql_file}: {e}")
            continue
    
    return results

def save_to_csv(results, output_file):
    """
    Save analysis results to CSV file with vertical table structure.
    
    Args:
        results (list): List of analysis results
        output_file (str): Output CSV file path
    """
    if not results:
        print("No results to save.")
        return
    
    # Define fieldnames for the vertical structure
    fieldnames = ['workbook_name', 'query', 'table_name', 'md5_used_or_not']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL, escapechar='\\', doublequote=True)
        
        writer.writeheader()
        
        # Process each result to ensure proper CSV formatting
        for result in results:
            # Create a clean copy of the result
            clean_result = {}
            
            for key, value in result.items():
                if value is None:
                    clean_result[key] = ''
                else:
                    # Convert to string
                    str_value = str(value)
                    
                    # Escape quotes by doubling them (CSV standard)
                    str_value = str_value.replace('"', '""')
                    
                    # Remove any remaining problematic characters that could break CSV
                    str_value = str_value.replace('\x00', '')  # Remove null bytes
                    str_value = str_value.replace('\x1a', '')  # Remove substitute character
                    
                    clean_result[key] = str_value
            
            writer.writerow(clean_result)
    
    print(f"Results saved to: {output_file}")

def main():
    """Main function to analyze SQL queries and generate CSV."""
    
    # Define paths
    sql_output_dir = "sql_output"
    output_csv = "sql_query_analysis_vertical_format.csv"
    
    print("Starting SQL Query Analysis...")
    print("=" * 60)
    
    # Check if SQL output directory exists
    if not os.path.exists(sql_output_dir):
        print(f"SQL output directory not found: {sql_output_dir}")
        return
    
    # Analyze SQL files
    results = analyze_sql_files(sql_output_dir)
    
    if not results:
        print("No SQL files found or analyzed.")
        return
    
    # Save results to CSV
    save_to_csv(results, output_csv)
    
    # Display summary
    print("\n" + "=" * 60)
    print("ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Total table-query relationships: {len(results)}")
    
    # Count unique workbooks
    unique_workbooks = len(set(result['workbook_name'] for result in results))
    print(f"Unique workbooks: {unique_workbooks}")
    
    # Count unique queries
    unique_queries = len(set(f"{result['workbook_name']}_{result['query']}" for result in results))
    print(f"Unique queries: {unique_queries}")
    
    # Count unique tables
    unique_tables = len(set(result['table_name'] for result in results if result['table_name']))
    print(f"Unique tables: {unique_tables}")
    
    # Count queries with MD5 usage
    md5_queries = len([r for r in results if r['md5_used_or_not'] == 'yes'])
    print(f"Table-query relationships with MD5: {md5_queries}")
    
    print(f"\nOutput file: {output_csv}")
    print("CSV structure: workbook_name, query, table_name, md5_used_or_not")
    print("Each row represents one table used by one query")

if __name__ == "__main__":
    main()
