"""
swiftnode/bot/whatsapp_bot.py
============================
WhatsApp bot integration for SwiftNode using Selenium.
Automates WhatsApp Web to read and reply to messages.
"""
import time
from rich.console import Console
from swiftnode.config import load_config
from swiftnode.core.agent import SwiftNodeCore

console = Console()

def run_whatsapp_bot():
    """Starts the WhatsApp Web automation bot."""
    config = load_config()
    agent = SwiftNodeCore(config)
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException, NoSuchElementException
        from webdriver_manager.chrome import ChromeDriverManager
    except ImportError:
        console.print("[bold red]❌ Selenium not installed. Run `pip install selenium webdriver-manager`[/]")
        return

    console.print("[bold green]🚀 Starting WhatsApp Web Automation...[/]")
    console.print("[dim]Please wait while the browser launches...[/dim]")

    chrome_options = Options()
    # User data dir to keep session alive after scanning QR once (optional, but good for UX)
    # chrome_options.add_argument(f"user-data-dir={Path.home()}/.swiftnode/whatsapp_session")
    
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
    except Exception as e:
        console.print(f"[bold red]❌ Failed to start Chrome WebDriver: {e}[/]")
        return

    driver.get("https://web.whatsapp.com")
    
    console.print()
    console.print("[bold yellow]📸📱 PLEASE SCAN THE QR CODE ON THE OPENED BROWSER 📱📸[/]")
    console.print("[dim]Waiting for authentication...[/dim]")
    
    try:
        # Wait until the main chat pane is visible (auth success)
        WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.ID, "pane-side"))
        )
        console.print("[bold green]✅ Authenticated successfully![/]")
    except TimeoutException:
        console.print("[bold red]❌ Timeout waiting for QR scan. Closing.[/]")
        driver.quit()
        return

    console.print("[dim]Listening for new messages...[/dim]")
    
    # Simple loop to check for unread messages
    while True:
        try:
            # Look for the green unread message badge
            unread_badges = driver.find_elements(By.XPATH, "//span[contains(@aria-label, 'unread message')]")
            
            if unread_badges:
                # Click the first unread chat
                unread_badges[0].click()
                time.sleep(1) # wait for chat to load
                
                # Fetch all messages in the loaded chat
                messages = driver.find_elements(By.XPATH, "//div[contains(@class, 'message-in')]//span[contains(@class, '_ao3e')]")
                if messages:
                    last_msg_text = messages[-1].text
                    console.print(f"[cyan]Received:[/] {last_msg_text}")
                    
                    # Process with SwiftNode
                    response_text = agent.process_query(last_msg_text)
                    
                    # Type response
                    message_box = driver.find_element(By.XPATH, "//div[@contenteditable='true'][@data-tab='10']")
                    
                    # Send response line by line (Selenium send_keys doesn't handle \n well sometimes in WhatsApp)
                    for line in response_text.split('\n'):
                        message_box.send_keys(line)
                        message_box.send_keys(webdriver.common.keys.Keys.SHIFT, webdriver.common.keys.Keys.ENTER)
                    
                    time.sleep(0.5)
                    # Click send button
                    send_button = driver.find_element(By.XPATH, "//span[@data-icon='send']")
                    send_button.click()
                    
            time.sleep(2) # Polling interval
            
        except KeyboardInterrupt:
            console.print("[yellow]Shutting down WhatsApp Bot...[/]")
            break
        except Exception as e:
            # Ignore stale elements or temporary errors during DOM updates
            time.sleep(1)

    driver.quit()

if __name__ == "__main__":
    run_whatsapp_bot()
