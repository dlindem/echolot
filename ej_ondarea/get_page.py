from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import os
from urllib.parse import urlparse


def save_rendered_page(url, output_dir="./saved_pages", wait_time=5):
    """
    Save a fully rendered webpage using Selenium with Chromium

    Args:
        url (str): The URL to save
        output_dir (str): Directory to save the files
        wait_time (int): Time to wait for dynamic content to load (seconds)
    """

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Configure Chrome options for headless browsing (optional)
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')  # Run in headless mode (no GUI)
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')

    # Uncomment these lines if you want to see the browser window
    # chrome_options.add_argument('--start-maximized')

    # Set up the driver (assuming chromedriver is in PATH)
    # If you need to specify the path to chromedriver:
    # service = Service('/path/to/chromedriver')
    # driver = webdriver.Chrome(service=service, options=chrome_options)

    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Navigate to the URL
        print(f"Loading {url}...")
        driver.get(url)

        # Wait for dynamic content to load
        print(f"Waiting {wait_time} seconds for content to render...")
        time.sleep(wait_time)

        # Optional: Scroll to trigger lazy-loaded content
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for lazy-loaded content

        # Get the rendered HTML
        html_content = driver.page_source

        # Generate filename from URL
        parsed_url = urlparse(url)
        filename = parsed_url.netloc.replace('.', '_') + parsed_url.path.replace('/', '_')
        if not filename or filename == parsed_url.netloc.replace('.', '_'):
            filename = "index"
        if parsed_url.query:
            filename += "_" + parsed_url.query.replace('=', '_').replace('&', '_')

        # Save HTML file
        html_file = os.path.join(output_dir, f"{filename}.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"HTML saved to: {html_file}")

        # Take a screenshot as well (optional)
        screenshot_file = os.path.join(output_dir, f"{filename}.png")
        driver.save_screenshot(screenshot_file)
        print(f"Screenshot saved to: {screenshot_file}")

        # Save page source with all resources (optional)
        # This creates a more complete save with CSS, JS, etc.
        page_data = {
            'url': driver.current_url,
            'title': driver.title,
            'html': html_content
        }

        # You could also use browser's "Save As" functionality
        # This is more complex and requires keyboard shortcuts or JavaScript

        return html_file

    except Exception as e:
        print(f"Error saving page: {e}")
        return None

    finally:
        # Close the browser
        driver.quit()



# Example usage
if __name__ == "__main__":
    # URL to save
    url = "https://www.euskadi.eus/web01-apintegr/eu/y47aIntegraWar/IBConsultaController/registrosMosaicoBien?registrosPagina=1000"  # Replace with your target URL

    # Simple save
    saved_file = save_rendered_page(
        url=url,
        output_dir="data",
        wait_time=15  # Increase this for pages with lots of dynamic content
    )

    # Or with more comprehensive resource saving
    # save_with_resources(url, "./my_saved_pages_complete")