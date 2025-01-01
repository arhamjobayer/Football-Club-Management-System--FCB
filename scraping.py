from bs4 import BeautifulSoup
import requests
import re

html_text = requests.get('https://www.fcbarcelona.com/en/football/first-team/schedule').text
soup = BeautifulSoup(html_text, 'lxml')
team1s = soup.find_all('div', class_=re.compile(("^fixture-info__name--home")))
team2s = soup.find_all('div', class_=re.compile(("^fixture-info__name--away")))
dates = soup.find_all('div', class_=re.compile(("^fixture-result-list__fixture-date")))
times = soup.find_all('div', class_=re.compile(("^fixture-info__time")))
stadiums = soup.find_all('div', class_=re.compile(("^fixture-result-list__stage-location")))

for team1, team2, date, time, stadium in zip(team1s, team2s, dates, times, stadiums):
    print(team1.text)
    print(team2.text)
    print(time.text)
    print(date.text)
    print(stadium.text)