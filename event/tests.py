from django import test
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from django.contrib.auth.models import User


class LoginTest(test.LiveServerTestCase):

    def setUp(self):
        self.selenium = webdriver.Chrome("/usr/local/chromedriver")
        User.objects.create_user('Cuser', 'c@c.com', 'c')

    def tearDown(self):
        self.selenium.quit()

    def test_login(self):
        usernames = ["Cuser", "Cuser", "Auser", "", "Cuser"]
        passwords = ["c", "d", "c", "c", ""]

        for usr, pwd in zip(usernames, passwords):
            self.selenium.get("%s%s" % (self.live_server_url, "/login_user/"))
            username = self.selenium.find_element_by_id("id_username")
            password = self.selenium.find_element_by_id("id_password")
            submit = self.selenium.find_element_by_id("id_submit")
            username.clear()
            password.clear()
            username.send_keys(usr)
            password.send_keys(pwd)
            submit.send_keys(Keys.RETURN)

            try:
                profile = self.selenium.find_element_by_id("id_profile").text
                self.assertEqual("Profile", profile, "Login successful")
            except NoSuchElementException:
                print("Login unsuccessful! ")
                print("Username: " + usr)
                print("Password: " + pwd)

        print("End of login testing")
