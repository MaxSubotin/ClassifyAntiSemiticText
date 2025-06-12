import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QTableWidgetItem, QStyledItemDelegate
from PyQt5.QtCore import Qt
from pymongo import MongoClient
from tiktokScraper import *
from redditScraper import *

################################
# Authors:                     #
#   Maxim Subotin - 207695479  #
#   Amiel Cohen - 315196311    #
################################

class ScraperApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        # load UI file 
        uic.loadUi('redditTiktokScraperUI.ui', self)
        
        # center the window on the screen
        self.centerWindow()

        # connecting buttons to click events
        self.scrapeFromRedditButton.clicked.connect(self.scrapeFromRedditButtonClicked)
        self.scrapeFromTikTokButton.clicked.connect(self.scrapeFromTikTokButtonClicked)
        self.showResultsFromRedditButton.clicked.connect(self.showResultsFromRedditButtonClicked)
        self.showResultsFromTikTokButton.clicked.connect(self.showResultsFromTikTokButtonClicked)

        # clear the table widget data
        self.setupTable()

        # initialize the connection to the MongoDB server
        try:
            self.initLocalMongoDBServer()
        except Exception as e:
            print(f'Encountered some exception when trying to initialize the local MongoDB server, make sure it is up and running and has correct tables. Exception: {e}')

        # initialize the Reddit Scraper
        self.redditScraper = RedditScraper(
            keywords=['jew', 'jews', 'zionist', 'zionism', 'zion', 'mosad', 'zio', 'kike', 'heeb', 'yid', 'isreal' ,'holocaust', 'holohoax', 'cabal', 'genocide', 'zog', 'occupied', 'occupation', 'nazi', 'jewish', 'zion', 'idf', 'palestine'],
            subreddits=['conspiracy', 'worldnews', 'politics', 'IsraelPalestine', 'AskReddit']
        )

        keywords = [
            'jew', 'jews', 'jewess', 'jewish', 'israel', 'isreal', 'israhell', 'idf',
            'zionist', 'zionists', 'zionism', 'zion', 'zio', 'zioist', 'zionazi', 'nazi',
            'mossad', 'mosad', 'palestine', 'holocaust', 'holohoax', 'hollowhoax', 'shoah', 'shoax',
            'auschwitz', 'treblinka', 'nuremberg', 'kike', 'heeb', 'yid', 'shylock', 'hooknose',
            'goy', 'goyim', 'gentile', 'gentiles', 'bloodlibel', 'zog', 'rothschild', 'circumcision',
            'talmud', 'chosen', 'synagogue', 'occupation', 'occupied', 'genocide'
        ]

        # initialize the TikTok Scraper
        self.tiktokScraper = TikTokScraper()

    #------------------------------------------------------------------------------------------------#
    #---------------------------------------Click-Events---------------------------------------------#
    
    # collect a bit of data from Reddit and save it to the database (collecting posts and comments with the above key words from the above sub reddits)
    def scrapeFromRedditButtonClicked(self):
        print('Starting to scrape from Reddit...')
        collected_posts = self.redditScraper.collect_data()#posts_limit=2, comments_limit=3)
        if collected_posts:
            # for post in collected_posts: #inserts the collected posts straight to the table
            #     self.insertRowToTable(post)
            self.reddit_db_collection.insert_many(collected_posts) #insert the collected tweets to the database
        print(f'Collected {len(collected_posts)} posts from Reddit.')


    # collect a bit of data from TikTok and save it to the database (collecting comments from trending videos on tiktok, just general comments without any filters)
    def scrapeFromTikTokButtonClicked(self):
        print('Starting to scrape from TikTok...')
        collected_comments = asyncio.run(self.tiktokScraper.collect_data(video_count=3, comments_per_video=5))
        if collected_comments:
            # for comment in collected_comments: #inserts the collected comments straight to the table
            #     self.insertRowToTable(comment)
            self.tiktok_db_collection.insert_many(collected_comments) #insert the collected tweets to the database
        print(f'Collected {len(collected_comments)} comments from TikTok.')


    # show ALL the collected data from Reddit to the screen
    def showResultsFromRedditButtonClicked(self):
        print('Loading data from Reddit collection...')
        self.loadDataFromMongodbCollection(self.reddit_db_collection)
        self.resultsLabel.setText('Results From Reddit Scraper:')
        self.updateTableWidget()


    # show ALL the collected data from TikTok to the screen
    def showResultsFromTikTokButtonClicked(self):
        print('Loading data from TikTok collection...')
        self.loadDataFromMongodbCollection(self.tiktok_db_collection)
        self.resultsLabel.setText('Results From TikTok Scraper:')
        self.updateTableWidget()

    #------------------------------------------------------------------------------------------------#
    #------------------------------------Database-Functions------------------------------------------#

    # initialize the local MongoDB server and create collections if they dont already exist
    def initLocalMongoDBServer(self):
        client = MongoClient('localhost', 27017)
        tiktok_db = client.tiktok_comments
        self.tiktok_db_collection = tiktok_db.tiktok_comments
        reddit_db = client.reddit_comments
        self.reddit_db_collection = reddit_db.reddit_comments


    # fetch all documents from a MongoDB collection and insert them into a QTableWidget
    def loadDataFromMongodbCollection(self, collection):
        try:
            # get all documents from MongoDB
            data = list(collection.find())

            # clear existing table content
            self.resultsTableWidget.setRowCount(0)

            if not data:
                print('No data found in the MongoDB collection.')
                return

            # extract column names from the first document
            columns = list(data[0].keys()) #MongoDB documents use dictionaries
            columns = columns[1:] #remove the _id column that the MongoDB adds to each element in the collection

            # Insert each document as a new row
            for document in data:
                row_data = [str(document.get(col, 'N/A')) for col in columns] #convert values to strings
                self.insertRowToTable(row_data)

            self.adjustColumnSizes()
            print(f'Successfully loaded {len(data)} documents into the table.')
        except Exception as e:
            print(f'Error loading data from MongoDB: {e}')

    #------------------------------------------------------------------------------------------------#
    #-------------------------------------Helper-Functions-------------------------------------------#

    # center the application window
    def centerWindow(self):
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        window_rect = self.frameGeometry()
        window_rect.moveCenter(screen.center())
        self.move(window_rect.topLeft())


    # setup the table widget correctly
    def setupTable(self):
        self.resultsTableWidget.setRowCount(0)
        self.resultsTableWidget.setColumnCount(6)

        # set column headers
        column_names = ['ID', 'Username', 'Message', 'Likes', 'Timestamp', 'Link']
        self.resultsTableWidget.setHorizontalHeaderLabels(column_names)
        
    
    # helper function to show the data in the table properly
    def updateTableWidget(self):
        self.resultsTableWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn) #always show scrollbars
        self.resultsTableWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.resultsTableWidget.setSizeAdjustPolicy(self.resultsTableWidget.AdjustToContents)
        self.resultsTableWidget.setWordWrap(True)
        self.resultsTableWidget.setItemDelegate(QStyledItemDelegate()) #prevents eliding
        self.resultsTableWidget.resizeColumnsToContents() #adjust column sizes
        self.resultsTableWidget.resizeRowsToContents() #adjust row sizes


    # inserts a dictionary as a new row at the end of the table
    def insertRowToTable(self, dataDict):
        row_position = self.resultsTableWidget.rowCount()
        self.resultsTableWidget.insertRow(row_position)

        for col, value in enumerate(dataDict):
            item = QTableWidgetItem(str(value))
            self.resultsTableWidget.setItem(row_position, col, item)


    # adjusts column sizes to fit content
    def adjustColumnSizes(self):
        self.resultsTableWidget.resizeColumnsToContents()
        self.resultsTableWidget.horizontalHeader().setStretchLastSection(True)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = ScraperApp()
    window.show()
    sys.exit(app.exec_())