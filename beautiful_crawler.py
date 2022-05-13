# Connor Reid 
# Pirate Hole Web crawler
#1/26/21
#description:
"""
This program uses beautifulsoup4 and lxml (for parsing), to conduct web crawling that specifically
searches websites for links containing key words realted to sports streaming. 
hyperlinks that contain these key words will be checked for video frames.
if video frames are found, it will flagged for scanning.
NOTE: video frame is temporary solution, will replace with a more accurate indicator once found
input = Homepage URL
output = a dictoinary containing the results of the scan
    dictionary{"hit" : [list of flagged sites] , "miss" : [list of sites wich failed to be flagged], "misc" : [list of urls that are iether invalid or not worth checking] }
"""
from lib2to3.pgen2.parse import ParseError
from logging import exception
import re
from urllib import request
from urllib.error import HTTPError #used to request and obtain HTML files
from xml.etree.ElementTree import tostring
from bs4 import BeautifulSoup as bs #beatiful soup for analyzing HTML files
#from lxml import etree as et #used to traverse website trees
import sys #for main function arguemnts 
import urllib.parse as parse #to break up URL and reconstruct base URL if needed

#Global Variables
#NOTE: global variables are normally bad, but this reduces the need to recompile objects & passing them between multiple function
#NOTE: other option is to take an object oriented aproach
keywords = re.compile(r'football|UFC|ufc|nfl|nba|nhl|ncaa')
target_tag = re.compile(r'Video|VideoFrame') #target_tag is an object of any string equal to video or videoframe
avoid = re.compile(r'#|&|discord|@|twitch|login|Login|signin|youtube|register|signup|fubo|linkedin|facebook|instagram|twitter') #links containing these strings/chars are avoided
opener = request.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0')] #adds user agent to circumvent website bot filters


def main_func(site_url):
    '''
    main function, which takes a homepage ULR to scan websites for pirated streams
    returns a dictionary containing the results or returns False if hompage url is not valid
    '''
    try:
        print("inserted URL: " + site_url)
        url_segments = parse.urlparse(site_url) #breaking up the URL into segments
        base_url = url_segments.scheme + "://" + url_segments.netloc #using URL segments to contruct the base URL
        response = pageGetter(site_url, None) #fetaching HTML page
        if response[0] == False:
            print("Link no longer valid")
            return False
        html_page = response[1]
        soup = bs(html_page, 'html.parser') #creating bs4 html parser object
        results = Traversal(soup, base_url, url_segments) #traverse all links on first webpage. returns dictionary of the results.

        '''for deeper traversal
        if len(results["hit"]) == 0:
            for url in results["missed"]:
                html_page = pageGetter(url, None)
                soup = bs(html_page, "html.parser")
                Traversal(soup, base_url, url_segments)
        '''
    except:
        print("invalid URL, or URL is no longer active")
        return None
    print("|||| SCAN COMPLETE |||| \n")
    return results
        #NOTE up to this point we can continue to go at greater depths but must pick to travers through iether 'hit' or 'missed' links
       

def Traversal(soup, base_url, url_segments):
    '''
    collects every link on the webpage and iterates through each one,
    to determine if its worth investigating or not. If the link is worth searching,
    a scan of the web page will be conducted. stores findings in dictionary called results 
    '''
    results = {"hit" : [], "missed" : [], "misc" : []} 
    for link in soup.find_all('a'): #pulls every 'a' tag on the webpage which is the tag for links
        hyperLink = link.get('href')

        #assess if link is worth checking
        if link_assesment(hyperLink) == False:
            results["misc"].append(hyperLink)
            continue

        #properly format link
        if "http" not in hyperLink: 
            hyperlink_format_2 = url_segments.scheme + ':' + hyperLink
            hyperLink = base_url +'/' + hyperLink #add base URL

        #retrieve HTML page
        response = pageGetter(hyperLink, hyperlink_format_2)
        if response[0] == False:
            results["misc"].append(response[2])
            continue
        html_page = response[1]
        hyperLink = response[2]

        #scan webpage and store results
        if scan_HTMLpage(html_page): 
            visual(hyperLink, 1)
            results["hit"].append(hyperLink)
        else:
            visual(hyperLink, 0)
            results["missed"].append(hyperLink)
        

    return results


def scan_HTMLpage(html_page):
    '''
    scans a webpage for evidence of stream. only searches for video frames at the moment
    the function returns a boolean value that indicates wether or not a video frame was found
    '''
    soup_1 = bs(html_page, 'html.parser') #use beautful soup to procress HTML file
    script = soup_1.find('script', text=target_tag) #seraches HTML file for viedo frames
    if script: #if video frame is found
        return True
    else:
        return False


#Helper Functions

def pageGetter(url, second_url_format):
    #attempts to fetch HTML page.
    #returns a list containing: result [0], HTML page [1], link used [2]
    #if result == False, then link does not work
    try:
        HTMLpage = opener.open(url) #fetch HTML Page
        return [True, HTMLpage, url]
    except (HTTPError, ValueError, ParseError): #if page request fails
        if second_url_format == None:
            return [False, None, url]
        else:
            return pageGetter(second_url_format, None)

def link_assesment(hyperLink):
    #checks to see if the link is worth crawling
    if re.search(avoid, hyperLink):
        return False
    elif re.search(keywords, hyperLink):
        return True
    else:
        return False

def visual(hyperLink, result):
    #for printing out scan results during testing
     print("scanning " + hyperLink)
     if result == 1:
        print("!!!!!VIDEO FRAME FOUND!!!! \n")
     else:
        print("No Evidence Found \n")
     print('-----------------------------------------\n')

if __name__ == "__main__":
    try:
        url = sys.argv[1]
        main_func(url)
    except ParseError:
        print("Link Failed")