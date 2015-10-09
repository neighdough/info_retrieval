'''
*************************************************************************
*Name:
*Assignment: Assignment 4
*Description:
*Author: Nate Ron-Ferguson
*Date: October 08, 2015
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

import urllib2
from bs4 import BeautifulSoup
import codecs
from collections import Counter, defaultdict
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
         
def download(url, file_type=None):
    """
    Receives an input url and splits page using whitespace. It does handle basic regex
    expressions to eliminate special characters including punctuation.
    
    Input:
        Required:
            url -> string; full url for page to be indexed
        Optional:
            file_type -> string; file extension that determines how to handle inpout
    Output:
        hash table containing words as key values matched with respective frequency
    """
    
    """Tests whether link is active or not. If not, it returns a null value which is
        later used to remove broken links from hash table"""
    try:
        urllib2.urlopen(url)
    except urllib2.URLError:
        return None
    #Handles text files
    if file_type == 'txt':
        txt = urllib2.urlopen(urllib2.Request(url)).read()
    #Handles pdf files
    elif file_type == 'pdf':
        txt = pdf_to_text(url)
        url = url.replace('.pdf', '.txt')
    #Handles all other input types
    else:    
        page = urllib2.urlopen(url)        
        soup = BeautifulSoup(page.read(), 'html.parser')#creates webpage object to scrape for text    
        txt = ''
        for tag in soup.find_all('p'):
            txt += tag.text + '\n'
    
    outfile = os.path.join('original', os.path.splitext(url.split('/')[-1])[0] + '.txt')
    with open(outfile, 'wb') as wt:
        wt.write(txt.encode('utf-8'))

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
    """
    all_words = list()
    for infile in os.listdir(os.path.join(dir, 'original')):
        with codecs.open(os.path.join(dir, 'original',infile), encoding='utf-8') as f:
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
        with open(os.path.join(dir, 'copy', outfile), 'wb') as wt:
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

def crawl_links(url):
    """
    Uses input url to search for all hyperlinks in order to create dictionary(hash table)
    of which words each page containwith open(os.path.join(dir, 'copy', infile), 'wb') as f:s and the frequency of each word within that page
    
    Input:
        Required:
            url -> string representing url for the base page that will serve as the
                starting point for the search
    Output:
        Dictionary (hash table) with the following structure:
            {Web Page: {word: count}}
    """
    print "\nCalculating frequency for ", url
    #initializes starting url to begin the search
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page.read(), 'html.parser')
    #initializes dictionary that will contain each site with its word count
    link_list = defaultdict(lambda: defaultdict())
    link_list[url] = word_count(url)#adds base(class home page) page to dictionary
    for link in soup.find_all('a'):
        """checks to verify that <a> tag is a link, not an anchor 
            AND that it's not a ppt 
            AND skip positional links (links with #)"""
        if link.get('href') and not link.get('href').endswith('ppt') and '#' not in link.get('href'):
            cur_url = link.get('href')#current url to be indexed
            file_type = cur_url.split('.')[-1]#gets file extension if it exists
            """checks the file type to determine whether the document address needs
                to be appended to the base page, or if it is a stand alone page"""
            if not file_type in ('txt', 'pdf', 'html'):#stand alone page
                download(cur_url)
            else:#needs to be appended to base site for full url
                download(url + cur_url, file_type)
    
    """clean up link_list to remove any broken or missing links"""
    for link in link_list.keys():
        if link_list[link] is None:
            del link_list[link]    
    return link_list
       
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
    import ir_project
    return '/'.join(dir for dir in ir_project.__file__.split('/')[:-1])
    
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
    preprocess(os.path.join(cur_dir, 'resources'))


    
