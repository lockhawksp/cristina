import requests

from bs4 import BeautifulSoup


class Job(object):
    pass


class V2exJob(Job):

    def __init__(self, url, summary=None, details=None):
        self.url = url
        self.summary = summary
        self.details = details

    def __repr__(self):
        return 'V2exJob: %s' % self.summary

    @classmethod
    def from_dict(cls, a_dict: dict):
        url = a_dict.get('url', None)
        if url is None:
            raise ValueError('a url is needed')
        summary = a_dict.get('summary', None)
        details = a_dict.get('details', None)
        return cls(url, summary=summary, details=details)


class Api(object):
    pass


class V2exApi(Api):

    INDEX_URL = 'http://www.v2ex.com'
    JOB_LIST_URL = INDEX_URL + '/go/jobs'

    def __init__(self):
        pass

    def get_job_list_url(self, page_num):
        if page_num == 1:
            return self.JOB_LIST_URL
        else:
            return '%s?p=%d' % (self.JOB_LIST_URL, page_num)

    def __to_full_url(self, url):
        return self.INDEX_URL + url

    def __download_job_list(self, page_num):
        url = self.get_job_list_url(page_num)
        resp = requests.get(url)
        html = resp.text if resp.status_code == 200 else ''
        return html

    def __parse_job_list(self, html):
        soup = BeautifulSoup(html)
        span_elems = soup.find_all('span', {'class': 'item_title'})

        jobs = []
        for span_elem in span_elems:
            a_elem = span_elem.find('a')
            url = self.__to_full_url(a_elem['href'])
            summary = a_elem.text
            job = {
                'url': url,
                'summary': summary
            }
            jobs.append(job)

        return jobs

    def fetch_job_list(self, page_num):
        html = self.__download_job_list(page_num)
        return self.__parse_job_list(html)

    def __download_job_details(self, url):
        resp = requests.get(url)
        html = resp.text if resp.status_code == 200 else ''
        return html

    def __parse_job_details(self, html):
        soup = BeautifulSoup(html)
        div_elem = soup.find('div', {'class': 'topic_content'})
        return div_elem.text

    def fetch_job_details(self, url):
        html = self.__download_job_details(url)
        return self.__parse_job_details(html)


class Filter(object):
    pass


class V2exJobFilter(Filter):

    def _filter(self, job):
        pass

    def filter(self, job):
        return self._filter(job)


class V2exCityFilter(V2exJobFilter):

    def __init__(self, include_cities=()):
        self.__include_cities = include_cities

    def _filter(self, job):
        for c in self.__include_cities:
            if c in job.summary:
                return True
        return False


class Finder(object):
    pass


class V2exJobFinder(Finder):

    def __init__(self, filters=()):
        self.__api = V2exApi()
        self.__filters = filters

    def __job_accepted(self, job):
        for f in self.__filters:
            if not f.filter(job):
                return False
        return True

    def find(self, page_num):
        job_dict_list = self.__api.fetch_job_list(page_num)
        jobs = []
        for job_dict in job_dict_list:
            job = V2exJob.from_dict(job_dict)
            if self.__job_accepted(job):
                print(job.url, job.summary)
                jobs.append(job)

        return jobs

    def find_in(self, *page_nums):
        jobs = []
        for page_num in page_nums:
            jobs.extend(self.find(page_num))
        return jobs

    def find_in_range(self, start, end):
        jobs = []
        for page_num in range(start, end+1):
            jobs.extend(self.find(page_num))
        return jobs
