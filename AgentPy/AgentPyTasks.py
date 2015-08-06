__author__ = 'jason.a.martin'

from AgentPy.AgentPy import WebWorker
from bs4 import BeautifulSoup

'''
    This file serves as an example of what you can do. Make your own task file by copying what's above this comment then putting functions inside of the WorkerTasks class like this:

    class WorkerTasks(WebWorker):
        def whatever(self):
            print("hi);
'''

class WorkerTasks(WebWorker):

    """This sub class is for making task functions that use the AgentPy core"""

    def task_home_crawl(self):
        """This task will hit a home page and keep crawling all pages of the base_url until the list is done.
        This task can be a good way to see all the possible URLs a visitor can hit from the homepage and to be sure
        your sitemap is accurate (or use this to build a sitemap).
        WARNING: This task is highly experimental and can lead to TONS of crawling especially with dynamic urls."""
        self.start_task()
        self.create_report_file()
        response = self.fetch_page(self.base_url)
        if response:
            self.soup = BeautifulSoup(response.read())
            self.tag = "a"
            page_tags = self.parse_tag()
            page_links = self.parse_href(page_tags)
            self.page_crawl_scrub(page_links)
            while True:
                # go to next page [0], get links, check if links were looked at, append crawl pages and remove
                current_page = self.pages_to_crawl[0]
                current_response = self.fetch_page(current_page)
                if current_response:
                    self.soup = BeautifulSoup(current_response.read())
                    self.tag = "a"
                    page_tags = self.parse_tag()
                    page_links = self.parse_href(page_tags)
                    self.page_crawl_scrub(page_links)
                    self.building_report(data=current_page, iterate=0, flag_max=0)
                self.pages_crawled.append(current_page)
                self.pages_to_crawl.remove(current_page)
                if len(self.pages_to_crawl) == 0:
                    break
        self.end_task()
        print(self.report_finished())

    def task_absolute_links(self, allow_list=[], site_type='wired', flag_max=0, no_report_urls=[], report_only_offending=False, check_url=False, replace_url=[]):
        self.start_task()
        self.create_report_file()
        has_sitemap = self.get_sitemap()
        offending_items = 0
        if has_sitemap:
            if site_type == 'mobile':
                links = self.get_mobile_pages()
            else:
                links = self.get_wired_pages()
            # Got all links so parse them
            for link in links:
                current_item = self.catch_absolute_links(page=link, allow_list=allow_list)
                if current_item:
                    offending_items += 1
                    self.building_report(data=current_item, iterate=1, flag_max=flag_max, no_report_urls=no_report_urls, report_only_offending=report_only_offending, check_url=check_url, replace_url=replace_url)
        self.end_task()
        if offending_items > 0:
            print(self.report_finished())
        else:
            print("No offending items")

    def code_check(self, code='', site_type='wired', report_type='all'):
        """Use this when you want to do a simple parse html for code, such as looking for a hidden comment"""
        self.start_task()
        self.create_report_file()
        has_sitemap = self.get_sitemap()
        code_found = []
        code_not_found = []
        report_decoration = self.string_repeater(repeating_string="=", repeat=30)
        offending_items = 0

        if has_sitemap:
            if site_type == 'mobile':
                links = self.get_mobile_pages()
            else:
                links = self.get_wired_pages()
            # Got all links so parse them
            for link in links:
                checking_link = self.scrub_link_exception(link)
                if not checking_link:
                    current_page = self.fetch_page(page=link)
                    if current_page:
                        # code could be str or list
                        current_item = self.parse_html(page=current_page.read(), code=code)
                        if current_item:
                            code_found.append(link)
                        else:
                            code_not_found.append(link)
        self.end_task()
        if len(code_not_found) > 0 or len(code_found) > 0:
            self.raw_report_addition(txt_data="Items Checked: {}\n\n".format(len(code_found) + len(code_not_found)))
            if len(code_found) > 0 and (report_type == 'all' or report_type == 'found'):
                offending_items += len(code_found)
                self.raw_report_addition(txt_data="\n{}Code Found On {} Items{}\n\n".format(report_decoration, len(code_found), report_decoration))
                for link in code_found:
                    self.raw_report_addition(txt_data="{}\n".format(link))
            if len(code_not_found) > 0 and (report_type == 'all' or report_type == 'not_found'):
                offending_items += len(code_not_found)
                self.raw_report_addition(txt_data="\n{}Code Missing On {} Items{}\n\n".format(report_decoration, len(code_not_found), report_decoration))
                for link in code_not_found:
                    self.raw_report_addition(txt_data="\t{}\n".format(link))
            if offending_items > 0:
                print(self.report_finished())
            else:
                print("No offending items.")

    def task_check_tags(self, has_tags=True, tag='', classname='', sub_tag_type='class', site_type='wired', flag_max=0):
        """has_tags: When set to True this function searches the page for the tag. When False, it searches for absense of tag.
        Also you pass in the tag you're searching for, like 'div' and the classname if desired, like 'my-class'
        flag_max means if the bot finds more than X number of tags, it will flag the entry"""
        self.start_task()
        self.create_report_file()
        offending_items = 0
        has_sitemap = self.get_sitemap()
        if has_sitemap:
            if site_type == 'mobile':
                links = self.get_mobile_pages()
            else:
                links = self.get_wired_pages()
            # Got all links so parse them
            for link in links:
                checking_link = self.scrub_link_exception(link)
                if not checking_link:
                    current_item = self.check_for_page_tags(page=link, tag=tag, classname=classname, sub_tag_type=sub_tag_type)
                    if current_item and has_tags:
                        offending_items += 1
                        self.building_report(data=current_item, iterate=1, flag_max=flag_max)
                    elif not current_item and not has_tags:
                        # the link has no ad div
                        offending_items += 1
                        self.building_report(data=link, iterate=0,  flag_max=flag_max)  # 0 for not iterating list
        self.end_task()
        if offending_items > 0:
            print(self.report_finished())
        else:
            print("No offending items")

    def url_verify(self, urls=[]):
        self.start_task()
        self.create_report_file()

        if self.task_file:
            # TODO: Add guard against file not existing!
            with open(self.task_file) as taskfile:
                for t_url in taskfile:
                    if len(t_url.strip()) > 0:
                        self.building_report(data=t_url + " -> " + str(self.url_status_code(t_url, ["", ""])), iterate=0)
        else:
            # using array passed in
            for url in urls:
                self.building_report(data=url + " -> " + str(self.url_status_code(url, ["", ""])), iterate=0)
        self.end_task()
        print(self.report_finished())

    def robot_parse(self, robots_url='', chain=False):
        # This function will attempt to grab a robots.txt file, read it and add any Disallow urls to the exception list.
        # By default it looks for /robots.txt off the base url, but you can pass in a custom url.
        # Pass in chain=True to get back a dictionary object containing both Allow and Disallow items found in the Robots file.
        # Note: If you pass chain=True, this function will not append your exception list.
        if robots_url:
            my_stuff = self.robot_filter(robots_url)
        else:
            my_stuff = self.robot_filter()
        if not chain:
            for site in my_stuff["disallow"]:
                self.exception_list.append(self.base_url + site)
                print(self.exception_list)
        else:
            return my_stuff

    # ================ Custom Tasks ================
    # Leaving these in the main repo in case others want to learn from them, use them or rebuild from them.

    def vdc_mobile_absolute_links(self, allow_list=[], site_type='wired', show_all=False):
        '''
        1. This custom function will look at a mobile page and search for absolute links.
        2. Once those links are found, it does a replace (www. to m.) to see if there is indeed a mobile page.
        3A. If show_all is FALSE, it wll report only offending urls (those returning a 200 status).
        3B. If show_all is TRUE, it will report all absolute links along with their status code.
        4. Since the test server for this function is returning 200 for pages on mobile that don't really exist, I'm doing a code check.
        '''
        self.start_task()
        self.create_report_file()
        report_decoration = self.string_repeater(repeating_string="=", repeat=30)
        self.raw_report_addition(txt_data="\n{}\nStatus: 200 -> Mobile version of the page does exist.\nStatus: 200(False) -> Mobile page doesn't exist, but some sort of non-404 page is being served.\nStatus: 404 -> Mobile version of the page does not exist, returns 404 page.\n{}\n".format(report_decoration, report_decoration))
        has_sitemap = self.get_sitemap()
        offending_items = 0

        if has_sitemap:
            if site_type == 'mobile':
                links = self.get_mobile_pages()
            else:
                links = self.get_wired_pages()
            # Got all links so parse them
            for link in links:
                current_item = self.catch_absolute_links(page=link, allow_list=allow_list)
                if current_item:
                    init = False
                    for abs_link in current_item:
                        if not init:
                            # first item, which is originating page, so ignore.
                            init = True
                            self.raw_report_addition(txt_data="PAGE: {}\n\r".format(abs_link))
                        else:
                            # pages to check.
                            is_mobile = self.url_status_code(abs_link, ['www.', 'm.'])
                            if is_mobile == 200:
                                # is it really there?
                                page_to_check = self.fetch_page(abs_link.replace("www.", "m."))
                                code_found = self.parse_html(page=page_to_check.read(), code="/mytrip/app/Widget")
                                if not code_found:
                                    # reported as 200 AND the code wasn't found, so this is likely a mobile page.
                                    self.raw_report_addition(txt_data="Status 200: {}\n".format(abs_link))
                                    offending_items += 1
                                else:
                                    if show_all:
                                        self.raw_report_addition(txt_data="Status 200(False): {}\n".format(abs_link))
                                        offending_items += 1
                            else:
                                if show_all:
                                    self.raw_report_addition(txt_data="Status {}: {}\n".format(is_mobile, abs_link))
                                    offending_items += 1
                    self.raw_report_addition(txt_data="\r\r")
        self.end_task()
        if offending_items > 0:
            # There's at least 1 item in the report
            self.raw_report_addition(txt_data="\r\r{}\rOffending URLs: {}\r{}\r".format(report_decoration, offending_items, report_decoration))
            print(self.report_finished())

    def vdc_mobile_missing_alternates(self, tag='', classname='', sub_tag_type='class', show_all=True):
            """has_tags: When set to True this function searches the page for the tag. When False, it searches for absense of tag.
            Also you pass in the tag you're searching for, like 'div' and the classname if desired, like 'my-class'
            flag_max means if the bot finds more than X number of tags, it will flag the entry"""
            self.start_task()
            self.create_report_file()
            offending_items = 0
            has_sitemap = self.get_sitemap()
            report_decoration = self.string_repeater(repeating_string="=", repeat=30)

            if show_all:
                self.raw_report_addition(txt_data="\n{}\nShowing all offending items.\nCode Status Legend:\n200 -> Page exists\n200(false) -> Page doesn't exists, but we're showing a fake page instead of 404 page.\n404 -> Page not found.\n{}\n\n".format(report_decoration,report_decoration))
            else:
                self.raw_report_addition(txt_data="\n{}\nReporting only offending pages where a mobile counterpart exists.\n{}\n\n".format(report_decoration, report_decoration))

            if has_sitemap:
                links = self.get_wired_pages()
                # Got all links so parse them
                for link in links:
                    checking_link = self.scrub_link_exception(link)
                    if not checking_link:
                        current_item = self.check_for_page_tags(page=link, tag=tag, classname=classname, sub_tag_type=sub_tag_type)
                        if not current_item:
                            # the link has code missing
                            is_mobile = self.url_status_code(link, ['www.', 'm.'])
                            if is_mobile == 200:
                                # is it really there?
                                page_to_check = self.fetch_page(link.replace("www.", "m."))
                                code_found = self.parse_html(page=page_to_check.read(), code="/mytrip/app/Widget")
                                # print(link)
                                if not code_found:
                                    # reported as 200 AND the code wasn't found, so this is likely a mobile page.
                                    self.raw_report_addition(txt_data="\nStatus 200: {}\n".format(link))
                                    offending_items += 1
                                else:
                                    if show_all:
                                        self.raw_report_addition(txt_data="\nStatus 200(False): {}\n".format(link))
                                        offending_items += 1
                            else:
                                if show_all:
                                    self.raw_report_addition(txt_data="\nStatus {}: {}\n".format(is_mobile, link))
                                    offending_items += 1
            self.end_task()
            if offending_items > 0:
                print(self.report_finished())
            else:
                print("No offending items")

    def vdc_find_broken_links(self):
            '''
            1. This custom function will grab all links in a sitemap file and check each link on those pages to see if they link to a 404.
            '''
            self.start_task()
            self.create_report_file()
            report_decoration = self.string_repeater(repeating_string="=", repeat=30)
            has_sitemap = self.get_sitemap()
            offending_items = 0

            if has_sitemap:
                # links = self.get_mobile_pages()
                links = self.get_wired_pages()
                # Got all links so parse them
                for link in links:
                    current_page = self.fetch_page(link)
                    if current_page:
                        self.soup = BeautifulSoup(current_page.read())
                        self.tag = "a"
                        page_tags = self.parse_tag()
                        page_links = self.parse_href(page_tags)
                        # check status of page link
                        first_link = True
                        for destination in page_links:
                            if destination:
                                if first_link:
                                    first_link = False
                                    self.raw_report_addition(txt_data="SOURCE: {}\n\n".format(link))
                                if destination.startswith("http://"):
                                    reporting_link = destination
                                    status = self.url_status_code(reporting_link)
                                else:
                                    reporting_link = self.base_url + destination
                                    status = self.url_status_code(reporting_link)
                                if status == 404:
                                    offending_items += 1
                                    self.raw_report_addition(txt_data="404 - {}: {}\n\n".format(status, reporting_link))
                                else:
                                    self.raw_report_addition(txt_data="{}: {}\n\n".format(status, reporting_link))
            self.end_task()
            if offending_items > 0:
                # There's at least 1 item in the report
                self.raw_report_addition(txt_data="\r\r{}\rOffending URLs: {}\r{}\r".format(report_decoration, offending_items, report_decoration))
                print(self.report_finished())

    def vdc_link_status(self):
            self.start_task()
            self.create_report_file()
            offending_items = 0

            if self.task_file:
                # TODO: Add guard against file not existing!
                with open(self.task_file) as taskfile:
                    for t_url in taskfile:
                        if len(t_url.strip()) > 0:
                            link_status = self.url_status_code(t_url)
                            if link_status is not 200:
                                offending_items += 1
                                self.raw_report_addition(txt_data="Status: {} Url: {}".format(link_status, t_url))

            self.end_task()
            if offending_items > 0:
                report_decoration = self.string_repeater(repeating_string="=", repeat=20)
                self.raw_report_addition(txt_data="{}Offending items: {}{}".format(report_decoration, offending_items, report_decoration))
                print(self.report_finished())
