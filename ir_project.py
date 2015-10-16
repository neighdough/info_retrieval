'''
*************************************************************************
*Name:
*Assignment: Assignment 5
*Description:
*Author: Nate Ron-Ferguson
*Date: October 16, 2015
*Comments:
    Assignment 2:
        Problem 1: input text resides in 'resources' directory included as 
        part of the final assignment. Directory will need to be changed if
        different input and output files are required.
    
        Problem 2: uses Beautiful Soup to parse class home page. If it's not
        already installed it can be installed using one of the following
        commands:  
        pip install beautifulsoup4
        easy_install beautifulsoup4
    
    Assignment 3:
        Problem 1 [20 points]. Design an extension of the basic Boolean model that 
        would allow for ranking of the retrieved documents. Be as detailed as possible.

        Problem 2 [30 points]. Write a Perl script that displays the vocabulary
        and frequency of each word in the main page of the class' website and
        on all other documents directly linked from the main page. For each
        word, also compute in how many different documents it occurs in this
        small collection. You must use hashes.
        
    Assignment 4:
        Problem 1 [30 points]. Write a Perl program that preprocesses a 
        collection of documents using the recommendations given in the 
        Text Operations lecture. The input to the program will be a directory
        containing a list of text files. Use the files from assignment #3 as
        test data as well as 10 documents (manually) collected from news.yahoo.com . 
        The yahoo documents must be converted to text before using them.
        
        Remove the following during the preprocessing:
        - digits
        - punctuation
        - stop words (use the generic list available at ...
            ir-websearch/papers/english.stopwords.txt)
        - urls and other html-like strings
        - uppercases
        - morphological variations   
        
    Assignment 5:
        Problem 1 [40 points]. Automatically collect from memphis.edu 10,000 
        unique documents. The documents should be proper after converting them to txt 
        (>50 valid tokens after saved as text); only collect .html, .txt, and and .pdf 
        web files and then convert them to text - make sure you do not keep any of 
        the presentation tags such as html tags. You may use third party tools to 
        convert the original files to text. Your output should be a set of 10,000 text 
        files (not html, txt, or pdf docs) of at least 50 textual tokens each. You must 
        write your own code to collect the documents - DO NOT use an existing crawler.
        
        Store for each proper file the original URL as you will need it later 
        when displaying the results to the user.
        
        Problem 2 [20 points]. Preprocess all the files using assignment #4. Save all
        preprocessed documents in a single directory which will be the input to
        the next assignment, index construction.
*************************************************************************
'''
import imp
for library in ['bs4', 'pdfminer', 'nltk']:
    try:
        imp.find_module(library)
    except:
        import sys
        error_msg = """
        \n
        *************************************************************************\n
        {0} is not installed, please run "pip install {0}" before running program.\n
        *************************************************************************
        \n"""
        sys.exit(error_msg.format(library))        


from bs4 import BeautifulSoup
import codecs
from collections import Counter, defaultdict, deque
import re
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from nltk.corpus import wordnet, stopwords
import nltk.stem
from nltk.stem.wordnet import WordNetLemmatizer
import os
import string
from StringIO import StringIO
import urllib2
from urlparse import urljoin

def in_domain(url):
    """
    check to make sure link is in uom domain
    """
    return 'memphis.edu' in url
    
def copy_text(infile=None, outfile=None):
    """
    Copies contents of document (text, pdf, html)  from one location to another
    
    parameters:
    infile -> string value representing input text file name (as .txt)
    outfile -> string value representing file to be written, 
                
    return -> None
    """  
    if infile:
        with open(infile, 'rt') as rd:
            reader = rd.read()  
    if outfile:
        with open(outfile, 'wt') as wt:
            wt.write(reader)    
         
def download(url, intext):
    print 'download ', url
    file_name = ''.join([t for t in url if t.isalpha() or t.isdigit() or t == ' ']).rstrip()    
    outfile = os.path.join('resources','original', file_name + '.txt')
    with open(outfile, 'wb') as wt:
        wt.write('#URL: {0}\n\n'.format(url))
        wt.write(intext.encode('utf-8'))

