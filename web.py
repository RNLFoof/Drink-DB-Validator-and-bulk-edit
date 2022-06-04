from datetime import datetime
import os
import re

import requests

class WebException(Exception):
    pass

timers = {}
timertower = []
def starttimer(name):
    if name in timers:
        raise Exception(f"{name} is an existing timer")
    timers[name] = datetime.utcnow()
    timertower.append(name)
    print(f"{str(timertower).ljust(100, ' ')} {name}: Starting now.")

def endtimer(name):
    if name not in timers:
        print("Guess it ended.")
    endedat = datetime.utcnow()-timers[name]
    del timers[name]
    timertower.remove(name)
    print(f"{str(timertower).ljust(100, ' ')} {name}: Ended at {endedat}.")

def endalltimers():
    timers.clear()
    timertower.clear()

class Website:
    HTML_PATH = r"html/"
    def __init__(self):
        # Generated when needed
        self._html = None
        self._url = None

    @property
    def url(self):
        return self._url

    @property
    def html(self):
        # starttimer("html")
        if not self._html:
            self._html = self.gethtml(self.url)
        # endtimer("html")
        return self._html

    @staticmethod
    def get_html_storage_path(url):
        return (os.path.join(Website.HTML_PATH, re.sub("[^A-Za-z0-9]", "", url)) + ".html").lower()

    @staticmethod
    def updatehtml(url):
        print("WAAAAAAAAAAAAAAAAAAAA", url)
        # Trying to not get ratelimited
        # time.sleep(10)
        # I know this is bad practice but fuck you
        # global driver
        # if driver is None:
        #     driver = webdriver.Firefox()
        # This would be done with requests, but I made like three requests and untappd said it was too many, so...
        html_storage_path = Website.get_html_storage_path(url)
        owned_page_html = requests.get(url).content
        # driver.get(url)
        # owned_page_html = driver.find_element_by_tag_name("body").get_attribute("innerHTML").encode("UTF-8", errors='replace').decode()
        with open(html_storage_path, "wb") as f:
            f.write(owned_page_html)
        return str(owned_page_html)

    @staticmethod
    def loadhtml(url):
        html_storage_path = Website.get_html_storage_path(url)
        try:
            with open(html_storage_path, "r", encoding="UTF-8") as f:
                return f.read()
        except:
            pass
        with open(html_storage_path, "r", encoding="UTF-8", errors="surrogateescape") as f:
            return f.read()

    @staticmethod
    def gethtml(url):
        html_storage_path = Website.get_html_storage_path(url)
        if os.path.exists(html_storage_path):
            return Website.loadhtml(url)
        return Website.updatehtml(url)

class GoogleSearch(Website):
    def __init__(self, searchterm):
        # starttimer("GoogleSearch init")
        super().__init__()
        self.searchterm = searchterm
        self._url = fr"https://www.google.com/search?client=firefox-b-d&q={self.searchterm}"
        self._searchinstead = None
        self.gottensearchinstead = False  # Because _searchinstead can genuinely be None
        # endtimer("GoogleSearch init")

    @property
    def searchinstead(self):
        """The term it assumes your dumb ass meant. Ex: https://www.google.com/search?q=typhooon - > typhoon"""
        if not self.gottensearchinstead:
            if "Showing results for" in self.html:  # Speed it up a bit
                suggestionmatch = re.search(r'">Showing results for <a id=.*?<span><b><i>(.*?)</i></b></span></a>',
                                            self.html)
                if suggestionmatch:
                    self._searchinstead = re.sub(r"</?[bi]>", "", suggestionmatch.group(1))
            self.gottensearchinstead = True
        return self._searchinstead

