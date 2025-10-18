# Tableau_Workbook_Query_Extractor

Tableau SQL Query Extractor is a Python automation tool that extracts SQL queries and dashboard metadata from Tableau workbooks at enterprise scale. It enables data lineage tracking, query dependency analysis, and supports data governance for Tableau Cloud and Server environments.

🚀 Features

Bulk Processing: Extract SQL from 100+ Tableau workbooks, generating 650+ SQL files automatically.

REST API Integration: Secure workbook downloads via Tableau REST API v3.20.

Secure Authentication: Personal Access Token (PAT) with SSL/TLS and session management.

Advanced XML Parsing: Handles complex Tableau workbook XML with nested elements and namespace variations.

Metadata Extraction: Extracts dashboard details, user roles, connection info, and query dependencies.

Automated File Management: Organized downloads, extracted files, and SQL outputs with timestamped filenames.

SQL Analysis: Detects table usage, MD5 hashing, and query patterns.

Batch Processing & Logging: Progress tracking, success/failure logging, and retry mechanisms.
