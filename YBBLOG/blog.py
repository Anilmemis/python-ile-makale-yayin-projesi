from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_login import current_user, login_user
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators,EmailField
import email_validator
from functools import wraps
from passlib.hash import sha256_crypt

#kullanıcı giriş decorater
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu sayfayı görüntülemeye yetkiniz yok. Giriş yapın.","danger")
            return redirect(url_for("login"))
    return decorated_function

#Kullanıcı kayıt formu
class RegistorForm(Form):
     name = StringField("İsim Soyisim",validators=[validators.length(min=4,max=25)])
     username = StringField("Kullanıcı Adı",validators=[validators.length(min=5,max=35)])
     email = StringField("E-Posta Adresiniz",validators=[validators.Email(message="Lütfen Geçerli Bir Mail Adresi Giriniz!"),validators.length(min=5,max=30)])
     password = PasswordField("Parolanız",validators=[
          validators.DataRequired(message="Lütfen bir parola belirleyin"),
          validators.EqualTo(fieldname="confirm",message="Parolanız Uyuşmuyor")])
     confirm = PasswordField("Password Doğrula")

#kullanıcı login formu
class LoginForm(Form):
     username = StringField("Kullanıcı Adınız")
     password = PasswordField("Şifreniz")

app = Flask (__name__)
app.secret_key = "ybblog"
mysql=MySQL(app)
app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_PASSWORD"]=""
app.config["MYSQL_DB"] ="ybblog"
app.config["MYSQL_CURSORCLASS"]="DictCursor"


@app.route("/")
def index():
    return render_template("index.html")
"""  articles = [
          {"id":1,"title":"Deneme1","content":"deneme1 içerik"},
          {"id":2,"title":"Deneme2","content":"deneme2 içerik"},
          {"id": 3, "title": "Deneme3", "content": "deneme3 içerik"},articles = articles
     ]"""
@app.route("/about")
def about():
     return  render_template("about.html")

@app.route("/dashboard")
@login_required
def dashboard():
    cursor = mysql.connection.cursor()
    sorgu = "Select * From articles where author = %s"
    result = cursor.execute(sorgu,(session["username"],))
    if result > 0:
        articles = cursor.fetchall()
        return render_template("dashboard.html",articles=articles)
    else:
        return render_template("dashboard.html")


    return render_template("dashboard.html")

#Kayıt Olma
@app.route("/register",methods = ["GET","POST"])
def register():
     form = RegistorForm(request.form)
     if request.method == "POST" and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(form.password.data)
        cursor = mysql.connection.cursor()
        sorgu1 = "Select * From users where username = %s"
        result = cursor.execute(sorgu1, (username,))
        if result == 0:
            sorgu2 = "Insert into users(name,username,email,password) VALUES (%s,%s,%s,%s)"
            cursor.execute(sorgu2,(name,username,email,password))
            mysql.connection.commit()
            cursor.close()
           #mesaj/bildiri
            flash("Başarıyla Kayıt Oldunuz.","success")
            return  redirect(url_for("login"))
        else:
                flash("Bu kullanıcı adına kayıtlı hesap mevcut.","danger")
                return render_template("register.html", form=form)
     else:
        return render_template("register.html", form=form)