class Wikipedia(Website):
    def __init__(self, searchtermorurl):
        # These guys are generated as needed.
        super().__init__()
        self._name = None
        self._url = None
        self._brackets = None
        self._googlesearch = None
        self._infobox = None
        self._openingparagraph = None
        self._openingsentence = None

        # This stuff can genuinely be None, so this is needed
        self.gottenbrackets = False
        self.gotteninfobox = False
        self.gottenopeningparagraph = False
        self.gottenopeningsentence = False

        # These losers let the properties be generated.
        if searchtermorurl.startswith("http"):
            self.createdwithurl = True
            self._url = searchtermorurl
        else:
            self.createdwithurl = False
            self.searchterm = searchtermorurl

    @property
    def createdwithsearchterm(self):
        return not self.createdwithurl

    @property
    def name(self):
        # starttimer("name")
        if not self._name:
            if self.createdwithurl:
                self.setnameandbrackets(
                    re.search(r"""<h1 id="firstHeading" class="firstHeading mw-first-heading">(?:<i>)?(.*?)(?:</i>)?</h1>""", self.html)
                        .group(1))
            else:
                self.setpropertiesusinggooglesearch()
        # endtimer("name")
        return self._name

    @property
    def brackets(self):
        # starttimer("brackets")
        if not self.gottenbrackets:
            self.name  # LOL
            self.gottenbrackets = True
        # endtimer("brackets")
        return self._brackets

    @property
    def url(self):
        if not self._url:
            if self.createdwithsearchterm:
                self.setpropertiesusinggooglesearch()
            else:
                raise WebException("Can't generate url, created with url. How did you get here lol")
        return self._url

    @property
    def googlesearch(self):
        # starttimer("googlesearch")
        if not self._googlesearch:
            if self.createdwithsearchterm:
                # starttimer("create GS")
                self._googlesearch = GoogleSearch(self.searchterm)
                # endtimer("create GS")
            else:
                raise WebException("Can't get google search, created with url.")
        # endtimer("googlesearch")
        return self._googlesearch

    @property
    def infobox(self):
        if not self.gotteninfobox:
            match = re.search(r'<table class="infobox.*?>((?:.|\n)*?)</table>', self.html)
            if match:
                self._infobox = match.group(1)
            self.gotteninfobox = True
        return self._infobox

    @property
    def openingparagraph(self):
        if not self.gottenopeningparagraph:
            workinghtml = self.html
            if self.infobox:
                workinghtml = self.html.replace(self.infobox, "")
            self._openingparagraph = re.search(r"<p>(.|\n)*?</p>", workinghtml).group()
            if len(re.sub("<br ?/?>|\s", "", self._openingparagraph)) <= 7:
                self._openingparagraph = None
            self.gottenopeningparagraph = True
        return self._openingparagraph

    @property
    def openingsentence(self):
        if not self.gottenopeningsentence:
            if not self.openingparagraph:
                self._openingsentence = None
            else:
                self._openingsentence = re.search(r"<p>((?:.|\n)*?)(\.|$)", self.openingparagraph).group(1)
            self.gottenopeningsentence = True
        return self._openingsentence

    def setpropertiesusinggooglesearch(self):
        # starttimer("setpropertiesusinggooglesearch")
        # starttimer("wikipediamatch")
        if " - Wikipedia" in self.googlesearch.html:
            # starttimer("wikipediaactualregex")
            wikipediamatch = re.search(r'<a[a-zA-Z0-9/."=:<>]+?href="([a-zA-Z0-9/."=:<>]+?)"[a-zA-Z0-9/."=:<>]+?>([a-zA-Z0-9/."=:]+?) - Wikipedia<', self.googlesearch.html)
            # endtimer("wikipediaactualregex")
        else:
            wikipediamatch = None
        # endtimer("wikipediamatch")
        if not wikipediamatch:
            endalltimers()
            raise WebException("No match.")
        self._url = wikipediamatch.group(1)
        self.setnameandbrackets(wikipediamatch.group(2))
        # endtimer("setpropertiesusinggooglesearch")

    def setnameandbrackets(self, string):
        # starttimer("setnameandbrackets")
        bracketmatch = re.search(f"\((.*?)\)$", string)
        if bracketmatch:
            self._brackets = bracketmatch.group()
            self._name = string.replace(bracketmatch.group(), "").strip()
        else:
            self._name = string
        # endtimer("setnameandbrackets")