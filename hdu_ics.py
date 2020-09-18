from HDUCal.gain_schedule import GainSchedule
from HDUCal.schedule2ics import Schedule2ICS
from HDUCal import info

if __name__ == "__main__":
    raw_schedule = GainSchedule(info.account, info.password).run()
    result = Schedule2ICS(raw_schedule).run(info.semester_start)
