# Web-scraping-jobs
Implementation of jobs recommendation algorithm by web scraping

https://user-images.githubusercontent.com/56866008/136713739-fb332ca9-5151-4481-b373-3531a43a8dae.mp4

## Table of contents 📝
* [My goals](#my-goals)
* [Acquired skills](#acquired-skills)
* [Technologies](#technologies)
* [Project composition](#project-composition)
* [Description](#description)
* [Help](#help)
* [Launch the program](#launch-the-program)
* [Sources](#sources)

Estimated reading time : ⏱️ 5min

## My goals 🎯
- Find an internship for my final year as student (equivalent to Master degree) in Data Science in Europe (5-6 months from February 2022)
- Learn how to gather information (by web scraping) to build a dataset 
- Build a web app with Flask

## Acquired skills :zap:
- Web scraping methods
- HTTP methods ('GET' and 'POST') + HTML/CSS review for the Flask implementation
- Concepts of Jinja templates
- Handle with SQLAlchemy

## Technologies 🖥️
Programming languages:
```bash
- Python (framework PyTorch)
```

Librairies:
```bash
- pandas
- requests
- geopy
- bs4 (BeautifulSoup)
- flask
- sqlalchemy
```

## Project composition 📂
```bash
.
├── README.md
│
├── app
│   │
│   ├── static
│   │   ├── css
│   │   │   └── main.css
│   │   │ 
│   │   ├── img  
│   │   │   └── logo.svg
│   │   │
│   │   └── phocacssflagswidthphoca-flags.css
│   │       ├── phoca-flags.css
│   │       │
│   │       └── style.css
│   │   
│   ├── templates
│   │   └── base.html
│   │
│   ├── app.py
│   │
│   └── requirements.txt
│
├── data
│   ├── raw
│   │   └── geoId.csv
│   │
│   ├── processed
│   │   └── geoId.csv
│   │
│   ├── jobs.csv
│   │
│   ├── jobs.json
│   │
│   └── jobs_parameters_user_request.json
│
└── notebooks
    ├── scraping_jobs.ipynb
    │
    └── scraping_jobs.py
```

## Description 📋 
This project aims to **find best job offers for you by web scrapping**. As a reminder, **web scraping is the process of gathering information from the Internet, most of the time automatically**. Just to make sure you understand the the scope of this process, scraping a page respectfully for educational purposes is not a problem since the information is publically available. User job request is sent (GET/POST) and saved as json file ```data/jobs_parameters_user_request.json```, then the ```notebooks/scraping_jobs.py``` taking in argument this json file, scrapes both websites (Indeed/LinkedIn). After data processing, user can either visualize results throught csv file ```data/jobs.csv``` or throught the wep app. The latter offer to the user to rank job offers by rating, alphabetical criteria.

- I choosen to use **BeautifulSoup** librairy because it's an easy one for beginners (for other librairies, see Selenium, lxml, Scrapy..). BeautifulSoup is a Python library for parsing structured data (```soup = BeautifulSoup(page.content, "html.parser")```). It allows you to interact with HTML in a similar way to how you interact with a web page using developer tools. Indeed, an HTML web page is structured by **tags** making elements search simple: 
    - find elements by class name: ```element1 = soup.find_all("<tag>", class_="<class>")```
    - find elements by id: ```element2 = soup.find_all("<tag>", id_="<id>")```
    - find elements by text content: ```element3 = soup.find_all("<tag>", string="<string>")```

- **Scrapping** and **parsing data process** enables to gather information about job offers: 'Title', 'Company', 'Company_type', 'Company_sector', 'Country', 'City', 'Summary, 'Date', 'Job_id' and 'Job_url'. The job recommendation algorithm can process **several websites**, **countries**, **cities** and **pages**.\
For *LinkedIn* website, the parameter geoId was required to scrap data. Information about geoId came from this *[website](https://help4access.com/no-more-secrets/)* and raw data was saved into ```data/raw/geoId.csv```, then cleaned and saved data in ```data/processed/geoId.csv```.

- The **jobs recommendation algorithm** takes in argument a dictionary with information about the user request: **jobs_parameters**. The fieds **Query** and **City** are mandatory to search jobs. By default:
    - Website: Indeed
    - Distance from the city: 0
    - Required keywords (in title): None
    - Excluded keywords (in title): None
    - Preferred keywords (in title): None
    - Number of pages: 3
    - Company size type: all company size type are considered (from 'Large' to 'Startup')

<p align="center">
  <kbd>
  <img width=1000 src="https://user-images.githubusercontent.com/56866008/136706114-b53fb869-7b16-4a1d-b52b-b90e17ce4d2a.jpg"><br>
  </kbd>
</p>

- As regarding the content, several information is displayed to the user:
    - **ID**: Integer, the job id in the table
    - **JOB RATING**: Integer, job rating computed by keywords (preferred keywords in title) and company-sized type
    - **WEBSITE**: String, name of websites used
    - **TITLE**: String, job offer title 
    - **COMPANY**: String, indicates the name of the company
    - **COMPANY TYPE**: String, company-sized type (Large, Intermediate, Medium, Small or Startup)
    - **COMPANY SECTOR**: company sector 
    - **COUNTRY**: String, company location (country)
    - **CITY**: String, company location (city)
    - **JOB SUMMARY**: String, summary of the job offer
    - **DATE**: String, date of publication of the job offer (from <1 day to 30 days)
    - **JOB URL**: String, link to the job offer

- Initially **jobs are ranked by their 'job_rating'** which is computed by preference criteria: **Preferred keywords (in title)** and **Company size type**. If the job offer come from a selected company size type or if the job offer's title contains the word in the preferred keywords, **the job_rating score increases by one as many times as title has preferred keywords**.\
\
For example, assuming that a user make a request with ```Preferred keywords (in title): Junior;Data Scientist``` and ```Company size type: Large-sized Entreprise (+5000 employees)```, the job offer below has a **job_rating=3** because the title *Junior Data Scientist / Artificial Intelligence Consultant* contains two preferred keywords and the company *DELOITTE* type is a Large-sized Entreprise.

<p align="center">
  <kbd>
  <img width=1000 src="https://user-images.githubusercontent.com/56866008/136706327-86e60f96-3b9f-424a-ba3d-2a71bef756ee.png"><br>
  </kbd>
</p>

- You can also rank jobs by others criteria such as **ID**, **Company**, **Company type**, **Company sector**, **Country**, **City** and **Date** with ranking buttons (jobs are sorted by alphabetical order [A-Z] and descending number [9-0].

## Help 🔑
It is possible that **LinkedIn blocked your access while scrapping the website**. You'll get the error mentioned below. Indeed you can only access a LinkedIn profile if you are logged in and when LinkedIn receives a request, it looks for a specific cookie called **li_at** in the request. If it does not find this cookie, it redirects the requester to a page with the JavaScript you had. This JavaScript serves to redirect you to the login page. That's what all the ```window.location.href=<thing>``` is about. You juste have to add the li_at cookie value: ```headers={'cookie': 'li_at=<cookie_li_at_value>'})```. By doing this, you "**fake**" a logged-in request by going to LinkedIn, copying your own li_at cookie, and adding that to your request. Note that this will only work temporarily: at some point LinkedIn will expect that cookie to change, and **you will have to re-copy it**.

``` bash
<html><head>
<script type="text/javascript">
window.onload = function() {
  // Parse the tracking code from cookies.
  var trk = "bf";
  var trkInfo = "bf";
  var cookies = document.cookie.split("; ");
  for (var i = 0; i < cookies.length; ++i) {
    if ((cookies[i].indexOf("trkCode=") == 0) && (cookies[i].length > 8)) {
      trk = cookies[i].substring(8);
    }
    else if ((cookies[i].indexOf("trkInfo=") == 0) && (cookies[i].length > 8)) {
      trkInfo = cookies[i].substring(8);
    }
  }

  if (window.location.protocol == "http:") {
    // If "sl" cookie is set, redirect to https.
    for (var i = 0; i < cookies.length; ++i) {
      if ((cookies[i].indexOf("sl=") == 0) && (cookies[i].length > 3)) {
        window.location.href = "https:" + window.location.href.substring(window.location.protocol.length);
        return;
      }
    }
  }

  // Get the new domain. For international domains such as
  // fr.linkedin.com, we convert it to www.linkedin.com
  var domain = "www.linkedin.com";
  if (domain != location.host) {
    var subdomainIndex = location.host.indexOf(".linkedin");
    if (subdomainIndex != -1) {
      domain = "www" + location.host.substring(subdomainIndex);
    }
  }

  window.location.href = "https://" + domain + "/authwall?trk=" + trk + "&trkInfo=" + trkInfo +
      "&originalReferer=" + document.referrer.substr(0, 200) +
      "&sessionRedirect=" + encodeURIComponent(window.location.href);
}
</script>
</head></html>
``` 

## Launch the program ▶️
Create project with a virtual environment (in 'app' folder)
```
$ mkdir myproject
$ cd myproject
$ python3 -m venv flask
```
Activate it (virtual environment's name is flask)
```
$ source flask/bin/activate
```
Install requirements
```
$ pip install -r requirements.txt
```
Set environment variables in terminal (in order to not rerun code after modifications)
```
$ export FLASK_APP=app.py
$ export FLASK_ENV=development
```
Run the app
```
$ flask run
```


## Sources ⚙️
- Inspired by the work of *John Watson Rooney* with his YouTube video [How to Web Scrape Indeed with Python - Extract Job Information to CSV](https://www.youtube.com/watch?v=PPcgtx0sI2E&t=146s) for **web scrapping methods**.
- Inspired by the work of *Python Engineer* with his YouTube video [Python Flask Beginner Tutorial - Todo App - Crash Course](https://www.youtube.com/watch?v=yKHJsLUENl0) for **Flask app implementation**. 
- Help with **Flask installation** [here](https://flask.palletsprojects.com/en/2.0.x/installation/).
- Help with **Jinja2 Templates and Forms** [here](https://www.codecademy.com/learn/learn-flask/modules/flask-templates-and-forms/cheatsheet).
<!-- - Help with **Web App deployment on Heroku** [here](https://www.heroku.com/) and [here](https://devcenter.heroku.com/articles/heroku-cli). -->
- Thanks to *RobertAKARobin* for his solution to **solve LinkedIn access blocking** on [Stack Overflow](https://stackoverflow.com/questions/53749379/download-a-linkedin-page).
