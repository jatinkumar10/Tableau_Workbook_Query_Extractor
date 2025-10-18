# Tableau SQL Extractor

A Python tool that automatically downloads Tableau workbooks from Tableau Cloud/Server and extracts SQL queries from them using the Tableau REST API.

## 🚀 Features

- **Automatic Authentication**: Uses Personal Access Token (PAT) for secure authentication
- **Workbook Download**: Downloads `.twbx` files directly from Tableau Cloud/Server via REST API
- **SQL Extraction**: Extracts SQL queries from Tableau workbook XML files
- **Organized Output**: Saves extracted SQL queries as individual `.sql` files with timestamps
- **REST API Only**: Uses official Tableau REST API (no VizPortal dependencies)
- **Error Handling**: Comprehensive error handling and progress reporting

## 📋 Prerequisites

- Python 3.7 or higher
- Tableau Cloud/Server account with Personal Access Token
- Appropriate permissions to download workbooks (Creator, Site Administrator, or Server Administrator role)

## 🛠️ Installation

1. **Clone or download this repository**
2. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

Edit the `config.py` file with your Tableau credentials:

```python
# Tableau Server Configuration
TABLEAU_SERVER_URL = "https://your-tableau-server.com"
TABLEAU_SITE_CONTENT_URL = "your-site-content-url"  # e.g., "cars24"
TABLEAU_SITE_ID = "your-site-uuid"  # e.g., "769dee74-3202-44e0-9956-da9829199cb1"
TABLEAU_API_VERSION = "3.20"

# Authentication Configuration
TABLEAU_TOKEN_NAME = "your-token-name"
TABLEAU_TOKEN_VALUE = "your-token-value"
```

### 🔑 Getting Your Credentials

1. **Server URL**: Your Tableau Cloud URL (e.g., `https://prod-apsoutheast-a.online.tableau.com`)
2. **Site Content URL**: The site identifier from your URL (e.g., from `/#/site/cars24/home` → `cars24`)
3. **Site ID**: The UUID returned during authentication (automatically extracted)
4. **Personal Access Token**: Create in Tableau Cloud under Account Settings → Personal Access Tokens

## 📁 Project Structure

```
tableau_sql_extractor/
├── config.py          # Configuration and authentication
├── downloader.py      # Workbook download functionality
├── extractor.py       # .twbx to .twb extraction
├── parser.py          # SQL query parsing from .twb files
├── saver.py           # SQL query file saving
├── main.py            # Main workflow orchestration
├── requirements.txt   # Python dependencies
├── README.md          # This file
├── downloads/         # Downloaded .twbx files
├── extracted_files/   # Extracted .twb files
└── sql_output/        # Generated .sql files
```

## 🚀 Usage

### Basic Usage

```python
from main import main

# Extract SQL from a specific workbook
main("workbook-id", "WorkbookName")
```

### Command Line Usage

```bash
python main.py
```

### Programmatic Usage

```python
import config
from downloader import download_workbook
from extractor import extract_twbx
from parser import parse_twb_for_sql
from saver import save_sql_queries

# Step 1: Download workbook
downloaded_file = download_workbook("workbook-id", "WorkbookName")

# Step 2: Extract .twb from .twbx
twb_file = extract_twbx(downloaded_file, "WorkbookName")

# Step 3: Parse SQL queries
sql_queries = parse_twb_for_sql(twb_file)

# Step 4: Save SQL queries
saved_files = save_sql_queries(sql_queries, "WorkbookName")
```

## 📊 How It Works

1. **Authentication**: Authenticates with Tableau using Personal Access Token
2. **Download**: Downloads `.twbx` workbook file via REST API
3. **Extract**: Extracts the `.twb` XML file from the `.twbx` archive
4. **Parse**: Parses the XML to find `<relation type="text">` elements containing SQL
5. **Save**: Saves each SQL query as a separate `.sql` file with timestamp

## 🔧 API Endpoints Used

- `POST /api/{version}/auth/signin` - Authentication
- `GET /api/{version}/sites/{site-id}/workbooks` - List workbooks
- `GET /api/{version}/sites/{site-id}/workbooks/{workbook-id}/content` - Download workbook
- `POST /api/{version}/auth/signout` - Sign out

## 📝 Output

SQL queries are saved in the `sql_output/` directory with the following naming convention:
- `{WorkbookName}_query1_20241201_143022.sql`
- `{WorkbookName}_query2_20241201_143022.sql`
- etc.

## 🛡️ Security

- Uses Personal Access Tokens for authentication (no password storage)
- Supports SSL/TLS connections
- Automatic session management and cleanup
- No sensitive data logged

## 🔍 Troubleshooting

### Common Issues

1. **Authentication Failed (401)**
   - Verify your Personal Access Token is correct
   - Check that the token hasn't expired
   - Ensure the site content URL is correct

2. **Site Not Found (404)**
   - Verify the site content URL matches your Tableau URL
   - Check that you have access to the specified site

3. **No SQL Queries Found**
   - Not all workbooks contain custom SQL queries
   - Some workbooks use only data source connections without custom SQL
   - Try different workbooks that might have custom calculations or SQL

4. **Permission Denied (403)**
   - Ensure your account has appropriate permissions
   - Creator, Site Administrator, or Server Administrator roles are required

### Debug Mode

Enable debug output by modifying the print statements in the code or adding logging.

## 📋 Requirements

- `requests` - HTTP library for API calls
- `lxml` - XML parsing library
- `xml.etree.ElementTree` - Built-in XML parsing (fallback)
- `zipfile` - Built-in archive handling
- `os` - Built-in file system operations
- `urllib.parse` - Built-in URL encoding
- `datetime` - Built-in timestamping

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source. Please check with your organization's policies before using.

## ⚠️ Disclaimer

This tool is for educational and legitimate business purposes only. Ensure you have proper authorization to download and extract content from your Tableau Server/Cloud instance. Always comply with your organization's data policies and Tableau's terms of service.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Verify your Tableau permissions and credentials
3. Ensure you're using the correct API version for your Tableau instance
4. Check Tableau's REST API documentation for any changes

---

**Happy SQL Extracting! 🎉**
