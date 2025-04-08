# Mumbai Police Lost & Found Items Scraper

![Project Banner](https://img.shields.io/badge/Mumbai%20Police-Lost%20%26%20Found%20Scraper-blue)
![Python Version](https://img.shields.io/badge/python-3.10-green)
![License](https://img.shields.io/badge/license-MIT-orange)

<mark>
This project, <b>Mumbai Police Lost & Found Items Scraper</b>,  is developed purely for educational and analysis purposes. It is not affiliated with or endorsed by the Mumbai Police or any official authority. The content and functionality are intended for learning and demonstration only.
</mark>

## 📋 Overview

This project is a high-performance web scraper designed to extract lost and found item reports from the Mumbai Police website. It provides both asynchronous and parallel processing capabilities to efficiently collect data about lost items, enabling analysis of patterns and trends.

## 🌟 Features

- **High-Performance Scraping**: Implements both asynchronous (using `aiohttp`) and parallel (using `ThreadPoolExecutor`) scraping methods
- **Detailed Data Extraction**: Extracts comprehensive information about lost/found items including police station, contact details, and item descriptions
- **Data Analysis**: Includes tools to analyze the collected data with visualizations for patterns by location, time, and day
- **Flexible Search Parameters**: Supports filtering by complaint type, article type, and description
- **Rich Console Output**: Uses the `rich` library for beautiful terminal output with progress indicators
- **Data Export**: Exports data to both CSV and JSON formats for further processing

## 🏗️ Architecture

The project is structured around several key components:

### Core Components

- **Models**: Defines data structures and enumerations for the application
- **Scraper**: Handles the web scraping logic with both synchronous and asynchronous implementations
- **Data Analysis**: Processes and visualizes the collected data
- **CLI Interface**: Provides a user-friendly command-line interface

### Data Flow

1. User defines search parameters (complaint type, article type, description)
2. Scraper fetches the first page and determines total number of pages
3. Remaining pages are scraped concurrently (async or parallel)
4. Data is processed, cleaned, and saved to disk
5. Analysis tools generate visualizations and statistics

## 📊 Data Analysis

The project includes comprehensive data analysis capabilities:

- **Temporal Analysis**: Identifies patterns by hour of day, day of week, and month
- **Spatial Analysis**: Maps lost items to specific areas in Mumbai
- **Contact Information Analysis**: Analyzes patterns in contact information
- **Police Station Distribution**: Shows which stations handle the most lost item reports

Example insights from our analysis:

- Most items are reported lost on Saturdays
- Peak reporting hours are between 6-8 PM
- Andheri, Malad, and Vile Parle are the top areas for lost items
- Nearly 90% of reports come from Mumbai pin codes

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- pip or uv package manager

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/rahulgurujala/lost-found.git
   cd lost-found
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   # or with uv
   uv pip install -e .
   ```

### Usage

#### Basic Usage

Run the scraper with default parameters:

```bash
python main.py
```

This will scrape lost item reports for "AirPods" and save the results to the `output` directory.

#### Advanced Usage

To customize the search parameters, modify the `params` object in `main.py`:

```python
params = SearchParams(
    complaint_type=ComplaintType.LOST_ITEM,  # or FOUND_ITEM
    article_type=ArticleType.DRIVING_LICENSE,  # various options available
    article_desc="iPhone",  # search term
    page=1,  # starting page
)
```

#### Running Analysis

After collecting data, run the analysis script:

```bash
python analyze.py
```

This will generate visualizations and a summary report in the `output/analysis` directory.

## 📚 Using as a Module

You can easily integrate this scraper into your own Python projects. Here's how to use it as a module:

### Basic Usage Example

Create a new Python file (e.g., `my_scraper.py`) and import the necessary components:

```python
from models import SearchParams, ComplaintType, ArticleType
from constants import URL_TEMPLATE
from extract import create_scraper, save_to_json
import asyncio

async def main():
    # Define your search parameters
    params = SearchParams(
        complaint_type=ComplaintType.LOST_ITEM,
        article_type=ArticleType.DRIVING_LICENSE,
        article_desc="License",
        page=1,
    )

    # Extract base URL from template
    base_url = URL_TEMPLATE.split("?")[0]

    # Create scraper instance
    scraper = create_scraper(base_url)

    # Fetch data asynchronously
    items = await scraper.scrape_all_pages_async(params.to_dict())

    # Process the results
    print(f"Found {len(items)} items")

    # Save to JSON if needed
    save_to_json(items, "my_results.json")

    return items

# Run the async function
if __name__ == "__main__":
    results = asyncio.run(main())
```

### Using Parallel Processing Instead

If you prefer parallel processing over async:

```python
from models import SearchParams, ComplaintType, ArticleType
from constants import URL_TEMPLATE
from extract import create_scraper, save_to_json

def main():
    # Define your search parameters
    params = SearchParams(
        complaint_type=ComplaintType.LOST_ITEM,
        article_type=ArticleType.DRIVING_LICENSE,
        article_desc="License",
        page=1,
    )

    # Extract base URL from template
    base_url = URL_TEMPLATE.split("?")[0]

    # Create scraper instance
    scraper = create_scraper(base_url)

    # Fetch data in parallel (with 8 workers)
    items = scraper.scrape_all_pages_parallel(params.to_dict(), max_workers=8)

    # Process the results
    print(f"Found {len(items)} items")

    # Save to JSON if needed
    save_to_json(items, "my_results.json")

    return items

if __name__ == "__main__":
    results = main()
```

### Extracting Data from Local HTML Files

If you have already saved HTML files:

```python
from extract import extract_details_from_html_file

# Extract data from a local HTML file
items = extract_details_from_html_file("path/to/saved_page.html")
print(f"Extracted {len(items)} items from file")
```

### Custom Data Processing

You can also process the extracted data directly:

```python
from models import SearchParams, ComplaintType, ArticleType
from constants import URL_TEMPLATE
from extract import create_scraper
import asyncio

async def process_lost_items():
    # Setup scraper
    params = SearchParams(
        complaint_type=ComplaintType.LOST_ITEM,
        article_type=ArticleType.OTHER_DOCUMENTS,
        article_desc="AirPods",
    )
    base_url = URL_TEMPLATE.split("?")[0]
    scraper = create_scraper(base_url)

    # Get data
    items = await scraper.scrape_all_pages_async(params.to_dict())

    # Custom processing
    mobile_related = [
        item for item in items
        if "mobile" in item.get("article_desc", "").lower()
    ]

    # Group by police station
    by_station = {}
    for item in items:
        station = item.get("police_station", "Unknown")
        if station not in by_station:
            by_station[station] = []
        by_station[station].append(item)

    return {
        "total": len(items),
        "mobile_related": len(mobile_related),
        "stations": {station: len(items) for station, items in by_station.items()}
    }

if __name__ == "__main__":
    summary = asyncio.run(process_lost_items())
    print(f"Total items: {summary['total']}")
    print(f"Mobile-related items: {summary['mobile_related']}")
    print("Top 3 police stations:")
    for station, count in sorted(summary['stations'].items(),
                                key=lambda x: x[1], reverse=True)[:3]:
        print(f"  - {station}: {count} items")
```

### Integration with Data Analysis

To perform analysis on the scraped data:

```python
import pandas as pd
import matplotlib.pyplot as plt
from models import SearchParams, ComplaintType, ArticleType
from constants import URL_TEMPLATE
from extract import create_scraper
import asyncio

async def analyze_lost_items():
    # Setup and get data
    params = SearchParams(
        complaint_type=ComplaintType.LOST_ITEM,
        article_type=ArticleType.OTHER_DOCUMENTS,
        article_desc="AirPods",
    )
    base_url = URL_TEMPLATE.split("?")[0]
    scraper = create_scraper(base_url)
    items = await scraper.scrape_all_pages_async(params.to_dict())

    # Convert to DataFrame
    df = pd.DataFrame(items)

    # Simple analysis
    if 'police_station' in df.columns:
        station_counts = df['police_station'].value_counts().head(10)

        # Create visualization
        plt.figure(figsize=(10, 6))
        station_counts.plot(kind='bar')
        plt.title('Top 10 Police Stations with Lost Item Reports')
        plt.xlabel('Police Station')
        plt.ylabel('Number of Reports')
        plt.tight_layout()
        plt.savefig('station_analysis.png')

        return {
            "total_items": len(df),
            "unique_stations": df['police_station'].nunique(),
            "top_station": station_counts.index[0],
            "top_station_count": station_counts.iloc[0]
        }

    return {"total_items": len(df)}

if __name__ == "__main__":
    results = asyncio.run(analyze_lost_items())
    print(f"Analysis complete! Found {results['total_items']} items.")
    if 'top_station' in results:
        print(f"Most common police station: {results['top_station']} with {results['top_station_count']} reports")
```

## 📈 Performance

The project offers two high-performance scraping methods:

1. **Asynchronous Scraping**: Uses `aiohttp` and `asyncio` for non-blocking I/O operations
2. **Parallel Scraping**: Uses `ThreadPoolExecutor` for parallel processing

Performance comparison on a sample dataset (10 pages):

| Method                | Time (seconds) | Items Scraped |
| --------------------- | -------------- | ------------- |
| Synchronous           | 12.5           | 173           |
| Parallel (10 workers) | 4.2            | 173           |
| Asynchronous          | 3.1            | 173           |

## 📊 Sample Analysis Results

Based on our analysis of lost item reports:

- **Top Police Stations**:

  - B.K.C.: 12 reports
  - R.A.K. Marg: 11 reports
  - Bangur Nagar Link Road: 10 reports

- **Time Patterns**:

  - Most common time: 19:00 hours (7 PM)
  - Most common day: Saturday

- **Location Hotspots**:

  - Andheri: 26 mentions
  - Malad: 20 mentions
  - Vile Parle: 17 mentions

- **Contact Information**:
  - 89.6% of reports have Mumbai pin codes
  - Top email domains: gmail (144), outlook (5), yahoo (4)

## 🛠️ Project Structure

```
lostfound/
├── constants.py         # Constants and configuration
├── extract.py           # Scraping logic
├── main.py              # Entry point
├── models.py            # Data models
├── analyze.py           # Data analysis
├── output/              # Output directory
│   ├── results_async.json  # Scraped data
│   ├── results_async.csv   # Scraped data (CSV)
│   └── analysis/        # Analysis results
│       ├── summary_report.txt
│       ├── police_station_distribution.png
│       ├── hourly_distribution.png
│       └── ...
├── pyproject.toml       # Project metadata
└── README.md            # This file
```

## 🤝 Contributing

Contributions are welcome! Here's how you can contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- Mumbai Police for providing the public lost and found database
- The open-source community for the excellent libraries used in this project

## 📞 Contact

For questions or feedback, please open an issue on GitHub or contact the maintainer.

---

Made with ❤️ by Rahul Gurujala
