#!/usr/bin/env python3
"""
Script to extract dashboard metadata (CAPTION, ROLE, USER_NAME) from Tableau workbook files (.twb)
and generate a CSV file with the extracted information.
"""

import os
import xml.etree.ElementTree as ET
import csv
import glob
from pathlib import Path

def extract_metadata_from_twb(twb_file_path):
    """
    Extract CAPTION, ROLE, and USER_NAME from a Tableau workbook file.
    
    Args:
        twb_file_path (str): Path to the .twb file
        
    Returns:
        list: List of dictionaries containing extracted metadata
    """
    try:
        tree = ET.parse(twb_file_path)
        root = tree.getroot()
        
        metadata_list = []
        
        # Find all datasource elements
        for datasource in root.findall('.//datasource'):
            # Find named-connection elements within this datasource to get the caption
            named_connections = datasource.findall('.//named-connection')
            
            for named_connection in named_connections:
                # Find connection elements within this named-connection
                connections = named_connection.findall('.//connection')
                
                for connection in connections:
                    instanceurl = connection.get('instanceurl', '')
                    role = connection.get('role', '')
                    username = connection.get('username', '')
                    
                    # Only add if instanceurl contains "snowflakecomputing.com" and we have at least some meaningful data
                    if 'snowflakecomputing.com' in instanceurl and (instanceurl or role or username):
                        metadata_list.append({
                            'dashboard_name': os.path.basename(twb_file_path).replace('.twb', ''),
                            'instanceurl': instanceurl,
                            'role': role,
                            'username': username,
                            'file_path': twb_file_path
                        })
        
        return metadata_list
        
    except ET.ParseError as e:
        print(f"Error parsing XML in {twb_file_path}: {e}")
        return []
    except Exception as e:
        print(f"Error processing {twb_file_path}: {e}")
        return []

def find_all_twb_files(extracted_files_dir):
    """
    Find all .twb files in the extracted_files directory.
    
    Args:
        extracted_files_dir (str): Path to the extracted_files directory
        
    Returns:
        list: List of paths to .twb files
    """
    twb_files = []
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(extracted_files_dir):
        for file in files:
            if file.endswith('.twb'):
                twb_files.append(os.path.join(root, file))
    
    return twb_files

def main():
    """Main function to extract metadata and generate CSV."""
    
    # Define paths
    extracted_files_dir = "extracted_files"
    output_csv = "dashboard_metadata_instanceurl.csv"
    
    print("Starting dashboard metadata extraction...")
    print(f"Looking for .twb files in: {extracted_files_dir}")
    
    # Find all .twb files
    twb_files = find_all_twb_files(extracted_files_dir)
    print(f"Found {len(twb_files)} .twb files")
    
    if not twb_files:
        print("No .twb files found. Exiting.")
        return
    
    # Extract metadata from all files
    all_metadata = []
    
    for twb_file in twb_files:
        print(f"Processing: {twb_file}")
        metadata = extract_metadata_from_twb(twb_file)
        all_metadata.extend(metadata)
    
    print(f"Extracted metadata from {len(all_metadata)} datasources")
    
    # Write to CSV
    if all_metadata:
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['dashboard_name', 'instanceurl', 'role', 'username', 'file_path']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(all_metadata)
        
        print(f"CSV file created: {output_csv}")
        print(f"Total records: {len(all_metadata)}")
        
        # Display summary
        unique_dashboards = len(set(record['dashboard_name'] for record in all_metadata))
        unique_instanceurls = len(set(record['instanceurl'] for record in all_metadata if record['instanceurl']))
        unique_roles = len(set(record['role'] for record in all_metadata if record['role']))
        unique_usernames = len(set(record['username'] for record in all_metadata if record['username']))
        
        print(f"\nSummary:")
        print(f"- Unique dashboards: {unique_dashboards}")
        print(f"- Unique instanceurls: {unique_instanceurls}")
        print(f"- Unique roles: {unique_roles}")
        print(f"- Unique usernames: {unique_usernames}")
        
    else:
        print("No metadata extracted. No CSV file created.")

if __name__ == "__main__":
    main()
