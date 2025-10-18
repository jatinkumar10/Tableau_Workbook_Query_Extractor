# Parser module for Tableau workbook XML files

import xml.etree.ElementTree as ET

def parse_twb_for_sql(twb_file):
    """
    Parse a .twb XML file to extract SQL query strings from relation elements.
    
    Args:
        twb_file (str): Path to the .twb XML file
        
    Returns:
        list: List of SQL query strings found in the workbook
        
    Raises:
        FileNotFoundError: If the .twb file doesn't exist
        ET.ParseError: If the XML file is malformed
    """
    print(f"🔍 Parsing SQL queries from: {twb_file}")
    
    # Parse the XML file
    tree = ET.parse(twb_file)
    root = tree.getroot()
    
    sql_queries = []
    
    # Find all relation elements with type="text" (these contain SQL queries)
    # Handle both with and without namespace
    relations = root.findall('.//{http://tableau.com/api}relation[@type="text"]')
    if not relations:
        # Try without namespace
        relations = root.findall('.//relation[@type="text"]')
    
    print(f"📊 Found {len(relations)} relation elements with type='text'")
    
    for i, relation in enumerate(relations, 1):
        # Look for query elements within the relation
        query_elements = relation.findall('{http://tableau.com/api}query')
        if not query_elements:
            query_elements = relation.findall('query')
        
        for j, query_elem in enumerate(query_elements, 1):
            # Get the SQL query text from the query element
            sql_text = query_elem.text
            
            if sql_text and sql_text.strip():
                # Clean up the SQL text
                cleaned_sql = sql_text.strip()
                sql_queries.append(cleaned_sql)
                print(f"✅ Extracted SQL query {i}.{j}: {len(cleaned_sql)} characters")
            else:
                print(f"⚠️ Query {i}.{j} has no SQL content")
        
        # If no query elements found, try to get text directly from relation
        if not query_elements:
            sql_text = relation.text
            if sql_text and sql_text.strip():
                cleaned_sql = sql_text.strip()
                sql_queries.append(cleaned_sql)
                print(f"✅ Extracted SQL query {i} (direct): {len(cleaned_sql)} characters")
            else:
                print(f"⚠️ Relation {i} has no SQL content")
    
    print(f"🎯 Total SQL queries extracted: {len(sql_queries)}")
    
    return sql_queries