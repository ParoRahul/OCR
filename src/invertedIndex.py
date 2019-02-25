# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 16:24:46 2018

@author: 683898
"""

import redis
import nltk
from nltk.stem.snowball import EnglishStemmer
from configparser import ConfigParser
import utility as ut
import sys
from os import listdir
from os.path import exists,join,isfile,basename

class Index:
    """ Inverted index datastructure """

    def __init__(self, tokenizer=nltk.word_tokenize,
                 stemmer=EnglishStemmer(),
                 stopwords=nltk.corpus.stopwords.words('english')):
        """Create an inverted index.

        Args:
          tokenizer -- NLTK compatible tokenizer function
          stemmer   -- NLTK compatible stemmer
          stopwords -- list of ignored words
        
        Methods:
          lookup  --   Look up words in the index; return the intersection of the hits.     
          print_lookup --- Print lookup results to stdout.
          document_is_processed -- Check whether a document (image file) has 
                                   already been processed.
          document_is_processed -- Add bookkeeping to indicate that the given 
                                   file had no discernible text.                         
          ADD -- Add a document string to the index.                         
        """

        # db 0 holds the token (words) inverted index.
        self.redis_token_client = redis.StrictRedis(db=0)
        # db 1 holds the filename--> text mapping.
        self.redis_docs_client = redis.StrictRedis(db=1)
        # Do an initial check on the redis connection. If redis is not up,
        # the constructor call will fail.
        #print(self.redis_token_client.client_getname())
        self.redis_docs_client.ping()
        self.tokenizer = tokenizer
        self.stemmer = stemmer
        self.__unique_id = 0
        self.stopwords = set(stopwords) if stopwords else set()

    def lookup(self, *words):
        """Look up words in the index; return the intersection of the hits."""
        conjunct = set()

        for word in words:
            word = word.lower()

            if self.stemmer:
                word = self.stemmer.stem(word)

            docs_with_word = self.redis_token_client.smembers(word)
            hits = set([
                (id, self.redis_docs_client.get(id))
                for id in docs_with_word
            ])
            conjunct = conjunct & hits if conjunct else hits
        return conjunct
    
    def delete_key(self):
        self.redis_token_client.flushall()
        self.redis_docs_client.flushall()
        self.redis_docs_client.flushdb()
        self.redis_token_client.flushdb()

    def print_lookup(self, *words):
        """Print lookup results to stdout."""
        hits = self.lookup(*words)
        if not hits:
            print("No hits found.")
            return
        for i in hits:
            print("*** %s has text:\n%s" % i)

    def document_is_processed(self, filename):
        """Check whether a document (image file) has already been processed."""
        res = self.redis_docs_client.get(filename)
        if res:
            print("%s already added to index." % filename)
            return True
        if res == '':
            print('File %s was already checked, and contains no text.'
                  % filename)
            return True
        return False

    def set_contains_no_text(self, filename):
        """Add bookkeeping to indicate that the given file had no discernible text."""
        self.redis_docs_client.set(filename, '')

    def add(self, filename, document):
        """
        Add a document string to the index.
        """
        # You can uncomment the following line to see the words found in each
        # image.
        # print("Words found in %s: %s" % (filename, document))
        for token in [t.lower() for t in nltk.word_tokenize(document)]:
            if token in self.stopwords:
                continue
            if token in ['.', ',', ':', '']:
                continue
            if self.stemmer:
                token = self.stemmer.stem(token)
            # Add the filename to the set associated with the token.
            self.redis_token_client.sadd(token, filename)
        # store the 'document text' for the filename.
        self.redis_docs_client.set(filename, document)
        
        
        
if __name__ == '__main__': 
     try:
        configFile = ConfigParser()
        configFile.read(ut.API_CONFIG_FILE)
        #input image output DOC and Json Paths
        DB_DIR = configFile.get('DB.Paths','DBDOCPath')
        JSON_DIR = configFile.get('OCR.Paths','jsonpath')

        #TYpe of DOC and Other DEFAULT parameters
        MAKE_JSON = configFile.getboolean('OCR.DEFAULT','makejson')
        DOC_TYPE = configFile.get('OCR.DEFAULT','DB_DOC_TYPE')
        TEMPDIR = configFile.get('DB.Paths','TEMPDIR')
     except ConfigParser.ParsingError as e:
         sys.exit(e)
     except Exception as e:    
         sys.exit(e)     
     else:
         print('CONFIG FILE LOADED SUCESSFULLY ')
     finally:
         pass       
     index = Index()
     allfileslist = [join(DB_DIR,file) for file in listdir(DB_DIR) 
                          if isfile(join(DB_DIR, file))]
     # Recursively construct a list of all the files in the given input
     # directory.
    
     fileslist = []
     for filename in allfileslist:
         # Look for text in any files that have not yet been processed.
         if index.document_is_processed(basename(filename)):
             continue
         fileslist.append(filename)
     print(" Total number of "+str(len(fileslist)))
     for filename in fileslist:
         with open(filename) as file:
              document = file.read()
              if document:
                  input_filename=basename(filename).split('.')[0]
                  index.add(input_filename, document)
                  sys.stdout.write('.')
                  sys.stdout.flush()
              else:
                  if document == []:
                     print('%s had no discernible text.' % input_filename)
                     index.set_contains_no_text(input_filename)
#import invertedIndex
#>>> index = invertedIndex.Index()
#>>> index.print_lookup('cats')
#...
#>>> index.print_lookup('cats', 'dogs')             