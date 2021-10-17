from genericpath import exists
import os, signal
from selenium.webdriver import Chrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from time import sleep
import requests
from shutil import rmtree

class ImgCapture:
	"""pinterestの画像収集
	"""
	def __init__(self, url):
		options = Options()
		print(options)
		options.add_argument('--user-data-dir=' + os.environ['USER_DATA_DIR'])
		options.add_argument('--profile-directory' + os.environ['PROFILE_DIRECTORY'])
		options.add_experimental_option('excludeSwitches', ['enable-logging'])
		options.use_chromium = True
		self.browser = Chrome(ChromeDriverManager().install(), options=options)
		self.browser.get(url)
		self.url_logs = []
		self.cnt = 0

	def searchKeyword(self, keyword):
		search = self.browser.find_element_by_tag_name('input')
		search.send_keys(keyword)
		search.send_keys(Keys.ENTER)
		sleep(5)

	def saveImg(self, max, dst):
		self.max = max
		self.dst = dst
		while not self.__getImg():
			self.__scroll()

	def __getImg(self):
		imgs = self.browser.find_elements_by_css_selector('div.vbI.XiG img')
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
		sleep(5)
	
	def __del__(self):
		self.browser.quit()

def main():
	dst = 'imgs/'
	if exists(dst):
		rmtree(dst)
	os.makedirs(dst)
	capture = ImgCapture('https://www.pinterest.jp/')

	capture.searchKeyword('search_keyword')
	capture.saveImg(100, dst)
	del capture

if __name__ == '__main__':
	try:
		main()
	except Exception as e:
		print("error:" + e.args[0])