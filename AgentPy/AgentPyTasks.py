__author__ = 'jason.a.martin'

from AgentPy.AgentPy import WebWorker
from bs4 import BeautifulSoup


# TODO: REMOVE BeautifulSoup and put it in main class. This sub should largely be void of reqs.
# TODO: Clean up this sub class, especially task_home_crawl
# TODO: Find way for page_crawl_scrub to be in main class.

class WorkerTasks(WebWorker):

    def task_home_crawl(self):
        """This task will hit a home page and keep crawling all pages of the base_url until the list is done.
        This task can be a good way to see all the possible URLs a visitor can hit from the homepage and to be sure
        your sitemap is accurate (or use this to build a sitemap)."""
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
        if has_sitemap:
            if site_type == 'mobile':
                links = self.get_mobile_pages()
            else:
                links = self.get_wired_pages()
            # Got all links so parse them
            for link in links:
                current_item = self.catch_absolute_links(page=link, allow_list=allow_list)
                if current_item:
                    print(current_item)
                    self.building_report(data=current_item, iterate=1, flag_max=flag_max, no_report_urls=no_report_urls, report_only_offending=report_only_offending, check_url=check_url, replace_url=replace_url)
        self.end_task()
        print(self.report_finished())

    def code_check(self, code='', site_type='wired'):
        """Use this when you want to do a simple parse html for code, such as looking for a hidden comment"""
        self.start_task()
        self.create_report_file()
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
                    current_page = self.fetch_page(page=link)
                    if current_page:
                        current_item = self.parse_html(page=current_page.read(), code=code)
                        if current_item:
                            self.building_report(data=current_item, iterate=0)
        self.end_task()
        print(self.report_finished())

    def task_check_tags(self, has_tags=True, tag='', classname='', sub_tag_type='class', site_type='wired', flag_max=0):
        """has_tags: When set to True this function searches the page for the tag. When False, it searches for absense of tag.
        Also you pass in the tag you're searching for, like 'div' and the classname if desired, like 'my-class'
        flag_max means if the bot finds more than X number of tags, it will flag the entry"""
        self.start_task()
        self.create_report_file()
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
                        self.building_report(data=current_item, iterate=1, flag_max=flag_max)
                    elif not current_item and not has_tags:
                        # the link has no ad div
                        self.building_report(data=link, iterate=0,  flag_max=flag_max)  # 0 for not iterating list
        self.end_task()
        print(self.report_finished())

"""This sub class is for making task functions that use the AgentPy core"""
