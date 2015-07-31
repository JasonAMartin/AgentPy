__author__ = 'jason.a.martin'

import urllib.request
from bs4 import BeautifulSoup
import datetime
import smtplib
from email.mime.text import MIMEText


class WebWorker(object):

    """A class that does various web-based tasks."""
    """Tasks are created in the subclass in AgentPyTasks.py"""

    def __init__(self, task_description, environment_description, base_url, report_file, sitemap_url, exception_list=[], silent=False, email_reports=False, emails=[], mail_server='', from_email='', task_file=''):
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
        self.silent = silent
        self.email_reports = email_reports
        self.emails = emails
        self.mail_server = mail_server
        self.from_email = from_email
        self.task_file = task_file

    def set_user_agent(self, agent):
        self.user_agent = agent

    def fetch_page(self, page):
        if not self.silent:
            print("Attempting to grab page: {}".format(page))
        headers = {}
        if not self.user_agent:
            headers['User-Agent'] = self.user_agent
        try:
            request = urllib.request.Request(page, headers=headers)
            response = urllib.request.urlopen(request)
            return response
        except urllib.request.URLError as url_error:
            if not self.silent:
                print("URL: {}\nFETCH ERROR: {}".format(page, url_error.reason))
            return False

    def get_sitemap(self):
        response = self.fetch_page(self.sitemap_url)
        if response:
            self.soup = BeautifulSoup(response.read())
            return True
        else:
            return None

    def parse_html(self, page, code):
        if code in str(page):
            if not self.silent:
                print("Code found.")
            return True
        else:
            return False

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
            checking_link = self.scrub_link_exception(link.get('href'))
            if not checking_link:
                urls.append(link.get('href'))
        return urls

    def parse_tag_text(self, obj):
        items = []
        for item in obj:
            items.append(item.text)
        return items

    def url_status_code(self, url='', replace_url=''):
        if replace_url:
            testing_url = url.replace(replace_url[0], replace_url[1])
        else:
            testing_url = url
        try:
            r = urllib.request.urlopen(testing_url)
            new_url = r.geturl()
            if new_url in url:
                return r.getcode()
            else:
                return 301
        except urllib.request.URLError as url_error:
            return url_error

    def scrub_link_exception(self, page):
        link_found = False
        for link in self.exception_list:
            # changing == to in for link in str(page) to match contains verses absolutes.
            if link in str(page):
                link_found = True
        return link_found

    def start_task(self):
        if not self.silent:
            print("Starting task: {}".format(self.task_description))
        self.start_time = datetime.datetime.now()

    def end_task(self):
        if not self.silent:
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
                        if firslt_case:
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

    def raw_report_addition(self, html_data='', txt_data=''):
        # Once a report is going, this function can be used to write data to the file.
        # If you're making your own tasks, it might be best to just generate whatever data you want in the report them spit it out here.
        # You can pass in data for the html file, text file or both.

        # write to html file
        if html_data:
            with open(self.report_file + '.html', 'a') as f:
                f.write(html_data)
                f.close()
        # writing txt file
        if txt_data:
            with open(self.report_file + '.txt', 'a') as txtFile:
                txtFile.write(txt_data)
                txtFile.close()

    def building_report(self, data, iterate=1, flag_max=0, no_report_urls=[], report_only_offending=False, check_url=False, replace_url=[]):
        index = 0
        offending_items = 0
        all_text = ''
        flag_class = ''
        working_url = 0
        if flag_max is not 0:
            if len(data) -1 > flag_max:
                flag_class = "scanFlagSite"
        html = '<div class="scanSection {}">'.format(flag_class)
        # if iterate is 1, normal reporting
        if iterate == 1:
            for item in data:
                if index == 0:
                    html += '<div class="scanSite">{}</div>'.format(item)
                    all_text += '\n{}\n'.format(item)
                else:
                    if item not in no_report_urls:
                        if check_url:
                            working_url = self.url_status_code(url=item, replace_url=replace_url)

                        if (not check_url) or (check_url and working_url == 200):
                            html += '<div class="scanOffendingURL">{}</div>'.format(item)
                            all_text += '\t{}\n'.format(item)
                            offending_items += 1
                index += 1
        else:
            html += '<div class="scanSite">{}</div>'.format(data)
            all_text += '{}\n'.format(data)
        # end iterate
        html += "</div>"

        # reporting if report_only_offending is turned on and there are offending items or the options is false.
        if (iterate == 1 and offending_items > 0 and report_only_offending) or not report_only_offending:
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
        # email report if requested
        if self.email_reports:
            self.email_report()
        return "Report finished in: {}".format(time_out)

    def email_report(self):
        # Check if emails were set and if so, build a To: list.
        if len(self.emails) > 0:
            first_email = 0
            all_emails = ''
            for current_email in self.emails:
                if first_email == 0:
                    all_emails = current_email
                    first_email = 1
                else:
                    all_emails += ","+current_email
            # self.report_file + '.txt'
            if not self.silent:
                print("Emailing reports to {} using mail server {}: ".format(all_emails, self.mail_server))
            with open(self.report_file + '.txt') as reportFile:
                # Reading the TXT version of the report file
                msg = MIMEText(reportFile.read())
                # Building email to send.
                msg['To'] = all_emails
                msg['From'] = self.from_email
                msg['Subject'] = 'AgentPy Report: ' + self.task_description
                s = smtplib.SMTP(self.mail_server)
                s.send_message(msg)
                s.quit()

    def page_crawl_scrub(self, links):
        for link in links:
            if "http://" in str(link):
                if self.base_url in str(link):
                    if (link not in self.pages_to_crawl) and (link not in self.pages_crawled):
                        self.pages_to_crawl.append(link)
            else:
                if (self.base_url+"/"+str(link) not in self.pages_to_crawl) and (self.base_url+"/"+str(link) not in self.pages_crawled):
                    self.pages_to_crawl.append(self.base_url+"/"+str(link))

    def robot_filter(self, robots_url=''):
        # Try to grab /robots.txt or provided url and look for Disallow: and add that data to exception list.
        # Returns a dictionary of two arrays, allow and disallow.
        disallow_robot_items = []
        allow_robot_items = []
        all_robot_items = {
            "allow" : allow_robot_items,
            "disallow" : disallow_robot_items
        }
        if robots_url:
            robots_file = self.fetch_page(robots_url)
        else:
            robots_file = self.fetch_page(self.base_url+"/robots.txt")
        parse_file = robots_file.readlines()
        for item in parse_file:
            # if Disallow is not in string, dump it
            # replacing garbage potentially found in item and splitting item by spaces
            current_item = str(item).replace("\\r", "").replace("'","").replace("\\n", "").replace("b'","").split(" ")
            if len(current_item) > 1:
                if ("*" not in current_item[1]) and ("$" not in current_item[1]) and (len(str(current_item[1])) > 0):
                    # current item has no restricted items and is 1+ chars in length.
                    if "Disallow" in current_item[0]:
                        disallow_robot_items.append(current_item[1])
                    if "Allow" in current_item[0]:
                        allow_robot_items.append(current_item[1])
        return all_robot_items

    def string_repeater(self, repeating_string='', repeat=0):
        final_string = ''
        starting_count = 1
        if repeat > 0 and repeating_string:
            while starting_count <= repeat:
                final_string += repeating_string
                starting_count += 1
        return final_string
