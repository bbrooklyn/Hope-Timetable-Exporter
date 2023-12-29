import time, os, json

from ics import Calendar, Event

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless=new")

# load credentials file from credentials.json
credentials = json.load(open("credentials.json", "r"))
USER_ID = credentials["user_id"]
PASSWORD = credentials["password"]

class HopeCalendar:
    def __init__(self, user_id, password):
        self.user_id = user_id
        self.password = password
        self.user_type = "student"
        self.start_date = time.strftime("%Y-01-01")
        self.end_date = "2024-12-31" # End of the academic year
        self.destination_url = f"https://my.hope.ac.uk/myhope/public/index.php/Main/timetable_json?user_id={self.user_id}&user_type={self.user_type}&start={self.start_date}&end={self.end_date}"
        try:
            self.timetable_json = self.fetch_calendar()
        except Exception as e:
            print(e)
            self.timetable_json = []
            print("Unable to fetch calendar")
            
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

    def fetch_calendar(self):
        driver = self.__login()
        driver.get(self.destination_url)
        body = driver.find_element(By.TAG_NAME, "body")
        return json.loads(body.text)

    def convert_ics(self):
        try:
            timetable = self.timetable_json
            timetable_ics = Calendar()
            for event in timetable:
                description = f"Staff: {event['description']}\nRoom: {event['room']}"
                ics_event = Event(
                    name=f"{event['module']} - {event['module_title']}",
                    begin=event["start"].replace("T", " "),
                    end=event["end"].replace("T", " "),
                    created=self.current_date,
                    location=event["room"],
                    description=description,
                    last_modified=self.current_date,
                    categories=[event["module"]],
                    url="https://live.moodle.hope.ac.uk/my/courses.php"
                )
                timetable_ics.events.add(ics_event)
            print("Successfully converted calendar to ics")
            return timetable_ics
        except Exception as e:
            print(e)
            print("Error converting calendar to ics")
            return None

c = HopeCalendar(USER_ID, PASSWORD)
ics_calendar = c.convert_ics()

with open("timetable.ics", "w") as f:
    f.writelines(ics_calendar.serialize_iter())
print("Successfully saved calendar to timetable.ics")

