from bs4 import BeautifulSoup
from urllib2 import urlopen
from xhtml2pdf import pisa
import os, httplib2, re


class G4GExtractor:
    __BASE_WEB_URL = 'http://www.geeksforgeeks.org/category/'
    __FILE_SAVE_PATH = ''
    __CURR_DIR_PATH = os.path.dirname(os.path.realpath(__file__)) + '/'

    def __init__(self, path=''):
       
        if len(path.strip()) == 0:
            self.__FILE_SAVE_PATH = self.__CURR_DIR_PATH
        elif os.path.exists(path) and os.access(path, os.W_OK):
            self.__FILE_SAVE_PATH = path
        else:
            raise Exception("Either the supplied path doesn't exists or you don't "
                            "have write permissions. \n Check the directory write "
                            "permissions and try again later. Thank You")

    def set_filesave_path(self, path):
        
        if os.path.exists(path) and os.access(path, os.W_OK):
            self.__FILE_SAVE_PATH = path
        else:
            raise Exception("Either the supplied path doesn't exists or you don't "
                            "have write permissions. \n Check the directory write "
                            "permissions and try again later. Thank You")

    def set_baseweburl_path(self, url):
        
        self.__BASE_WEB_URL = url

    def __valid_webpage(self,urllink):

        h = httplib2.Http()
        resp = h.request(urllink, 'HEAD')
        return int(resp[0]['status']) == 200

    def __remove_non_ascii(self,text):
        
        return ''.join([i if ord(i) < 128 else '' for i in text])

    def extract_content_and_save(self, cat_list, pdf=False):
       

        #List to store all the links.
        totallinks = []

        #String to store html code
        pagedata = ''

        #Iterate for each category
        for cat in cat_list:
            #Create Directory path.
            newpath = self.__FILE_SAVE_PATH + cat

            #Create Directory for each category.
            os.mkdir(newpath)

            #Prepare URL to extract number of pagination pages
            url = self.__BASE_WEB_URL + cat + "/"

            #Check if webpage exists and is valid
            if self.__valid_webpage(url):
                pagedata = urlopen(url).read()
                soup = BeautifulSoup(pagedata)

                #Get number of Pagination pages for each category
                pages = soup.find('span', {"class": "pages"})
                if pages:
                    cat_content_pages = int(str(pages.text).split()[3])
                else:
                    cat_content_pages = 1

                for i in range(1, cat_content_pages + 1):

                    listofLinks = []

                    #Prepare URL to extract links
                    if i == 1:
                        url = self.__BASE_WEB_URL + cat + "/"
                    else:
                        url = self.__BASE_WEB_URL + cat + "/page/" + str(i) + "/"

                    print("Working with %s" % url)
                    print "Sarthak"

                    #Check if the webpages have Status 200 or 404
                    if self.__valid_webpage(url):
                        pagedata = urlopen(url).read()
                        soup = BeautifulSoup(pagedata)

                        #Find all the title links in the page
                        content_links = soup.findAll("h2", class_="entry-title")

                        #Iterate every page and save the content links in a list
                        for link in content_links:
                            mainLink = \
                                str(link.findAll("a")[0]).split("<a href=")[1].split('rel="bookmark"')[0].strip(
                                    '"').split(
                                    '"')[0]
                            listofLinks.append(mainLink)
                            print "Going to save data"
                            self.save_pages(listofLinks, newpath)
                        totallinks.append(listofLinks)
                    else:
                        print url + ' Returned Status 404'
            else:
                print url + ' Returned Status 404'

		print "Returning from save and extract data"
        return totallinks

    def save_pages(self, listoflinks, newpath, pdf=False):

        for link in listoflinks:
            pagedata = urlopen(link).read()
            soup = BeautifulSoup(pagedata)
            title = soup.find('h1', {"class": "entry-title"})
            print link

            #Create File name to be saved as
            filename = re.sub('[^a-zA-Z0-9\n\.]', '_', title.text)

            #If path ends with trailing slash then remove it.
            if newpath.endswith('/'):
                newpath = newpath[:len(newpath) - 1]

            try:
                if os.path.exists(newpath):
                    filePath = newpath + "/" + filename
                    with open(filePath + '.html', "wb") as f:
						f.write(self.__remove_non_ascii(pagedata))

            except OSError as e:
                print(e.message)

    
    def convertHtmlToPdf(self,sourceHtml, outputFilename):
       
        resultFile = open(outputFilename, "w+b")

        # convert HTML to PDF
        pisaStatus = pisa.CreatePDF(sourceHtml, dest=resultFile)

        # close output file
        resultFile.close()

        # return True on success and False on errors
        return pisaStatus.err

def demo():
    """
    A demo run if this app.
    """
    demo_cat_list = ['Array']
    path = '/root/PycharmProjects/GeekForGeeks-Spider/'
    demo = G4GExtractor()
    totallinks = len(demo.extract_content_and_save(demo_cat_list,True))
    print("Number of links crawled and saved is %d" % totallinks)
if __name__ == '__main__':
    demo()
