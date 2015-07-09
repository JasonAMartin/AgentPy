AgentPy
============

I created AgentPy to support my site checking/scraping needs. Additionally, my work started using the library, so I wrote a front-end for it for work and continued to develop this library out.

For work, AgentPy is used to grab and process 1000s of files to help us save QA team time, to be alerted of publishing errors and to keep on top of a large site.

The main reason this is here is in case someone wants to use it or learn from it. 

On the "front end" I have another python script that has a full user menu, utilizes all the functions here, and so forth, but that script isn't GitHub since it was for work only.

** At some point, I'll be putting up a basic version example of the front-end script I use at work for AgentPy.

##Requirements:

([BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/))

##Example Usage:

```python
import AgentPy.AgentPy #Your import may differ depending on your setup

worker = AgentPy.AgentPy.WebWorker(options_here)

worker.task_check_tags(True, 'link', 'alternative', 'rel', site_type, 1)
```

###Additional Information:

I wrote this for Python 3. 

The general idea is to keep building this out to support all my web scraping needs.
