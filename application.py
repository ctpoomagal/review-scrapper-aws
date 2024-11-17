from flask import Flask, render_template, request,jsonify
# from flask_cors import CORS,cross_origin
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
from util import resp
import logging as lg
lg.basicConfig(filename="scrapper.log",  level=lg.INFO)

application=Flask(__name__)
app=application

#Route
@app.route("/", methods=["GET"])
def homepage():
    # return "Hello All!!!"
    return render_template("index.html")


@app.route("/review", methods=["GET", "POST"])
def index():
    if request.method=="POST":
        try:
            searchString=request.form['content'].replace(" ", "")
            flipcart_url= "https://www.flipkart.com/search?q=" + searchString
            uClient=resp(flipcart_url)
            flipcartpage=uClient.read()
            flipcart_html=bs(flipcartpage, "html.parser")
            bigboxes=flipcart_html.findAll("div", {"class": "cPHDOP col-12-12"})
            del bigboxes[0:3]
            box=bigboxes[0]
            prodlink="http://www.flipkart.com"+box.div.div.div.a["href"]
            prodres=resp(prodlink)
            prodcontent=prodres.read()
            prod_html=bs(prodcontent, "html.parser")
            prodrevs=prod_html.findAll("div", {"class": "RcXBOT"})

            filename= searchString + ".csv"
            fw=open(filename, "w")
            headers= "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews=[]
            for i in prodrevs:
                try:
                    name=i.div.div.find_all("p", {"class" : "_2NsDsF AwS1CA"})[0].text
                except:
                    name="No Name"
                try:
                    rating=i.div.div.div.div.text
                except:
                    rating= "No Rating"
                try:
                    cmthead= i.div.div.div.p.text
                except:
                    cmthead="No comment Head"
                try:
                    commenttag=i.div.div.find_all("div", {"class" : ""})
                    comment=commenttag[0].div.text
                except Exception as e:
                    comment= "No Comment"
                    lg.info("Exception while creating dictionary")
                
                mydict= {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": cmthead,
                         "Comments": comment}
                reviews.append(mydict)
                lg.info("log my final result {}".format(reviews))
            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            lg.info(f"The exception message is {e}")
            return "Something is wrong"
    else:      
        return render_template("index.html")


if __name__=="__main__":
    # app.run(host="127.0.0.1")
    app.run(host="0.0.0.0", port=5000)
