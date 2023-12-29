import time, os, json

from ics import Calendar, Event
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless=new")

USER_ID = "user_id"
PASSWORD = "password"


class HopeCalendar:
    def __init__(self, user_id, password):
        self.user_id = user_id
        self.password = password

        print(self.user_id, self.password)

        self.user_type = "student"
        self.start_date = time.strftime("%Y-01-01")
        # self.end_date = time.strftime("%Y-12-31")
        self.end_date = "2024-12-31"
        self.destination_url = f"https://my.hope.ac.uk/myhope/public/index.php/Main/timetable_json?user_id={self.user_id}&user_type={self.user_type}&start={self.start_date}&end={self.end_date}"

        print(self.destination_url)
        self.timetable_json = self.get_calendar()
        print(self.timetable_json)
        self.current_date = time.strftime("%Y-%m-%d")

    def __login(self):
        driver = webdriver.Chrome(options=options)
        driver.get(self.destination_url)

        user_id_input = driver.find_element(By.ID, "username")
        user_id_input.send_keys(self.user_id)
        password_input = driver.find_element(By.ID, "password")
        password_input.send_keys(self.password)

        login_button = driver.find_element(By.NAME, "submit")
        login_button.click()

        return driver

    def get_calendar(self):
        driver = self.__login()
        driver.get(self.destination_url)
        body = driver.find_element(By.TAG_NAME, "body")

        return json.loads(body.text)

    def convert_ics(self):
        timetable = self.timetable_json
        timetable_ics = Calendar()

        for event in timetable:
            print(event["StartTime"], event["EndTime"])
            
            ics_event = Event(
                name=f"{event['module']} - {event['module_title']}",
                begin=event["start"].replace("T", " "),
                end=event["end"].replace("T", " "),
                created=self.current_date,
                last_modified=self.current_date,
            )
            
            timetable_ics.events.add(ics_event)
        return timetable_ics


c = HopeCalendar(USER_ID, PASSWORD)
ics_calendar = c.convert_ics()

with open("timetable.ics", "w") as f:
    f.writelines(ics_calendar.serialize_iter())

