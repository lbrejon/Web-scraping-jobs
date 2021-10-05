# Jobs-scrapping
Implementation of jobs recommendation algorithm by web scrapping

## Table of contents 📝
* [My goals](#my-goals)
* [Acquired skills](#acquired-skills)
* [Technologies](#technologies)
* [Project composition](#project-composition)
* [Description](#description)
* [Launch the program](#launch-the-program)
* [Sources](#sources)

Estimated reading time : ⏱️ 5min

## My goals 🎯
- Find an internship for my final year as student (equivalent to Master degree) in Data Science in Europe (5-6 months from February 2022)
- Learn how to gather information (by web scraping) to build a dataset 
- Build and deploy a web app with Flask

## Acquired skills :zap:
- Web scrapping methods
- Manipulation of Jinja templates

## Technologies 🖥️
Programming languages:
```bash
- Python (framework pytorch)
```

Librairies:
```bash
- pandas
- requests
- bs4 (BeautifulSoup)
```


## Project composition 📂
```bash
.
├── README.md
│
├── data
│   ├── raw
│   │   └── geoId.csv
│   │
│   ├── processed
│   │   └── geoId.csv
│   │
│   └── jobs.csv
│
└── notebooks
    └── scrapping_jobs.ipynb
```

## Description 📋 
This project aims to **find best job offers for you by web scrapping**. As a reminder, **web scraping is the process of gathering information from the Internet, most of the time automatically**. Just to make sure you understand the the scope of this process, scraping a page respectfully for educational purposes is not a problem since the information is publically available.

- I choosen to use **BeautifulSoup** librairy because it's an easy one for beginners (for other librairies, see Selenium, lxml, Scrapy..). BeautifulSoup is a Python library for parsing structured data (```soup = BeautifulSoup(page.content, "html.parser")```). It allows you to interact with HTML in a similar way to how you interact with a web page using developer tools. Indeed, an HTML web page is structured by **tags** making elements search simple: 
    - find elements by class name: ```element1 = soup.find_all("<tag>", class_="<class>")```
    - find elements by id: ```element2 = soup.find_all("<tag>", id_="<id>")```
    - find elements by text content: ```element3 = soup.find_all("<tag>", string="<string>")```

- **Scrapping** and **parsing data process** enables to gather information about job offers: 'Title', 'Company', 'Company_type', 'Company_sector', 'Country', 'City', 'Summary, 'Date', 'Job_id' and 'Job_url'. The job recommendation algorithm can process **several websites**, **countries**, **cities** and **pages**.\
For *LinkedIn* website, the parameter geoId was required to scrap data. Information about geoId came from this *[website](https://help4access.com/no-more-secrets/)* and raw data was saved into ```data/raw/geoId.csv```, then cleaned and saved data in ```data/processed/geoId.csv```.

- The **jobs recommendation algorithm** takes in argument a dictionary with information about the user request: **jobs_parameters**.
``` bash
jobs_parameters = {
    # Job request
    'website': ['indeed', 'linkedin'],
    'query': 'Data Scientist',
    'location': ['Geneva', 'Paris', 'Brussels', 'Amsterdam'],
    'distance': 10,
    'description_keywords_ordered': ['Data Science', 'Deep Learning', 'Machine Learning', 'AWS', 'Data', 'Python', 'SQL','Analysis', 'Modelling'],
    'description_keywords_excluded': ['Headhunter', 'Manager', 'Director', 'Senior'],
    'title_keywords_must': ['Data'],
    'title_keywords_excluded': ['Manager', 'Director', 'Senior', 'Head', 'Freelance', 'Engineer', 'Experienced'],
    'pages': 20,
    
    # Preferences
    'title_keywords_ordered': ['Junior', 'Data Scientist', 'Internship', 'Data Science', 'DataScientist', 'DataScience'],
    'company_size_type': {'Large Enterprise (+5000 employees)':True,
                    'Intermediate-sized Enterprise (251-5000 employees)':False,
                    'Medium-sized Enterprise (51-250 employees)':False,
                    'Small-sized Enterprise (11-50 employees)':False,
                    'Startup (1-10 employees)':False
                    }
}
```      


- It is possible that **LinkedIn blocked your access while scrapping the website**. You'll get the error mentioned below. Indeed you can only access a LinkedIn profile if you are logged in and when LinkedIn receives a request, it looks for a specific cookie called **li_at** in the request. If it does not find this cookie, it redirects the requester to a page with the JavaScript you had. This JavaScript serves to redirect you to the login page. That's what all the ```window.location.href=<thing>``` is about. You juste have to add the li_at cookie value: ```request = requests.get('https://www.linkedin.com/in/<your_profile>/', headers={'cookie': 'li_at=<cookie_li_at_value>'})```. You "**fake**" a logged-in request by going to LinkedIn, copying your own li_at cookie, and adding that to your request. Note that this will only work temporarily: at some point LinkedIn will expect that cookie to change, and **you will have to re-copy it**.
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
```
IN PROGRESS
```

## Sources ⚙️
- Inspired by the work of *John Watson Rooney* with his [YouTube video](How to Web Scrape Indeed with Python - Extract Job Information to CSV).
- Thanks to *RobertAKARobin* for his solution to solve LinkedIn access blocking on [Stack Overflow](https://stackoverflow.com/questions/53749379/download-a-linkedin-page).
