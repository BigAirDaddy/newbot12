import discord
import time
from discord.ext import commands, tasks
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Create a new instance of intents
intents = discord.Intents.default()
intents.typing = False  # You can adjust these intents as needed

# Initialize the Discord bot with intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Replace with your channel ID
YOUR_CHANNEL_ID = 1154626838035959878
DISCORD_TOKEN = 'MTE1NDYxNDY2MTAyMzUzMTE1OQ.G1lrKC.GRGwILDvQis3UeCSTf_2-YnrqB8zfgPnNhfkGE'

# Function to click the "Reply" button, scrape comments, and return
def click_reply_and_scrape_comments(driver):
    # Find and click the "Reply" button
    try:
        reply_button = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div#reply-button-end ytd-button-renderer a'))
        )
        ActionChains(driver).move_to_element(reply_button).click().perform()
    except Exception as e:
        print(f"Error clicking the reply button: {str(e)}")

    # Wait for the comments to load (adjust the wait time as needed)
    time.sleep(10)  # Adjust as needed

    # Extract and save comments
    comments = driver.find_elements(By.CSS_SELECTOR, 'ytd-backstage-comment')
    comment_text = ""
    for comment in comments:
        comment_text += comment.find_element(By.CSS_SELECTOR, 'div#content').text + '\n'

    # Go back to the community page
    driver.back()

    return comment_text

# Function to scrape community posts and read comments
async def scrape_community_post_and_comments(ctx):
    # Initialize the Selenium WebDriver (use Chrome or Firefox WebDriver)
    driver = webdriver.Chrome()  # Use Chrome WebDriver
    # driver = webdriver.Firefox()  # Use Firefox WebDriver

    # Open the channel's community page
    channel_url = 'https://www.youtube.com/@DanielLarson-ob2jw/community'  # Replace with the actual channel URL
    driver.get(channel_url)

    # Find and extract the first community post (with explicit wait)
    try:
        first_post = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, 'ytd-backstage-post-thread-renderer'))
        )
    except Exception as e:
        print(f"No community posts found: {str(e)}")
        driver.quit()
        return

    # Extract and save the content of the first post
    post_content = first_post.text

    # Extract and save comments for the first post if available
    comment_text = click_reply_and_scrape_comments(driver)

    # Send the post content and comments to Discord
    await ctx.send(f"**Post Content:**\n{post_content}\n\n**Comments:**\n{comment_text}")

    # Close the WebDriver
    driver.quit()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await scrape_task.start()

# Create a scheduled task to scrape periodically
@tasks.loop(minutes=30)  # Adjust the interval as needed
async def scrape_task():
    # Get the channel where you want to send updates
    channel = bot.get_channel(YOUR_CHANNEL_ID)  # Replace with your channel ID

    # Call the scraping function
    await scrape_community_post_and_comments(channel)

# Run the bot
bot.run('DISCORD_TOKEN')
