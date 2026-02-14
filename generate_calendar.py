import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

BASE_URL = "https://oktagonmma.com"

def get_events():
    url = f"{BASE_URL}/events"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    events = []
    
    for event in soup.select("a.c-card-event"):
        event_url = BASE_URL + event.get("href")
        event_title = event.select_one(".c-card-event__title").text.strip()
        event_date = event.select_one(".c-card-event__date").text.strip()
        
        events.append({
            "title": event_title,
            "date": event_date,
            "url": event_url
        })
    
    return events


def get_fightcard(event_url):
    response = requests.get(event_url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    fights = []
    
    for fight in soup.select(".c-fight-card__item"):
        fighter1 = fight.select_one(".c-fight-card__name--red")
        fighter2 = fight.select_one(".c-fight-card__name--blue")
        
        if fighter1 and fighter2:
            fights.append(f"{fighter1.text.strip()} vs {fighter2.text.strip()}")
    
    return fights


def create_ics(events):
    tz = pytz.timezone("Europe/Berlin")
    now = datetime.now(tz).strftime("%Y%m%dT%H%M%S")
    
    ics_content = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Oktagon Kalender//EN\n"
    
    for event in events:
        try:
            event_date = datetime.strptime(event["date"], "%d.%m.%Y")
            event_date = tz.localize(event_date)
            
            fights = get_fightcard(event["url"])
            description = "\\n".join(fights)
            
            ics_content += f"""BEGIN:VEVENT
UID:{event["title"]}-{event_date.strftime('%Y%m%d')}
DTSTAMP:{now}
DTSTART:{event_date.strftime('%Y%m%dT190000')}
SUMMARY:{event["title"]}
DESCRIPTION:{description}
END:VEVENT
"""
        except:
            continue
    
    ics_content += "END:VCALENDAR"
    
    with open("oktagon_kalender.ics", "w", encoding="utf-8") as f:
        f.write(ics_content)


if __name__ == "__main__":
    events = get_events()
    create_ics(events)
