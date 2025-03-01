from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os, time, pyperclip, pyautogui, shutil, unicodedata

source_folder = r"C:\nihongo\Easy Japanese\source"                  # Specify folder with the audio files (Not yet added into LingQ)
archive_folder = r"C:\nihongo\Easy Japanese\archive"               # Define the destination folder (Archive folder where the files should go after being added into LingQ)
website_link = "https://www.lingq.com/sv/learn/ja/web/library"      # Specify website link, include the correct language
mail_adress = "Mail"
password = "Password"

too_long_filenames = 1                                              # Set this to 1 in you have file names that are over 60 charachters long.
                                                                    # LingQ can only import files with less than 100 charachters in the file name, 
                                                                    # and can only add titles that are 60 charachters long.

chinese_or_japanese_only = 1                                        # If you only want chinese or japanese in the file names.                                   

if too_long_filenames:
    # Iterate over all items in the folder
    for file_name in os.listdir(source_folder):
        # Construct the full file path
        full_path = os.path.join(source_folder, file_name)
        
        # Check if it's a file (skip directories)
        if os.path.isfile(full_path):
            # Split the file name and extension
            name, ext = os.path.splitext(file_name)
            
            # Shorten the file name to the first 60 characters if it's longer
            if len(name) > 60:
                new_name = name[:60] + ext  # keep the extension
                new_full_path = os.path.join(source_folder, new_name)
                
                # Rename the file
                os.rename(full_path, new_full_path)
                print(f"Renamed '{file_name}' to '{new_name}'")
                
def is_cjk(c):
    """Return True if character c is in one of the Chinese/Japanese Unicode ranges."""
    return (
        '\u4e00' <= c <= '\u9fff' or  # CJK Unified Ideographs
        '\u3400' <= c <= '\u4dbf' or  # CJK Unified Ideographs Extension A
        '\u3040' <= c <= '\u309f' or  # Hiragana
        '\u30a0' <= c <= '\u30ff' or  # Katakana
        '\uff66' <= c <= '\uff9f'     # Half-width Katakana
    )

def has_cjk(text):
    """Return True if any character in text is a Chinese/Japanese character."""
    return any(is_cjk(c) for c in text)                


def filter_filename(name):
    """
    If the original name has any Chinese/Japanese characters,
    then keep only Chinese/Japanese, digits, and punctuation/symbols.
    Otherwise, keep English letters as well.
    """
    contains_cjk = has_cjk(name)
    allowed_chars = []
    for c in name:
        # Always allow digits
        if c.isdigit():
            allowed_chars.append(c)
            continue

        # If the name contains Chinese/Japanese, only allow CJK characters.
        if contains_cjk:
            if is_cjk(c):
                allowed_chars.append(c)
                continue
        else:
            # If no CJK, allow English letters as well.
            if c.isalpha():
                allowed_chars.append(c)
                continue

        # Allow punctuation or symbols
        cat = unicodedata.category(c)
        if cat[0] in ('P', 'S'):
            allowed_chars.append(c)
            continue

        # Otherwise, skip the character.
    return "".join(allowed_chars)


if chinese_or_japanese_only:
    for file_name in os.listdir(source_folder):
        full_path = os.path.join(source_folder, file_name)
        if os.path.isfile(full_path):
            # Split the file name into the base and extension
            base, ext = os.path.splitext(file_name)
            # Filter the base name
            new_base = filter_filename(base)
            new_file_name = new_base + ext
            new_full_path = os.path.join(source_folder, new_file_name)
            
            # Rename the file if the new name is different from the original
            if new_file_name != file_name:
                os.rename(full_path, new_full_path)
                print(f"Renamed: {file_name} -> {new_file_name}")


def start_driver():
    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    return driver


  
def login(driver):
    wait = WebDriverWait(driver, 20)
    driver.get(website_link)  # Replace with your URL
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "field__input"))).send_keys(mail_adress)
    wait.until(EC.element_to_be_clickable((By.ID, "id_password"))).send_keys(password)
    wait.until(EC.element_to_be_clickable((By.ID, "submit-button"))).click()




def process_files(driver, folder_path, destination_folder):
    wait = WebDriverWait(driver, 20)
    file_names = os.listdir(folder_path)
    file_names = [f for f in file_names if os.path.isfile(os.path.join(folder_path, f))]
    time.sleep(3)  # Allow page to stabilize after login

    for file_name in file_names:
        try:
            full_file_path = os.path.join(folder_path, file_name)
            title, ext = os.path.splitext(file_name)
            pyperclip.copy(full_file_path)

            # Import button
            wait.until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, ".secondary-navbar--import.grid-layout.grid-justify--right.grid-align--center")
            )).click()

            # Audio option
            wait.until(EC.visibility_of_element_located(
                (By.XPATH, "//*[@id='dropdown-menu']/div/div[4]/a")
            )).click()

            # Choose file button
            wait.until(EC.visibility_of_element_located(
                (By.XPATH, "/html/body/div[4]/div/div[2]/section[2]/div/div/div/div/button")
            )).click()

            time.sleep(2)  # wait for OS file dialog to open
            pyautogui.hotkey("ctrl", "v")
            pyautogui.press("enter")
            time.sleep(2)

            # Title input
            wait.until(EC.visibility_of_element_located(
                (By.XPATH, "/html/body/div[4]/div/div[2]/section[2]/div/div[2]/div[2]/div[1]/div/input")
            )).send_keys(title)

            # Courses button
            wait.until(EC.visibility_of_element_located(
                (By.XPATH, "/html/body/div[4]/div/div[2]/section[2]/div/div[2]/div[2]/div[3]/button")
            )).click()

            # Specific course
            time.sleep(1)
            wait.until(EC.visibility_of_element_located(
                (By.XPATH, "/html/body/div[5]/div/div[2]/section[2]/div[2]/div[2]")
            )).click()
            time.sleep(1)

            
            
            # First Add button
            wait.until(EC.visibility_of_element_located(
                (By.XPATH, "/html/body/div[5]/div/div[2]/section[3]/div[2]/button[2]")
            )).click()

            # Second Add button
            wait.until(EC.visibility_of_element_located(
                (By.XPATH, "/html/body/div[4]/div/div[2]/section[3]/div/button[2]")
            )).click()


            # Close dialog
            wait.until(EC.element_to_be_clickable(
                (By.XPATH, "/html/body/div[4]/div/div[2]/section[2]/div/div/button")
            )).click()
            
            time.sleep(1)
            # Move file after processing
            destination_file_path = os.path.join(destination_folder, file_name)
            shutil.move(full_file_path, destination_file_path)
            print(f"Moved {file_name} to {destination_folder}")

        except Exception as e:
            print(f"Error processing {file_name}: {e}")
            raise  # re-raise exception to trigger a restart

if __name__ == "__main__":

    while True:
        try:
            driver = start_driver()
            login(driver)
            process_files(driver, source_folder, archive_folder)
            driver.quit()
            break  # exit loop if processing completes successfully
        except Exception as ex:
            print(f"Exception encountered: {ex}. Restarting Chrome...")
            try:
                driver.quit()
            except Exception:
                pass
            time.sleep(5)  # Wait a moment before restarting