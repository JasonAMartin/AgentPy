import AgentPy.AgentPyTasks

# DATA
# keep env keys in lowercase when possible
worker_environment_options = {
    "production": "http://www.vegas.com",
    "test01": "http://test01-www.vegas.com",
    "test02": "http://test02-www.vegas.com",
    "test03": "http://test03-www.vegas.com",
    "test04": "http://test04-www.vegas.com",
    "test05": "http://test05-www.vegas.com",
    "test06": "http://test06-www.vegas.com",
    "test07": "http://test07-www.vegas.com",
    "test08": "http://test08-www.vegas.com",
    "test09": "http://test09-www.vegas.com",
    "test10": "http://test10-www.vegas.com",
    "test11": "http://test11-www.vegas.com",
    "test12": "http://test12-www.vegas.com",
    "test13": "http://test13-www.vegas.com",
    "test14": "http://test14-www.vegas.com"
}

# task key , list[task description, report name, "mobile" or "wired"]
worker_task_options = {
    "1": ["Check for existance of mobile ads (divs with class 'vdcMobileAds')", "rep-m-AdPages", "mobile"],
    "2": ["Check for absense of mobile ads (divs with class 'vdcMobileAds')", "rep-m-PagesNoAds", "mobile"],
    "3": ["Check for mobile pages that have absolute links on them.", "rep-m-AbsoluteLinks", "mobile"],
    "4": ["Check for mobile pages that have canonical tag.", "rep-m-Canonical", "mobile"],
    "5": ["Check for mobile pages that are missing canonical tag.", "rep-m-Canonical-Missing", "mobile"],
    "6": ["Check wired pages for alternate tag.", "rep-wired-Alternate", "wired"],
    "7": ["Check wired pages for missing alternate tag.", "rep-wired-Alternate-Missing", "wired"],
    "8": ["Discover all linked pages from homepage - mobile.", "rep-mobile-HomeCrawl", "mobile"],
    "9": ["Discover all linked pages from homepage - wired.", "rep-wired-HomeCrawl", "wired"]
}

vdc_exceptions = ["http://www.vegas.com/?fws=true","http://www.vegas.com/searchagent/restaurant/ViewRestaurant.do?restaurantId"]

# MENUS


def show_environment_menu():
  ans = True
  while ans:
    print("\nSelect an environment for your work.\n")
    for k in sorted(worker_environment_options):
        print("\tType: '{}' :: {}".format(k, worker_environment_options[k]))
    print("\n\tType: 'Quit' :: Exit\n")
    response=input("What environment do you want to scan? ")

    try:
        answer = str(response)
    except ValueError:
        answer = "999"

    if answer in worker_environment_options:
        return answer
    elif answer == "quit":
      print("\n Goodbye")
      exit()
    elif answer == "999":
      print("\n Please enter a choice from my menu. Thank you.")


def show_task_menu():
  ans = True
  while ans:
    print("\nSelect a task for your web bot.\n")
    for k in sorted(worker_task_options):
        print("\tType: '{}' :: {}".format(k, worker_task_options[k][0]))
    print("\n\tType: 'Quit' :: Exit\n")
    response=input("What task do you want to run? ")

    try:
        answer = str(response)
    except ValueError:
        answer = "999"

    if answer in worker_task_options:
        return answer
    elif answer == "quit":
      print("\n Goodbye")
      exit()
    elif answer == "999":
      print("\n Please select a task from my menu. Thank you.")


# INPUT DATA
worker_environment = show_environment_menu()
worker_task = show_task_menu()
sitemap = worker_environment_options[worker_environment] + "/sitemap.xml"
site_type = worker_task_options[worker_task][2]

if worker_task_options[worker_task][2] is "mobile":
    working_url = worker_environment_options[worker_environment].replace("www", "m")
else:
    working_url = worker_environment_options[worker_environment]

# SETUP WORKER
reporting_file = "{}-{}".format(worker_task_options[worker_task][1],worker_environment)
worker = AgentPy.AgentPyTasks.WorkerTasks(task_description=worker_task_options[worker_task][0], environment_description=worker_environment, base_url=working_url, report_file=reporting_file, sitemap_url=sitemap, exception_list=vdc_exceptions);

print("Task DESC: {}\nENV DESC: {}\nBASE URL: {}\nREPORT FILE:{}".format(worker.task_description,worker.environment_description,worker.base_url,worker.report_file))

if worker_task == "1":
    # check for ad tags
    worker.task_check_tags(has_tags=True, tag='div', classname='vdcMobileAds', sub_tag_type='', site_type=site_type, flag_max=0)
if worker_task == "2":
    # check for absense of ad tags
    worker.task_check_tags(has_tags=False, tag='div', classname='vdcMobileAds', sub_tag_type='', site_type=site_type, flag_max=0)
if worker_task == "3":
    # check for absolute links
    worker.task_absolute_links(allow_list=["http://www.vegas.com"], site_type=site_type, flag_max=6)
if worker_task == "4":
    # check for canonical
    worker.task_check_tags(has_tags=True, tag='link', classname='canonical', sub_tag_type='rel', site_type=site_type, flag_max=1)
if worker_task == "5":
    # check for missing canonical tag on mobile
    worker.task_check_tags(has_tags=False, tag='link', classname='canonical', sub_tag_type='rel', site_type=site_type, flag_max=0)
if worker_task == "6":
    # check for alternate media tag
    worker.task_check_tags(has_tags=True, tag='link', classname='alternate', sub_tag_type='rel', site_type=site_type, flag_max=1)
if worker_task == "7":
    # check for missing alternate media tag
    worker.task_check_tags(has_tags=False, tag='link', classname='alternate', sub_tag_type='rel', site_type=site_type, flag_max=0)
if worker_task == "8" or worker_task == "9":
    worker.task_home_crawl()