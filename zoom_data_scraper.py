from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time

# Set up Selenium WebDriver with headless mode
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service('/usr/local/bin/chromedriver')  # Replace with the correct path to your chromedriver
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.implicitly_wait(10)

base_url = "https://www.teamblind.com/company/Zoom/posts"
post_base_url = "https://www.teamblind.com"
page_number = 1
data = []
log_data = []

# Record start time
start_time = datetime.now()
print(f"Scraping started at: {start_time}")

# Step 1: Scrape the main posts and extract their URLs
while True:
    # Construct the URL for the current page
    url = f"{base_url}?page={page_number}"
    driver.get(url)

    # Wait for the content to load
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        print(f"Page {page_number} loaded successfully.")
    except Exception as e:
        print(f"Error loading page {page_number}: {e}")
        break

    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Debugging: Save page source for review
    with open(f'page_{page_number}_source.html', 'w') as file:
        file.write(driver.page_source)

    # Extract titles and post URLs
    title_elements = soup.find_all('h3', class_='truncate')
    post_preview_elements = soup.find_all('p', class_='line-clamp-2 break-words text-xs text-gray-700')
    url_elements = soup.find_all('a', {'data-testid': 'company-page-posts-search-preview-card'})  # Identify href tags

    if not title_elements:
        print(f"No titles found on page {page_number}. Exiting.")
        break  # Exit loop if no titles found, which likely means we've reached the last page or an error occurred

    for title_element, preview_element, url_element in zip(title_elements, post_preview_elements, url_elements):
        title = title_element.get_text(strip=True)
        main_post = preview_element.get_text(strip=True)
        post_url = post_base_url + url_element['href']

        # Step 2: Navigate to each post's page and scrape comments
        print(f"Scraping post: {title}, URL: {post_url}")
        driver.get(post_url)


        # Function to click all "View more comments" and "View more replies" buttons
        def click_view_more_buttons():
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                try:
                    # Scroll to the bottom to load all content
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(3)  # Allow time for dynamic content to load

                    # Find all "View more comments" and "View more replies" buttons
                    buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'View more')]")
                    for button in buttons:
                        if button.is_enabled():
                            try:
                                # Scroll into view and click the button
                                driver.execute_script("arguments[0].scrollIntoView();", button)
                                WebDriverWait(driver, 20).until(
                                    EC.element_to_be_clickable((By.XPATH, ".//button[contains(text(), 'View more')]")))
                                ActionChains(driver).move_to_element(button).click(button).perform()
                                time.sleep(3)  # Ensure content is fully loaded
                            except Exception as e:
                                print(f"Could not click on button: {e}")
                                continue

                    # Check if more content has loaded
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break  # Break if no new content has loaded
                    last_height = new_height
                except Exception as e:
                    print(f"Error during loading replies: {e}")
                    break


        # Click all "View more comments" and "View more replies" buttons
        click_view_more_buttons()

        # Reparse the updated page content with BeautifulSoup to capture newly loaded content
        time.sleep(5)  # Ensure all content is loaded
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find all comments on the post
        comment_elements = soup.find_all('p',
                                         class_='whitespace-pre-wrap break-words text-sm/5 text-gray-999 md:text-base/6')
        poster_elements = soup.find_all('div', class_='flex flex-wrap text-xs font-semibold text-gray-700')
        date_elements = soup.find_all('span', class_='text-gray-600')

        # Log the data
        log_data.append({
            'Scraping Post': title,
            'URL': post_url,
            'Comments Found': len(comment_elements),
            'Posters': len(poster_elements),
            'Dates Found': len(date_elements),
            'Timestamp': datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        })

        print(f"Found {len(comment_elements)} comments, {len(poster_elements)} posters, and {len(date_elements)} dates")

        # Ensure data alignment
        for i in range(max(len(comment_elements), len(poster_elements), len(date_elements))):
            comment = comment_elements[i].get_text(strip=True) if i < len(comment_elements) else ""
            poster = poster_elements[i].get_text(strip=True) if i < len(poster_elements) else ""
            date = date_elements[i].get_text(strip=True) if i < len(date_elements) else ""
            data.append({
                'Title': title,
                'Main_Post': main_post,
                'Comment': comment,
                'Response_Poster_ID': poster,
                'Date': date
            })

    # Check for the presence of a next page link
    next_page = soup.find('a', class_='nextPage')
    if next_page:
        page_number += 1
    else:
        break

# Record end time
end_time = datetime.now()

# Calculate the duration
duration = end_time - start_time
hours, remainder = divmod(duration.total_seconds(), 3600)
minutes, seconds = divmod(remainder, 60)

# Print the result with the time taken
print(
    f"Scraping completed in {int(hours)} hour(s) {int(minutes)} minute(s) {int(seconds)} second(s). {len(data)} comments were saved.")

# Store the results in a DataFrame
df = pd.DataFrame(data)

# Save to a CSV file
df.to_csv('zoom_blind_data.csv', index=False)

# Save to an Excel file
df.to_excel('zoom_blind_data.xlsx', index=False)

# Save the log to a CSV file
log_df = pd.DataFrame(log_data)
log_filename = f'zoomScraperLog_{datetime.now().strftime("%d%m%y%H%M%S")}.csv'
log_df.to_csv(log_filename, index=False)

print(f"Log file saved as {log_filename}")

# Close the browser
driver.quit()
