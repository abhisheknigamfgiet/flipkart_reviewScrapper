# doing necessary imports

from flask import Flask, render_template, request,jsonify
# from flask_cors import CORS,cross_origin
#from lxml import html
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

app = Flask(__name__)  # initialising the flask app with the name 'app'

@app.route('/', methods=['GET'])
def homepage():
    return render_template('index.html')

# base url + /
#http://localhost:8000 + /
@app.route('/scrap',methods=['POST']) # route with allowed methods as POST and GET
def index():
    if request.method == 'POST':
        searchString = request.form['content'].replace(" ","+") # obtaining the search string entered in the form
        #searchString = request.form['content']  # obtaining the search string entered in the form
        try:
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString # preparing the URL to search the product on flipkart
            uClient = uReq(flipkart_url) # requesting the webpage from the internet
            flipkartPage = uClient.read() # reading the webpage
            uClient.close() # closing the connection to the web server
            flipkart_html = bs(flipkartPage, "html.parser") # parsing the webpage as HTML
            #bigboxes = flipkart_html.findAll("div", {"class": "bhgxx2 col-12-12"}) # seacrhing for appropriate tag to redirect to the product link
            bigboxes = flipkart_html.findAll("div", {"class": "_13oc-S"})
            #del bigboxes[0:3] # the first 3 members of the list do not contain relevant information, hence deleting them.
            box = bigboxes[0] #  taking the first iteration (for demo)
            productLink = "https://www.flipkart.com" + box.div.div.a['href'] # extracting the actual product link
            prodRes = requests.get(productLink) # getting the product page from server
            prod_html = bs(prodRes.text, "html.parser") # parsing the product page as HTML
            #commentboxes = prod_html.find_all('div', {'class': "_3nrCtb"}) # finding the HTML section containing the customer comments
            #commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})  # finding the HTML section containing the customer comments
            reviewboxes = prod_html.find_all('div', {'class': "col JOpGWq"})  # finding the HTML section containing the customer comments
            #tree = html.fromstring(prodRes.content)
            # This will create a list of buyers:
            #reviewMore = tree.xpath('/html/body/div[1]/div/div[3]/div[1]/div[2]/div[9]/div[7]/div/a/@href')
            for review in reviewboxes:
                reviewMore = review.find_all('a', {'class': ''})
            reviewLink = "https://www.flipkart.com" + reviewMore[10]['href']
            reviewRes = requests.get(reviewLink)  # getting the product page from server
            review_html = bs(reviewRes.text, "html.parser")  # parsing the product page as HTML
            product_fetched = review_html.find_all('div', {'class': "_2s4DIt _1CDdy2"})  # finding the HTML section containing the customer comments
            for product in product_fetched:
                product_name = product.text

            reviews = [] # initializing an empty list for reviews
            matchNext = "Next"
            while matchNext == 'Next':
                commentboxes = review_html.find_all('div', {'class': "_1AtVbE col-12-12"})  # finding the HTML section containing the customer comments
                del commentboxes[0:4]
                #iterating over the comment section to get the details of customer and their comments
                for commentbox in commentboxes[0:len(commentboxes)-1]:
                    try:
                        #name = commentbox.div.div.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text
                        name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                    except:
                        name = 'No Name'

                    try:
                        rating = commentbox.div.div.div.div.div.text

                    except:
                        rating = 'No Rating'

                    try:
                        commentHead = commentbox.div.div.div.p.text
                    except:
                        commentHead = 'No Comment Heading'
                    try:
                        comtag = commentbox.div.div.find_all('div', {'class': ''})
                        custComment = comtag[0].div.text
                    except:
                        custComment = 'No Customer Comment'
                    #fw.write(searchString+","+name.replace(",", ":")+","+rating + "," + commentHead.replace(",", ":") + "," + custComment.replace(",", ":") + "\n")
                    mydict = {"Product": product_name[0:-8], "Name": name, "Rating": rating, "CommentHead": commentHead,
                              "Comment": custComment} # saving that detail to a dictionary
                    # x = table.insert_one(mydict) #insertig the dictionary containing the rview comments to the collection
                    reviews.append(mydict) #  appending the comments to the review list

                whileNext = ''
                #whileNext = review_html.find_all('a', {'class': '_1LKTO3'})
                whileNext = review_html.find_all('a', {'class':'_1LKTO3'})
                i = 0
                for resultset in whileNext:
                    i = i+1
                if i > 1:
                    whileNext_value = review_html.find_all('a', {'class':'_1LKTO3'})[1].span.text
                    whileNext = review_html.find_all('a', {'class': '_1LKTO3'})[1]
                else:
                    whileNext_value = review_html.find_all('a', {'class':'_1LKTO3'})[0].span.text
                    whileNext = review_html.find_all('a', {'class': '_1LKTO3'})[0]
                if whileNext_value == 'Previous':
                    matchNext = 'Not Next'
                else:
                    reviewLink = "https://www.flipkart.com" + whileNext.get('href')
                    reviewRes = requests.get(reviewLink)  # getting the product page from server
                    review_html = bs(reviewRes.text, "html.parser")
                    matchNext = 'Next'

            return render_template('results.html', reviews=reviews) # showing the review to the user
        except:
            return 'something is wrong'


if __name__ == "__main__":
    app.run(port=8000,debug=True) # running the app on the local machine on port 8000