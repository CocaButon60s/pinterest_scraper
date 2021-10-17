from genericpath import exists
import os, signal
from traceback import format_exc
from selenium.webdriver import Chrome
from selenium.webdriver.chrome import service as cs
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep
import requests
from shutil import rmtree
from pickle import dump, load
from sys import argv

class ImgCapture:
	"""pinterestの画像収集
	"""
	def __init__(self, url):
		options = Options()
		options.add_argument('--user-data-dir=' + os.environ['USER_DATA_DIR'])
		options.add_argument('--profile-directory' + os.environ['PROFILE_DIRECTORY'])
		# options.add_argument('--headless')
		# options.add_argument('--start-maximized')
		# options.add_argument('--window-size=1920,1080')
		options.add_experimental_option('excludeSwitches', ['enable-logging'])
		options.use_chromium = True
		chrome_service = cs.Service(executable_path=ChromeDriverManager().install())
		self.browser = Chrome(service=chrome_service, options=options)
		self.browser.implicitly_wait(15)
		self.url_logs = []
		self.browser.get(url)
		self.cnt = 0

	def searchKeyword(self, keyword):
		search = self.browser.find_element(by=By.TAG_NAME, value='input')
		search.send_keys(keyword)
		search.send_keys(Keys.ENTER)

	def saveImg(self, max, dst):
		self.max = max
		self.dst = dst
		while not self.__getImg():
			self.__scroll()

	def __getImg(self):
		sleep(10)
		imgs = self.browser.find_elements(by=By.CSS_SELECTOR, value='div.vbI.XiG img')
		is_not_change = True
		for img in imgs:
			url = img.get_attribute('src')
			if url in self.url_logs:
				continue
			is_not_change = False
			self.url_logs.append(url)
			res = requests.get(url)
			with open(self.dst + "{}.jpg".format(self.cnt), "wb") as f:
				f.write(res.content)
				self.cnt += 1
			if self.cnt >= self.max:
				return True
			sleep(1)
		return is_not_change

	def __scroll(self):
		self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	
	def __del__(self):
		self.browser.quit()

def main():
	global capture
	dst = argv[1]
	os.makedirs(dst, exist_ok=True)
	capture = ImgCapture('https://www.pinterest.jp/')

	capture.searchKeyword(argv[2])
	capture.saveImg(5000, dst)

if __name__ == '__main__':
	if len(argv) < 3:
		print('command line param error')
		exit()
	try:
		main()
		print("SUCCESS!!!")
	except Exception as e:
		print("error:" + e.args[0])
		print(format_exc())
	del capture