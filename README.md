This project is a web scraping tool designed to extract posts, comments, and other related information from the Zoom company page on Blind. 
The scraper navigates through multiple pages of posts, follows each post link, and extracts relevant data, such as post titles, previews, comments, posters, and dates.

Features
Scrapes posts and associated comments from the Zoom company page on Blind.
Handles dynamic content loading using Selenium WebDriver and BeautifulSoup.
Outputs data to CSV and Excel formats for easy analysis.
Logs scraping progress and errors for troubleshooting.


Prerequisites
Python 3.7 or higher
Google Chrome browser installed
ChromeDriver compatible with your Chrome version

Installation:
1. Clone this repository:

git clone https://github.com/yourusername/zoom-posts-scraper.git
cd zoom-posts-scraper

2. Install the required packages
pip install -r requirements.txt

Note: The installation must include the necessary libraries as it might not work without the following libraries installed
selenium
beautifulsoup4
pandas
openpyxl

3. Install and set up Chrome Driver
Set up ChromeDriver:

Download ChromeDriver from here (https://sites.google.com/chromium.org/driver/getting-started).
Ensure the downloaded version matches your installed Chrome browser version.
Place the ChromeDriver executable in a directory included in your system's PATH or specify the path directly in the script.

4. Set the driver in the correct Path and modify this line in your script
service = Service('/path/to/your/chromedriver')  # Replace with the correct path to your chromedriver

Note: If you want to run the script in headless mode, uncomment the chrome_options.add_argument("--headless") line in the script.

5. Finally, run the script
python zoom_scraper.py


Troubleshooting
If the script doesn't work as expected in headless mode, try running it with the browser visible by commenting out the headless mode option.
Use the saved page source files or screenshots to debug rendering or JavaScript loading issues in headless mode.





