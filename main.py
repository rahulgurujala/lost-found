import asyncio
import logging
import os
import time

from rich.console import Console
from rich.logging import RichHandler

from constants import URL_TEMPLATE
from extract import create_scraper, save_to_csv, save_to_json
from models import ArticleType, ComplaintType, SearchParams

# Configure rich logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)
logger = logging.getLogger("lostfound")
console = Console()


async def main_async():
    # Create output directory if it doesn't exist
    os.makedirs("./output", exist_ok=True)

    # Create search parameters
    params = SearchParams(
        complaint_type=ComplaintType.LOST_ITEM,
        article_type=ArticleType.OTHER_DOCUMENTS,
        article_desc="AirPods",
        page=1,
    )

    # Extract base URL from template
    base_url = URL_TEMPLATE.split("?")[0]

    # Create scraper
    scraper = create_scraper(base_url)

    # Display search parameters
    console.print(
        "[bold green]Starting scraper with the following parameters:[/bold green]"
    )
    console.print(f"Complaint Type: [cyan]{params.complaint_type.name}[/cyan]")
    console.print(f"Article Type: [cyan]{params.article_type.value}[/cyan]")
    console.print(f"Article Description: [cyan]{params.article_desc}[/cyan]")

    # Measure execution time
    start_time = time.time()

    with console.status(
        "[bold green]Scraping pages asynchronously...[/bold green]"
    ):
        # Use async scraping
        all_items = await scraper.scrape_all_pages_async(params.to_dict())

    end_time = time.time()
    execution_time = end_time - start_time

    # Display results
    console.print(
        f"[bold green]Scraped a total of {len(all_items)} items in {execution_time:.2f} seconds[/bold green]"
    )

    # Save results with progress indication
    if all_items:
        with console.status("[bold green]Saving results...[/bold green]"):
            # save_to_csv(all_items, f"./output/results_async.csv")
            save_to_json(all_items, f"./output/results_async.json")
        console.print(
            "[bold green]Results saved to output directory[/bold green]"
        )
    else:
        console.print("[bold red]No items found to save[/bold red]")


def main_parallel():
    # Create output directory if it doesn't exist
    os.makedirs("./output", exist_ok=True)

    # Create search parameters
    params = SearchParams(
        complaint_type=ComplaintType.LOST_ITEM,
        article_type=ArticleType.OTHER_DOCUMENTS,
        article_desc="AirPods",
        page=1,
    )

    # Extract base URL from template
    base_url = URL_TEMPLATE.split("?")[0]

    # Create scraper
    scraper = create_scraper(base_url)

    # Display search parameters
    console.print(
        "[bold green]Starting scraper with the following parameters:[/bold green]"
    )
    console.print(f"Complaint Type: [cyan]{params.complaint_type.name}[/cyan]")
    console.print(f"Article Type: [cyan]{params.article_type.value}[/cyan]")
    console.print(f"Article Description: [cyan]{params.article_desc}[/cyan]")

    # Measure execution time
    start_time = time.time()

    with console.status(
        "[bold green]Scraping pages in parallel...[/bold green]"
    ):
        # Use parallel scraping with 10 workers
        all_items = scraper.scrape_all_pages_parallel(
            params.to_dict(), max_workers=10
        )

    end_time = time.time()
    execution_time = end_time - start_time

    # Display results
    console.print(
        f"[bold green]Scraped a total of {len(all_items)} items in {execution_time:.2f} seconds[/bold green]"
    )

    # Save results with progress indication
    if all_items:
        with console.status("[bold green]Saving results...[/bold green]"):
            save_to_csv(all_items, "./output/results_parallel.csv")
            save_to_json(all_items, "./output/results_parallel.json")
        console.print(
            "[bold green]Results saved to output directory[/bold green]"
        )
    else:
        console.print("[bold red]No items found to save[/bold red]")


if __name__ == "__main__":
    # Choose which method to use
    use_async = True  # Set to False to use parallel instead

    if use_async:
        console.print("[bold blue]Using asynchronous scraping[/bold blue]")
        asyncio.run(main_async())
    else:
        console.print("[bold blue]Using parallel scraping[/bold blue]")
        main_parallel()
