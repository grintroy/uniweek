from datetime import datetime as DT
from datetime import timedelta
import json, rumps

# Massive thanks to the author of this article:
# https://camillovisini.com/article/create-macos-menu-bar-app-pomodoro/

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

class DateRange:
	def __init__(self, start_date: DT, end_date: DT):
		self.start = start_date
		self.end = end_date

	def __contains__(self, date: DT):
		return self.start <= date < self.end + timedelta(days=1)

class Semester(DateRange):
	def __init__(self, name: str, start_date: DT, end_date: DT, holidays: list = []):
		super().__init__(start_date, end_date)
		self.name = name
		self.holidays = []
		self.weeks = []
		for sd, ed in holidays:
			self.add_holiday(sd, ed)
		self.update_weeks()

	def __contains__(self, date: DT):
		for h in self.holidays:
			if date in h:
				return False
		return self.start <= date < self.end + timedelta(days=1)

	def add_holiday(self, start_date: DT, end_date: DT) -> None:
		self.holidays.append(DateRange(start_date, end_date))

	def update_weeks(self) -> None:
		self.weeks = []
		dcount = self.start
		wc = 1
		while (dcount < self.end):
			ndcount = dcount + timedelta(days=7)
			if dcount in self:
				self.weeks.append(Week(self, wc, dcount, ndcount - timedelta(days=1)))
				wc += 1
			dcount = ndcount

class Week(DateRange):
	def __init__(self, s: Semester, n: int, start_date: DT, end_date: DT):
		super().__init__(start_date, end_date)
		self.s = s
		self.n = n


class Year():
	def __init__(self):
		self.semesters = []

	def add_semester(self, s: Semester) -> None:
		self.semesters.append(s)

	def search_week_by_date(self, date: DT) -> Week:
		for s in self.semesters:
			for w in s.weeks:
				if date in w:
					return w
		return None

	def search_date_by_week(self, sname: str, wknum: int, dnum: int) -> DT:
		try:
			s = [s for s in self.semesters if sname == s.name][0]
			w = [w for w in s.weeks if wknum == w.n][0]
		except IndexError:
			return None
		return w.start + timedelta(days=dnum - 1)


class UniWeek():
	def __init__(self):
		# Load semesters from JSON file into self.year
		self.year = Year()
		semesters = []
		with open("dates.json", "r") as f:
			semesters = json.load(f)["semesters"]
		for s in semesters:
			start_date = self.json_to_DT(s["start_date"])
			end_date = self.json_to_DT(s["end_date"])
			hdays = [(self.json_to_DT(h["start_date"]), self.json_to_DT(h["end_date"]))
                            for h in s["holidays"]]
			self.year.add_semester(Semester(s["name"], start_date, end_date, hdays))
		
		# Set up rumps app
		self.app = rumps.App("UniWeek", "")

		# Create input windows for user to enter semester name, week number and day number
		self.search_input_date = rumps.Window(title="Enter the semester name, week number and a day number (e.g. 2 for Tuesday) in a format NAME-WW-D", message="e.g. 'FALL-6-2'", cancel=True, dimensions=(300, 60))
		self.search_input_week = rumps.Window(title="Enter the date in a format DD-MM-YYYY", message="e.g. '16-1-2023'", cancel=True, dimensions=(300, 60))

		# Create two menu items: one to search for a date, and one to search for a week
		self.search_date = rumps.MenuItem("Search for a date", callback=self.run_search_date_by_week)
		self.search_week = rumps.MenuItem("Search for a week", callback=self.run_search_week_by_date)
		self.app.menu = [self.search_date, self.search_week]

		# Schedule self update to run every 5 minutes
		self.timer = rumps.Timer(self.update, 300)
		self.timer.start()
	
	def run_search_date_by_week(self, _):
		response = self.search_input_date.run()
		if not response.clicked:
			return
		input = response.text.strip()
		try:
			s, w, d = [i for i in input.split("-")]
			w, d = int(w), int(d)
			date = self.year.search_date_by_week(s, w, d)
		except ValueError:
			rumps.alert("Invalid formatting")
			return
		if date:
			rumps.alert(f"{date.day}-{date.month}-{date.year}")
		else:
			rumps.alert("BREAK")

	def run_search_week_by_date(self, _):
		response = self.search_input_week.run()
		if not response.clicked:
			return
		input = response.text.strip()
		try:
			d, m, y = [int(i) for i in input.split("-")]
			date = DT(day=d, month=m, year=y)
		except ValueError:
			rumps.alert("Invalid formatting")
			return
		week = self.year.search_week_by_date(date)
		if week:
			rumps.alert(f"{week.s.name} W{week.n}")
		else:
			rumps.alert("BREAK")

	def json_to_DT(self, json_dt: list) -> DT:
		sd, sm, sy = json_dt
		return DT(day=sd, month=sm, year=sy)

	def get_week(self):
		today = DT.today()
		this_week = self.year.search_week_by_date(today)
		if this_week:
			return f"{this_week.s.name} W{this_week.n}"
	
	def run(self):
		self.app.run()
	
	def update(self, _):
		self.app.title = self.get_week()

if __name__ == '__main__':
	app = UniWeek()
	app.run()