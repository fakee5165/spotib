import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configuration
TELEGRAM_BOT_TOKEN = "6207831810:AAGp0zPsMNWAXRuUI2qDmHyyDSGgb8bYeMk"
CHANNEL_USERNAME = "@AnonConnection"  # Replace with your channel username

# Fetch top 5 ICOs from icodrops
def get_top_upcoming_icos_from_icodrops():
    url = "https://icodrops.com/category/upcoming-ico/"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return f"Error: Failed to fetch data. Status code: {response.status_code}"

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all projects with the appropriate class
        projects = soup.find_all('li', class_='Tbl-Row Tbl-Row--usual')  # Update this line based on the new class

        top_icos = []
        for project in projects[:5]:
            # Extract ICO project data
            name = project.find('p', class_='Cll-Project__name').text.strip()  # Update this line
            date = project.find('p', class_='Cll-Project__date').text.strip() if project.find('p', class_='Cll-Project__date') else "No date available"  # Update this line
            description = project.find('p', class_='Cll-Project__description').text.strip() if project.find('p', class_='Cll-Project__description') else "No description available."  # Update this line
            image_url = project.find('img')['data-src'] if project.find('img') else ""

            top_icos.append({
                "name": name,
                "date": date,
                "description": description,
                "image_url": image_url
            })

        return top_icos

    except Exception as e:
        return f"Error: {str(e)}"

# Check if user is a member of the channel
async def is_user_in_channel(user_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getChatMember"
    params = {"chat_id": CHANNEL_USERNAME, "user_id": user_id}
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            status = response.json().get("result", {}).get("status", "left")
            return status in ["member", "administrator", "creator"]
        else:
            return False
    except requests.RequestException:
        return False


# Command to send top ICOs
async def send_upcoming_icos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await is_user_in_channel(user_id):
        await update.message.reply_text(f"Please join our channel {CHANNEL_USERNAME} to use this bot.")
        return

    icos = get_top_upcoming_icos_from_icodrops()

    # If there's an error in fetching ICOs, print the error
    if isinstance(icos, str):
        await update.message.reply_text(icos)  # Print error message
        return

    # Check the ICOs list content
    print("Fetched ICOs:", icos)

    # Emoji using Unicode
    message = "🔄 Top 5 Upcoming ICOs from ICODrops:\n\n"
    for idx, ico in enumerate(icos, 1):
        message += (
            f"{idx}. {ico['name']}\n"
            f"   Date: {ico['date']}\n"
            f"   Description: {ico['description']}\n"
            f"   Image: {ico['image_url']}\n\n"
        )

    # Print the constructed message to debug
    print("Constructed message:", message)

    # If the message is too long, split it into smaller chunks
    if len(message) > 4096:
        chunks = [message[i:i+4096] for i in range(0, len(message), 4096)]
        for chunk in chunks:
            await update.message.reply_text(chunk)
    else:
        await update.message.reply_text(message)

# Welcome message
async def send_welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Welcome to the bot! Please join our channel {CHANNEL_USERNAME} to use the features.\n"
        "Use /upcoming_icos to see the top upcoming ICOs from ICODrops."
    )

# Main function
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", send_welcome_message))
    application.add_handler(CommandHandler("upcoming_icos", send_upcoming_icos))

    application.run_polling()

if __name__ == "__main__":
    main()