def preprocess(dir):
    """
    Cleans text and prepares it for future indexing by stripping the following:
    
        * numeric and other non-alphabetic characters
        * punctuation
        * stop words
        * urls and other html-like strings
        * uppercase values
        * morphological variations
    
    Input:
        dir -> root directory containing both original and copy directories 
    Output:
        word_list -> list of words without any affixes
    
    TODO:
    modify output to include url to document as first line
    """
    all_words = list()
    for infile in os.listdir(os.path.join(dir, 'original')):
        with codecs.open(os.path.join(dir, 'original',infile), encoding='utf-8') as f:
            url = f.readline()
            cur_text = f.read()
            
        print 'Results for ', infile, '\n\tLength before preprocessing: ', \
                len(nltk.word_tokenize(cur_text))
        #regex that searches for any url-like pattern
        http = """http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|\
        (?:%[0-9a-fA-F][0-9a-fA-F]))+|(w{3}\..+\.[a-z]{2,4})"""
        regex = '[^A-Za-z\s]+'#regex to remove any non-alphabetic character except whitespace
        txtclean = re.sub(http, '', cur_text)
        txtclean = re.sub(regex, ' ', txtclean)
        
        print '\tLength after regex: ', len(nltk.word_tokenize(txtclean))
        
        """remove all stopwords from text
            stopwords loaded from nltk stopword list
        """
        stpwrds = stopwords.words('english')    
        word_list = [re.sub(regex, '', word) for word in nltk.word_tokenize(txtclean) \
                     if not word in string.punctuation and not word in stpwrds]
        print '\tLength after stopwords: ', len(word_list)
        
        porter = nltk.PorterStemmer()
        print '\tStemming Results '
        for i, item in enumerate(word_list):
            word_list[i] = porter.stem(item).lower()
            print '\t', item, ' -> ', word_list[i]
        all_words.append(word_list)
        #rename input file and place in 'copy' directory
        outfile = os.path.splitext(infile.split('/')[-1])[0] + '.txt'
        """save cleaned version of current document to 'copy' directory"""
        with open(os.path.join(dir, 'copy', outfile), 'a') as wt:
            wt.write(url)
            wt.write(',\n'.join(word for word in word_list))            
    return all_words
        
def word_count(word_list):  
    """
        creates a hash table containing all unique words and number of occurrences
        
        Input:
            Required:
                word_list -> list of unique words
        Output:
            collections Counter object
    """
        
        
    word_count = Counter(word_list)  
    return word_count

def crawl(url):
    """
    Uses a queue to crawl all links found on current web page. As each link
    is popped off of the queue, it is opened and scanned for all links within
    the page. Each linked page is subsequently opened, extracted, saved 
    locally (in original directory), and preprocessed (in copy directory)
    
    parameters:
    url -> string of hyperlink for current document
    """
    queue = [url]
    visited = set([url])
    #Scans 'original' directory to check for 10,000 documents
    while len(os.listdir(os.path.join('resources','original'))) < docs:#len(queue) > 0 
        #checks to make sure that link is valid, outputs error with link if not
        try:
            page = urllib2.urlopen(queue[0])
            soup = BeautifulSoup(page.read(), 'html.parser')
        except Exception as e:     
            fd = open('errors.csv', 'a')
            fd.write(str(e) + ', ' + queue[0] + '\n')
            fd.close()
            queue.pop(0)   
        #remove link from queue    
        queue.pop(0)
        for link in soup.find_all(['a', re.compile('[^mailto]')]):
            new_url = link.get('href')
            if new_url and new_url[0] == '/':
                new_url = urljoin(url, new_url)
            """checks to verify that <a> tag is a link, not an anchor 
            AND that it's not a ppt 
            AND skip positional links (links with #)
            AND that it's in u of m domain
            AND that it's a new link
            AND that it's not an email link"""
            if new_url and not new_url.endswith('ppt') \
                and '#' not in new_url \
                and in_domain(new_url) \
                and new_url not in visited \
                and 'mailto' not in new_url:                    
                
                print '\t', len(queue), '\t', len(visited),'\t', new_url
                queue.append(new_url)                
                visited.add(new_url)
                doc_text = create_text(new_url)
                if keep(doc_text):
                    download(new_url, doc_text)   
    preprocess('resources')             
        
