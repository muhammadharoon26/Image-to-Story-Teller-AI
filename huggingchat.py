import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait  #..............
from selenium.webdriver.support import expected_conditions as EC    #................
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import os
import time


class HuggingChatScraperBot:
    def __init__(self, headless_mode=False) -> None:
        self.headless_mode = headless_mode
        self.driver = self.gen_driver()
        self.prompt = ""
        self.response_list = []

    def gen_driver(self):
        try:
            chrome_options = uc.ChromeOptions()
            if self.headless_mode:
                # chrome_options.headless = True
                chrome_options.add_argument('--headless=new')
            driver = uc.Chrome(options=chrome_options)
            return driver
        except Exception as e:
            print("Error in Driver: ",e)

    def prosecutor(self, prompt):
        self.driver.get("https://huggingface.co/chat/")
        self.prompt = prompt
        print("Prompt: {}".format(self.prompt))

        self.enter_prompt()
        
        text_response = self.get_response()

        self.response_list.extend([self.prompt, text_response, self.prompt+text_response])

        self.driver.quit()

        return self.response_list

    def enter_prompt(self):
        # Send Keys
        self.send_keys_manager(
            "Entered Text", 
            '//*[@id="app"]/div[1]/div/div[2]/form/div/div/textarea',
            self.prompt
            )
        # Click on Send Prompt Button
        self.click_manager(
            "Enter Text BTN",
            '//*[@id="app"]/div[1]/div/div[2]/form/div/button'
        )

    def get_response(self):
        text_response = self.get_text_manager(
            "Get Text",
            '//*[@id="app"]/div[1]/nav[3]/div[2]/a[1]/div',
            '//*[@id="app"]/div[1]/div/div[1]/div/div[2]/div[1]/div'
        )
        return text_response

    def wait_manager(self, identifier, t, mode=By.XPATH):
        i = 1
        while True:
            try:
                # WebDriverWait(self.driver, t).until(EC.visibility_of_element_located((By.CLASS_NAME, identifier)))
                element = self.driver.find_element(mode, identifier)
                if element:
                    print("[{}]Wait Manager [Success]: Element Detected no need to wait for {} seconds".format(i,t))
                    break
                else:
                    print("[{}]Wait Manager [Active]: Element not Detected! Waiting for {} seconds".format(i,t))
                    time.sleep(t)
                # WebDriverWait(self.driver, t).until(EC.presence_of_element_located((By.CSS_SELECTOR, identifier)))
            except Exception as e:
                print("[{}]Wait Manager [Error]: {}\nNow waiting for {} seconds!".format(i,str(e).split('\n')[0],t))
                time.sleep(t)
            i+=1

    def click_manager(self, name, identifier, mode=By.XPATH):
        t = 3
        i=1
        while True:
            try:
                self.driver.find_element(mode, identifier).click()
                print("[{}]Click Manager [Success]: {} clicked successfully!".format(i,name))
                break
            except Exception as e:
                print("[{}]Click Manager [Error]:{}\n[{}]Click Manager [Active]: Activating Wait Manager".format(i,str(e).split('\n')[0],i))
                # time.sleep(t)
                self.wait_manager(identifier, t, mode)
            i+=1

    def get_text_manager(self, name, tag_identifier, text_identifier, mode=By.XPATH):
        t = 3
        i=1
        while True:
            try:
                generated_text = self.driver.find_element(mode, text_identifier).text
                chat_tag = self.driver.find_element(mode, tag_identifier).text
                if chat_tag.find("Untitled") == -1:
                    print("[{}]Get Text Manager [Success]: {} content generated successfully!".format(i,name))
                    break
                else:
                    print("[{}]Get Text Manager [Waiting]: {} waiting for content generation".format(i,name))
            except Exception as e:
                print("[{}]Get Text Manager [Error]:{}\n[{}]Get Text Manager [Active]: Activating Wait Manager".format(i,str(e).split('\n')[0],i))
                # time.sleep(t)
                self.wait_manager(text_identifier, t, mode)
            i+=1
        return generated_text

    def send_keys_manager(self, name, identifier, keys, mode=By.XPATH):
        t = 3
        i=1
        while True:
            try:
                for part in keys.split('\n'):
                    self.driver.find_element(mode, identifier).send_keys(part)
                    ActionChains(self.driver).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.ENTER).perform()
                print("[{}]Send Keys Manager [Success]: {} keys sent successfully!".format(i,name))
                break
            except Exception as e:
                print("[{}]Send Keys Manager [Error]:{}\n[{}]Send Keys Manager [Active]: Activating Wait Manager".format(i,str(e).split('\n')[0],i))
                self.wait_manager(identifier, t, mode)
            i+=1


if __name__ == '__main__':
    scenario = "two bulls fighiting each other"
    agent = HuggingChatScraperBot(headless_mode=True)
    response = agent.prosecutor([scenario,scenario])
    print(response[2])
    os.system("pause")
    