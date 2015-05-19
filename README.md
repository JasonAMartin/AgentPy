AgentPy
============

This is a Python class I created so that I could do some tasks for work and fun.

For work, I wanted a way to hit our whole site (1000s of pages) to verify my work before sending it off to QA.

The main reason this is here is in case someone wants to use it or learn from it. 

On the "front end" I have another python script that has a full user menu, utilizes all the functions here, and so forth, but that script isn't GitHub since it was for work only.

** May 18, 2015 - I'll be creating a "worker" script and uploading it to this repo soon.

##Requirements:

([BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/))

##Example Usage:

```python
import WebBot.WebBot #Your import may differ depending on your setup

worker = WebBot.WebBot.WebWorker(options_here)

worker.task_check_tags(True, 'link', 'alternative', 'rel', site_type, 1)
```

###Additional Information:

I wrote this for Python 3. 

The general idea is to keep building this out to support all my web scraping needs.