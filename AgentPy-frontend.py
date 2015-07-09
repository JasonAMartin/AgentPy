"""
     This script uses AgentPy, which is open-source code located here:
     http://www.github.com/jasonamartin/AgentPy

     This is a front-end example. It's barebones and stripped down from what I normally use. This version takes argument flags, which is something work wanted for scheduling AgentPy on the server.
     At home, I was using a front-end with a menu-based system I created at first, but I ended up replacing it with command line flags.

     If you were using this front-end, you might run it by issuing the following command:
     $ python vdcBot.py --env=http://www.mysite.com --task=1 --sitetype=mobile --report=SomeReportName --reporttime=False --sitemap=http://www.mysite.com/sitemap.xml --filter=http://www.mysite.com/blah.do?funzone

"""

import AgentPy.AgentPyTasks
import argparse
from time import strftime

parser = argparse.ArgumentParser(description='Front-end interface for Agent Py')

# possible args to pass via command line
parser.add_argument("--env", required=True, help="The url main URL for this test.")
parser.add_argument("--task", required=True, help="The task you want to perform")
parser.add_argument("--filter", help="The URLs you want to filter, space separated and no spacing")
parser.add_argument("--sitemap", help="The URL to the sitemap for the task.")
parser.add_argument("--sitetype", help="wired or mobile", required=True)
parser.add_argument("--report", help="File path & name for the report -- no extensions", required=True)
parser.add_argument("--reporttime", help="If you want the report time to be appended to the report file name, which will add something like -2015-07-07-10:14:33 to the file name.", default=False)
parser.add_argument("--silent", help="If you want to squash most of the printout from the program.", default=False)

# parse args for list of sites and put into array
def parse_filter_urls(list):
    new_list = [x.strip() for x in list.split(',')]
    return new_list

# parsing the arguments
args = parser.parse_args()

# setting variables
worker_environment = args.env
worker_task = args.task
sitemap = args.sitemap
site_type = args.sitetype
reporting_file = args.report

# checking if filter is passed. If not, setting it to empty array
# example filters for --filter
# http://www.site.com/?blah,http://www.blah.com/something.do?restaurantId

if args.filter:
    filter_urls = parse_filter_urls(args.filter)
else:
    filter_urls = []

# Adding always filter urls
    filter_urls.append("http://www.github.com/?fakeVar=true")

# Checking for the silent flag
if args.silent:
    silent = True
else:
    silent = False

# Altering working_url if the environment is mobile
if "mobile" in site_type:
    working_url = worker_environment.replace("www", "m")
else:
    working_url = worker_environment

# Appending date/time to reporting_file name if reporttime arg is passed.
if args.reporttime:
    reporting_file += "-" + strftime("%Y-%m-%d-%H:%M:%S")

# TODO: this list can be re-factored. It's here to pass # + description, but was mostly used when the program was terminal reponse based. Currently, only the first array item (description) is used.
# task key , list[task description, report name, "mobile" or "wired"]

worker_task_options = {
    "1": ["Check for mobile pages that have absolute links on them.", "rep-m-AbsoluteLinks", "mobile"],
    "2": ["Check wired pages for missing alternate tag.", "rep-wired-Alternate-Missing", "wired"],
    "3": ["Discover all linked pages from homepage - mobile.", "rep-mobile-HomeCrawl", "mobile"],
    "4": ["Discover all linked pages from homepage - wired.", "rep-wired-HomeCrawl", "wired"],
    "5": ["Code search: Find html comment: <!-- xxx -->", "rep-nocare","wired"]
}

# doing a simple catch for task outside of range
if (int(worker_task) < 1) or (int(worker_task) > len(worker_task_options)):
    print("Please enter a task between 1 and {}".format(len(worker_task_options)))
    quit()


# SETUP WORKER
worker = AgentPy.AgentPyTasks.WorkerTasks(task_description=worker_task_options[worker_task][0], environment_description=worker_environment, base_url=working_url, report_file=reporting_file, sitemap_url=sitemap, exception_list=filter_urls, silent=silent);


if worker_task == "1":
    # check for absolute links
    worker.task_absolute_links(allow_list=["http://www.mysite.com"], site_type=site_type, flag_max=1, no_report_urls=['http://www.balh.com/?fake=true'], report_only_offending=True, check_url=True, replace_url=["www","m"])
if worker_task == "2":
    # check for missing alternate media tag
    worker.task_check_tags(has_tags=False, tag='link', classname='alternate', sub_tag_type='rel', site_type=site_type, flag_max=0)
if worker_task == "3" or worker_task == "4":
    worker.task_home_crawl()
if worker_task == "5":
    # parse html code for whatever
    worker.code_check(code='<!-- hi -->', site_type='wired')
