__author__ = 'jason.a.martin'

import urllib.request
from bs4 import BeautifulSoup
import datetime

class WebWorker(object):
    """A class that does various web-based tasks."""
    """Tasks are created in the subclass in AgentPyTasks.py"""

    def __init__(self, task_description, environment_description, base_url, report_file, sitemap_url, exception_list=[]):
        self.task_description = task_description
        self.environment_description = environment_description
        self.base_url = base_url
        self.report_file = report_file
        self.report_html = ''
        self.report_text = ''
        self.soup = ''
        self.tag = ''
        self.tag_classname = ''
        self.start_time = ''
        self.end_time = ''
        self.exception_list = exception_list
        self.sitemap_url = sitemap_url
        self.pages_crawled = []
        self.pages_to_crawl = []
        self.generated_sitemap = {}
        self.user_agent = ''

    def set_user_agent(self, agent):
        self.user_agent = agent

    def fetch_page(self, page):
        print("Attempting to grab page: {}".format(page))
        headers = {}
        if not self.user_agent:
            headers['User-Agent'] = self.user_agent
        try:
            request = urllib.request.Request(page, headers=headers)
            response = urllib.request.urlopen(request)
            return response
        except urllib.request.URLError as url_error:
            print("URL: {}\nFETCH ERROR: {}".format(page, url_error.reason))
            return False

    def get_sitemap(self):
        response = self.fetch_page(self.sitemap_url)
        if response:
            self.soup = BeautifulSoup(response.read())
            return True
        else:
            return None

    def get_mobile_pages(self):
        self.tag = "xhtml:link"
        all_tags = self.parse_tag()
        links = self.parse_href(all_tags)
        return links

    def get_wired_pages(self):
        self.tag = "loc"
        all_tags = self.parse_tag()
        links = self.parse_tag_text(all_tags)
        return links

    def parse_tag(self, sub_tag_type='class'):
        """Set to search for classes by default"""
        if self.tag_classname == '':
            instance_tags = self.soup.findAll(self.tag)
        else:
            instance_tags = self.soup.findAll(self.tag, {sub_tag_type: self.tag_classname})
        return instance_tags

    def parse_href(self, obj):
        urls = []
        for link in obj:
            urls.append(link.get('href'))
        return urls

    def parse_tag_text(self, obj):
        items = []
        for item in obj:
            items.append(item.text)
        return items

    def scrub_link_exception(self, page):
        link_found = False
        for link in self.exception_list:
            #changing == to in for link in str(page) to match contains verses absolutes.
            if link in str(page):
                link_found = True
        return link_found

    def start_task(self):
        print("Starting task: {}".format(self.task_description))
        self.start_time = datetime.datetime.now()

    def end_task(self):
        print("Ending task: {}".format(self.task_description))
        self.end_time = datetime.datetime.now()

    def catch_absolute_links(self, page, allow_list=[]):
        # change page to match environment
        report = []
        first_case = True
        page_exists = self.fetch_page(page)
        if not page_exists:
            return None
        html = page_exists.read()
        self.soup = BeautifulSoup(html)
        self.tag = "a"
        tags = self.parse_tag()
        links = self.parse_href(tags)

        for link in links:
            checking_link = self.scrub_link_exception(link)
            if not checking_link:  # link not found so proceed
                # cycle through list and look for allowed url bases
                for allowed_url in allow_list:
                    if allowed_url in str(link):
                        if first_case:
                            report.append(page)
                            first_case = False
                        report.append(link)
                        break
        if not first_case:
            return report
        else:
            return None

    def check_for_page_tags(self, page, tag, classname, sub_tag_type='class'):
        # change page to match environment
        report = []
        first_case = True
        page_exists = self.fetch_page(page)
        if not page_exists:
            return None

        html = page_exists.read()
        self.soup = BeautifulSoup(html)
        self.tag = tag
        self.tag_classname = classname
        tags = self.parse_tag(sub_tag_type)

        for tag in tags:
            check_tag = str(tag)
            # replace < and > with [ and ] so the tag isn't interpreted in html report.
            check_tag = check_tag.replace('<', '[')
            check_tag = check_tag.replace('>', ']')
            if first_case:
                report.append(page)
                first_case = False
            report.append(check_tag)
        if not first_case:
            return report
        else:
            return None

    # BUILDING REPORT

    def create_report_file(self):
        # blows out any current file
        with open(self.report_file + '.html', 'w') as f:
            f.write('<link rel="stylesheet" type="text/css" href="style.css">')
            f.write('<div class="scanEnvironment">ENVIRONMENT: {}</div>'.format(self.environment_description))
            f.close()
            # making TXT report too
        with open(self.report_file + '.txt', 'w') as txtFile:
            txtFile.write("Report generated on: {}\n".format(datetime.datetime.now()))
            txtFile.write("Environment: {}\n".format(self.environment_description))
            txtFile.write("Task: {}\n\n\n".format(self.task_description))
            txtFile.close()

    def building_report(self, data, iterate=1, flag_max=0):
        index = 0
        all_text = ''
        flag_class = ''
        if flag_max is not 0:
            if len(data) - 1 > flag_max:
                flag_class = "scanFlagSite"
        html = '<div class="scanSection {}">'.format(flag_class)
        # if iterate is 1, normal reporting
        if iterate == 1:
            for item in data:
                if index == 0:
                    html += '<div class="scanSite">{}</div>'.format(item)
                    all_text += '\n{}\n'.format(item)
                else:
                    html += '<div class="scanOffendingURL">{}</div>'.format(item)
                    all_text += '\t{}\n'.format(item)
                index += 1
        else:
            html += '<div class="scanSite">{}</div>'.format(data)
            all_text += '{}\n'.format(data)
        # end iterate
        html += "</div>"
        # write to file
        with open(self.report_file + '.html', 'a') as f:
            f.write(html)
            f.close()
        # writing txt file too
        with open(self.report_file + '.txt', 'a') as txtFile:
            txtFile.write(all_text)
            txtFile.close()

    def report_finished(self):
        total_time = self.end_time - self.start_time
        datetime.timedelta(0, 8, 562000)
        time_out = divmod(total_time.days * 86400 + total_time.seconds, 60)
        return "Report finished in: {}".format(time_out)

    def page_crawl_scrub(self, links):
        for link in links:
            if "http://" in str(link):
                if self.base_url in str(link):
                    if (link not in self.pages_to_crawl) and (link not in self.pages_crawled):
                        self.pages_to_crawl.append(link)
            else:
                if (self.base_url+"/"+str(link) not in self.pages_to_crawl) and (self.base_url+"/"+str(link) not in self.pages_crawled):
                    self.pages_to_crawl.append(self.base_url+"/"+str(link))
