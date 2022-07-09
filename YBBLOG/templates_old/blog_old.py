"""from flask import Flask,render_template

app = Flask(__name__)
@app.route("/")
def index():
    article = dict()
    article["Title"] = "Deneme"
    article["Body"] = "Deneme2"
    article["Author"] ="Anıl Memiş"


    #sayi = 10
    #sayi2 = 20
    #return render_template("index.html", number = sayi,number2 = sayi2)
    return render_template("index.html", article = article)


@app.route("/about")
def about():
    return "Hakkımda Sayfası"

@app.route("/about/anil")
def about_person():
    return "anıl hakkında"


if __name__ == "__main__":
     app.run(debug=True)

"""