def pdf_to_text(pdf):
    """
    method to extract text from pdf document
    modified from example given at http://bit.ly/1KuNxYW
    Input:
        Required -> url to online pdf document
    Output:
        Raw string extracted from the pdf document
    """    
    #sets up the pdf object to extract text
    print "\nExtracting from a pdf, can be slow...\n"
    open_pdf = urllib2.urlopen(urllib2.Request(pdf)).read()
    pdf_string_io = StringIO(open_pdf)
    parser = PDFParser(pdf_string_io)
    pdf_doc = PDFDocument(parser)
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    
    #empty text string that content from pdf will be appended to
    txt = ''
    #iterates over each page in the pdf to extract text
    for page in PDFPage.create_pages(pdf_doc):
        interpreter.process_page(page)
        txt += retstr.getvalue()    
    return txt.decode('utf-8')

def word_freq_table(link_list):
    """
    Method to get full count of all words in search and their frequencies across
    all documents
    
    Input:
        link_list -> list returned from word_count method
    Output:
        dictionary (hash table) that contains each word and the number of documents
        that it appears in.
    """
    words_all = Counter()
    for words in link_list.itervalues():
        words_all.update(words.keys())
    return words_all    

def get_directory():
    """
    helper method to set working directory to ensure paths are correct for
    later referencing. Currently set up to only work on unix-based machines
    """
    import ir_project
    return '/'.join(dir for dir in ir_project.__file__.split('/')[:-1])

def create_text(url):
    """
    convert input url to raw string
    Parameters:
        Input:
            url -> string; full url for page to be indexed
            file_type -> string; file extension that determines how to handle input

        Output:
            txt -> raw string of content from page
    """

    """Tests whether link is active or not. If not, it returns a null value which is
        later used to remove broken links from hash table"""
    try:
        page = urllib2.urlopen(url)
        file_type = page.info().getmaintype()
    except urllib2.URLError as e:
            fd = open('errors.csv', 'a')
            fd.write(str(e) + ', ' + url + '\n')
            fd.close()
            return None
    #Handles text files
#     if file_type == 'txt':
#         txt = urllib2.urlopen(urllib2.Request(url)).read()
    #Handles pdf files
    if file_type == 'application':
        if page.info().subtype == 'pdf':
            txt = pdf_to_text(url)
        else:
            return None
    #Handles all other input types
    else: 
        page = urllib2.urlopen(url)        
        soup = BeautifulSoup(page.read(), 'html.parser')#creates webpage object to scrape for text    
        #list of script text to be extracted
        scripts = [script.text for script in soup.find_all('script') if script != '\n']
        txt = soup.text
        for script in scripts:
            if script in txt:
                txt = txt.replace(script, '')        
    return txt

def keep(converted_text):
    """
    perform quick check on document to determine if it contains required
    number of tokens (50)
    
    Parameters:
        Input:
            converted_text -> document converted to string
        Output:
            boolean to retain document, or to toss it
    """
    try:
        return len(nltk.word_tokenize(converted_text)) >= 50
    except:
        return False
        
if __name__ == '__main__':
    
    cur_dir = get_directory()
    os.chdir(cur_dir)
    
    if not os.path.exists(os.path.join(cur_dir, 'resources/nltk_data')):
        import sys
        error_msg = """\n\n
        **************************************************************\n
        Assignment 4 uses data from the Natural Language Toolkit.\n\
        The necessary files have been included in an updated copy \n\
        of the resources directory. Please download a new copy at:\n\n
        https://www.dropbox.com/s/v67p3s03lfximtd/resources.zip?dl=0\n
        Once downloaded, place in the same directory as ir_project.py.\n
        *****************************************************************
        \n\n"""
        sys.exit(error_msg)
    else:
        nltk.data.path = [os.path.join('resources','nltk_data')]
    
    url = 'http://www.memphis.edu'
    docs = 10000
    crawl(url)


    