#Login
@app.route("/login",methods = ["GET","POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
        username = form.username.data
        password_entered = form.password.data
        cursor = mysql.connection.cursor()
        sorgu = "Select * from users where username = %s "
        result = cursor.execute(sorgu,(username,))
        if result > 0:
            data = cursor.fetchone()
            real_password = data["password"]
            if sha256_crypt.verify(password_entered,real_password):
                flash("Başarı ile giriş yapıldı","success")
                session["logged_in"] == True
                if session["logged_in"] == True:
                    cursor = mysql.connection.cursor()
                    sorgu2 = "Select * from users where  username = %s and id "
                    result2 = cursor.execute(sorgu2, (username,))
                    session["id"] = result2[1]

                return redirect(url_for("index"))
            else:
                flash("Parolanızı yanlış girdiniz","danger")
                return redirect(url_for("login"))
        else:
            flash("Böyle bir kullanıcı bulunmuyor.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html",form = form)

class ProfileForm(Form):
    name = StringField("İsim Soyisim", validators=[validators.length(min=4, max=25)])
    username = StringField("Kullanıcı Adı", validators=[validators.length(min=5, max=35)])
    email = StringField("E-Posta Adresiniz",
                        validators=[validators.Email(message="Lütfen Geçerli Bir Mail Adresi Giriniz!"),
                                    validators.length(min=5, max=30)])
    password = PasswordField("Parolanız", validators=[
        validators.DataRequired(message="Lütfen bir parola belirleyin"),
        validators.EqualTo(fieldname="confirm", message="Parolanız Uyuşmuyor")])
    confirm = PasswordField("Password Doğrula")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    pass

#Çıkış/logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


#detay sayfası
@app.route("/article/<string:id>")
def article(id):
    cursor = mysql.connection.cursor()
    sorgu = "Select * From articles where id = %s"
    result = cursor.execute(sorgu,(id,))
    if result > 0:
        article = cursor.fetchone()
        return render_template("article.html",article=article)
    else:
        return render_template("article.html")


#makaleçekme/sorgulama
@app.route("/articles")
def detail():
     cursor = mysql.connection.cursor()
     sorgu = "Select * from articles"
     result = cursor.execute(sorgu)
     if result > 0:
         articles = cursor.fetchall()
         return render_template("articles.html",articles = articles)
     else:
         return render_template("articles.html")


#makaleform
class ArticleForm(Form):
    title= StringField("Makale Başlığı",validators=[validators.Length(min=5,max=100)])
    content = TextAreaField("Makale İçeriği",validators=[validators.Length(min=10)])

#makale ekle
@app.route("/addarticle",methods=["GET","POST"])
def addarticle():
    form = ArticleForm(request.form)
    if request.method == "POST" and form.validate():
        title = form.title.data
        content = form.content.data
        cursor = mysql.connection.cursor()
        sorgu = "Insert into articles(title,author,content) VALUES (%s,%s,%s)"
        cursor.execute(sorgu,(title,session["username"],content))
        mysql.connection.commit()
        cursor.close()
        flash("Makale başarıyla kaydedildi.","succsess")
        return redirect(url_for("dashboard"))
    return render_template("addarticle.html",form=form)

#makale silme
@app.route("/delete/<string:id>")
@login_required
def delete(id):
    cursor = mysql.connection.cursor()
    sorgu = "Select * From articles where author = %s and id = %s"
    result = cursor.execute(sorgu,(session["username"],id))
    if result > 0:
        sorgu2 = "Delete from articles where id = %s"
        cursor.execute(sorgu2,(id,))
        mysql.connection.commit()
        return redirect(url_for("dashboard"))
    else:
        flash("Böyle Makale Yok Veya Bu Makaleyi Silemye Yetkiniz Yok!","danger")
        return redirect(url_for("index"))

@app.route("/edit/<string:id>",methods =["GET","POST"])
@login_required
def update(id):
    if request.method == "GET":
        cursor = mysql.connection.cursor()
        sorgu = "select * from articles where id = %s and author = %s"
        result = cursor.execute(sorgu,(id,session["username"]))
        if result == 0:
            flash("Böyle bir makale yok veya bu işleme yetkiniz yok!","danger")
            return redirect(url_for("index"))
        else:
            article = cursor.fetchone()
            form = ArticleForm()
            form.title.data = article["title"]
            form.content.data = article["content"]
            return render_template("update.html",form = form)
    else:
        form = ArticleForm(request.form)
        newTitle = form.title.data
        newContent = form.content.data

        sorgu2 = "Update articles Set title = %s , content = %s where id = %s"
        cursor = mysql.connection.cursor()
        cursor.execute(sorgu2,(newTitle,newContent,id))
        mysql.connection.commit()
        flash("Makale Başarıyla Güncellendi","success")
        return redirect(url_for("dashboard"))

#makale arama url
@app.route("/search",methods =["GET","POST"])
def search():
    if request.method == "GET":
        return redirect(url_for("index"))
    else:
        keyword = request.form.get("keyword")
        cursor = mysql.connection.cursor()
        """sorgu = "Select * From articles where title = %s"""
        sorgu = "Select * from articles where title like '%"+ keyword + "%'"
        result = cursor.execute(sorgu)
        if result == 0:
            flash("Makale Bulunamadı","warning")
            return redirect(url_for("detail"))
        else:
            articles =cursor.fetchall()
            return render_template("articles.html",articles=articles)


if __name__ == "__main__":
     app.run(debug=True)

