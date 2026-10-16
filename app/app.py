from flask import Flask, render_template ,request, redirect, session, jsonify
import sqlite3, os
from werkzeug.security import generate_password_hash
from datetime import datetime
import math
app = Flask(__name__)
app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "local-development-key-change-me"
)
database_dir = "vfilm.db"


def create_connection():
    conn = sqlite3.connect(database_dir)
    return conn

def bringMovies(order):
    dic = {
        'recent' : lambda : """SELECT * FROM Movies
                            ORDER BY id DESC LIMIT 12""",
        'asc' : lambda : """SELECT * FROM Movies
                            ORDER BY id asc""",
        'view' : lambda : """SELECT * FROM Movies
                            ORDER BY view"""}
    query = dic[order]()
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(str(query))
    filmler = cursor.fetchall()
    conn.close()
    return filmler

def bringTheMovie(id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Movies WHERE id = ?",(id,))
    movie = cursor.fetchone()
    conn.close()
    return movie

def bringWL(userid):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT WList FROM User WHERE id = ?",(userid,))
    Wlist = cursor.fetchone()
    conn.close()
    return Wlist[0]

def checkWL(userid,mid):
    wl=bringWL(userid)
    wlist=wl.split(',')
    p=False
    for i in wlist:
        if i==str(mid):
            p=True
            break
        else:
            p=False
    return p

def bringuser(userid):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM User WHERE id = ?",(userid,))
    user=cursor.fetchone()
    conn.close()

    return user

def veli(mid):
    movie=bringTheMovie(mid)
    viewSum = int(movie[11])
    viewSum += 1
    connection=create_connection()
    cursor=connection.cursor()
    cursor.execute("""UPDATE Movies 
                    SET viewCounter = ? Where id = ? """,(viewSum,movie[0]))
    connection.commit()
    connection.close()

def sendMsg(data):
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO messages(AdSoyad, mail, phone_number, message) VALUES (?,?,?,?)",
        (data[0], data[1], data[2], data[3])
    )

    connection.commit()
    connection.close()

@app.route("/contacts")
def iletisim():
    if "user_id" in session:
        uid = session["user_id"]
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT name_sname, email FROM User WHERE id=?",
            (uid,)
        )
        user_data = cursor.fetchone()
        connection.close()
        return render_template("contacts.htm", logged=True, user=user_data)
    else:
        return render_template("contacts.htm")



@app.route("/sendMsg", methods=["POST"])
def send_message():
    try:
        data = request.get_json()
        msgData = data["msgData"]

        sendMsg(msgData)

        return jsonify({"status": "success"})

    except Exception as e:
        print("SEND MESSAGE ERROR:", e)
        return jsonify({"status": "error"}), 500

@app.route("/") 
def anasayfa():
    filmler = bringMovies('recent')
    if "user_id" in session:
        return render_template("mainpage.htm", logged=True, userid=session["user_id"], movies = filmler)
    elif "user_ad" in session:
        ad = session["user_ad"]  
        conn = create_connection()
        cursor = conn.cursor()
    
    
        cursor.execute("""
                        SELECT id FROM User
                        WHERE name_sname = ?
                        """, (ad,))
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            return render_template("mainpage.htm", logged=True, userid=session["user_id"], movies = filmler)
        else:
            
            return redirect("/login")  

    else:
        return render_template("mainpage.htm",logged=False, movies = filmler)

@app.route("/register",methods=["GET","POST"]) 
def kayitol():
    if request.method == "POST":
        name = request.form["inp_name"] + " " + request.form["inp_surname"]
        mail = request.form["inp_mail"]
        password = request.form["inp_password"]
        date = datetime.now()
        date = str(date).split(" ")

        if not name.strip() or not mail.strip() or not password.strip():
            return render_template("register.htm",error="Lütfen tüm alanları doldurunuz!")

        if len(password) < 6:
            return render_template("register.htm",error="Şifre en az 6 karakter olmalıdır!")

        connection = create_connection()
        cursor = connection.cursor()
        
        cursor.execute("SELECT * FROM User WHERE email = ? ",(mail,))
        existing_user = cursor.fetchone()
        if existing_user:
            connection.close()
            return render_template("register.htm",error="Bu e-posta zaten kayıtlı!")
        
        
        cursor.execute("""
                        INSERT INTO User
                        (name_sname, email, password, date)
                        VALUES (?,?,?,?)
                        """,(name,mail,password,date[0]))
        connection.commit()
        connection.close()
        session["user_ad"] = name
        return redirect("/") 
    else:
        return render_template("register.htm")

@app.route("/login",methods=["GET","POST"]) 
def girisyap():
    if request.method == "POST":
        mail = request.form["inp_mail"]
        password = request.form["inp_password"]
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""
                        SELECT * FROM User
                        WHERE email = ? AND password = ?
                                """,(mail,password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            session["user_ad"] = user[1]
            session["user_wl"] = user[4]
            return redirect("/")
        else:
           return render_template("login.htm",error="Geçersiz e-posta veya şifre!")

    else:
        return render_template("login.htm")

@app.route("/logout")  
def logout():
    session.clear()  
    return redirect("/")

@app.route("/profile")
def profile():
    user_id=session["user_id"]
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(" SELECT name_sname,email,pp,date FROM User WHERE id = ? ",(user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        rdate = user[3].split(' ')[0]
        wlcounter = len(bringWL(user_id).split(',')) - 1
        user_data = {"name_sname": user[0], "email": user[1], "user_pp": user[2], "date": rdate}
        return render_template("profile.htm",Udata=user_data,wlc=wlcounter, logged=True)
    else:
        if "user_id" in session:
            return redirect("/", logged=True)
        else:
            return redirect("/")

@app.route("/account-settings", methods=["POST","GET"])
def accdetails():
    user_id = session["user_id"]
    connection = create_connection()
    cursor = connection.cursor()
    
    if request.method == "POST":
        name = request.form["inp_name"]
        email = request.form["inp_email"]
        password = request.form.get("inp_password")
        selected_pp = request.form.get("btnradio")
        
        try:
            if password:  
                cursor.execute("""
                    UPDATE User SET name_sname=?, email=?, password=?, pp=? WHERE id=?
                """, (name, email, password, selected_pp, user_id))
            else:  
                cursor.execute("""
                    UPDATE User SET name_sname=?, email=?, pp=? WHERE id=?
                """, (name, email, selected_pp, user_id))
            session["user_ad"]=name
            connection.commit()
            success = "Bilgileriniz başarıyla güncellendi!"
            return render_template("acc-sttngs.htm",logged=True, userid=session["user_id"], success=success, user={"name_sname": name, "email": email, "user_pp": selected_pp})
        
        except sqlite3.Error as e:
            error = "Bilgiler güncellenirken bir hata oluştu!"
            return render_template("acc-sttngs.htm", error=error, user={"name_sname": name, "email": email, "user_pp": selected_pp},logged=True)
    
    else:
        cursor.execute("SELECT name_sname, email, pp FROM User WHERE id=?", (user_id,))
        user = cursor.fetchone()
        connection.close()
        
        if user:
            user_data = {"name_sname": user[0], "email": user[1], "user_pp": user[2]}
            return render_template("acc-sttngs.htm",logged=True, userid=session["user_id"], user=user_data)
        else:
            return redirect("/")

@app.route("/delete-account", methods=["POST"])
def delete_account():
    if "user_id" in session:
        user_id = session["user_id"]
        
        
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM User WHERE id = ?", (user_id,))
        connection.commit()
        connection.close()

        
        session.clear()
        
        return redirect("/")
    else:
        return redirect("/login")

@app.route("/mywatchlist")
def mywl():
    userid = session["user_id"]
    wl = bringWL(userid).split(",")
    wl=sorted(wl, reverse=True)
    movies=[]
    movieCounter=len(wl) - 1
    for i in range(0,movieCounter-1,1):
        movies.append(bringTheMovie(wl[i]))
    user = bringuser(session["user_id"])
    date = user[5].split(' ')
    if movieCounter!=0:
        p = math.ceil(movieCounter/16)
        return render_template("myWL.htm",logged=True,User=user,Movies=movies,MC=movieCounter,dt=date[0],P=p)
    else:
        nf="İzleme Listesi Boş"
        return render_template("myWL.htm",logged=True,User=user,NF=nf,MC=movieCounter,dt=date[0],P=0)

@app.route('/moviedetails/<int:id>')
def mdetails(id):
    movie = bringTheMovie(id)
    if movie:
        movie_details = movie
        veli(movie[0])
        if "user_id" in session:
            uid = session["user_id"]
            Wl=checkWL(uid,movie[0])
            return render_template("movieDetails.htm",Movie=movie_details,logged=True,wl=Wl)
        else:
            return render_template("movieDetails.htm",Movie=movie_details)
    else:
            return redirect("/page-not-found")    

@app.route("/addToWL/<int:id>", methods=["POST"])
def addToWL(id):
    userid=session["user_id"]
    Mid = str(id) +  ','
    wl=bringWL(userid)
    wlist=wl+Mid
    try:
        conn=create_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE User SET WList = ? WHERE id = ?",(wlist,userid,))
        conn.commit()
        conn.close()
        adres = "/moviedetails/" + str(id)
        return redirect(adres)
    except sqlite3.Error as e:
        error = "Listeye eklenirken bir hata oluştu!"
        return render_template("movieDetails.htm", error=error, logged=True)


@app.route("/removeFromWL/<int:id>", methods=["POST"])
def removefromwl(id):
    Mid=str(id) + ','
    userid=session["user_id"]
    wlist=bringWL(userid)
    Wlist = wlist.replace(Mid,'')
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE User SET WList = ? WHERE id = ?",(Wlist,userid,))
    conn.commit()
    conn.close()
    adres = "/moviedetails/" + str(id) 
    return redirect(adres)


@app.route('/movielist/<string:listType>/<int:no>')
def mlist(listType, no):
    dict = {
        'IMDb-rated'  : "SELECT * FROM Movies ORDER BY imdbP DESC",
        'most-viewed' : "SELECT * FROM Movies ORDER BY viewCounter DESC",
        'recent'      : "SELECT * FROM Movies ORDER BY id DESC"
    }
    dict2 = {
        'IMDb-rated'  : "VFilm | IMDb Sıralaması",
        'most-viewed' : "VFilm | En Çok Görüntülenenler",
        'recent'      : "VFilm | Son Eklenenler"
    } 
    Title = dict2[listType]
    lT=dict[listType]
    bag = (16*(no-1),(16*no))
    header = Title.split('|')

    conn=create_connection()
    cursor=conn.cursor()
    cursor.execute(lT)
    movies = cursor.fetchall()
    conn.close()
    p = math.ceil(len(movies)/16)

    if movies:
        if "user_id" in session:
            return render_template("movieList.htm",Movies = movies[bag[0]:bag[1]],title=Title,baslik=header[1],lType=listType,P=p,logged=True)
        else:
            return render_template("movieList.htm",Movies = movies[bag[0]:bag[1]],title=Title,baslik=header[1],lType=listType,P=p)
    else:
        if "user_id" in session:
            return render_template("notFound.htm",title=Title,logged=True)
        else:
            return render_template("notFound.htm",title=Title)

@app.route("/movielistGenre/<string:genre>/<int:no>")
def listgenre(genre,no):
    dict = {
        'action' : "VFilm | Aksiyon Filmleri",
        'anim' : "VFilm | Animasyon Filmleri",
        'scifi' : "VFilm | Bilim Kurgu Filmleri",
        'bio' : "VFilm | Biyografi Filmleri",
        'drama' : "VFilm | Drama Filmleri",
        'fantesy' : "VFilm | Fantezi Filmleri",
        'comedy' : "VFilm | Komedi Filmleri",
        'horror-thriller' : "VFilm | Korku/Gerilim Filmleri",
        'romance' : "VFilm | Romantik Filmler",
        'war' : "VFilm | Savaş Filmleri",
        'crime' : "VFilm | Suç Filmleri"
    }

    dict2 = {
        'action' : "Aksiyon",
        'anim' : "Animasyon",
        'scifi' : "Bilim Kurgu",
        'bio' : "Biyografi",
        'drama' : "Dram",
        'fantesy' : "Fantezi",
        'comedy' : "Komedi",
        'romance' : "Romantik",
        'war' : "Savaş",
        'crime' : "Suç"
    }
    Title = dict[genre]
    header = Title.split("|")[1]
    if genre=="horror-thriller":
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("""SELECT * FROM Movies 
                       WHERE genre LIKE '%Korku%'
                       OR genre LIKE '%Gerilim%'; """)
        movies = cursor.fetchall()
        connection.close()
    else:
        tur = "%"+dict2[genre]+"%"
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM Movies WHERE genre LIKE ? """,[tur])
        movies = cursor.fetchall()
        conn.close()
        
    bag = (16*(no-1),(16*no))
    p = len(movies)/16
    if p%1!=0:
        p = math.ceil(p)
    if movies:
        if "user_id" in session:
            return render_template("movieListGenre.htm",Movies=movies[bag[0]:bag[1]],Header=header,title=Title,lType=genre,P=p,logged=True)
        else:
            return render_template("movieListGenre.htm",Movies=movies[bag[0]:bag[1]],Header=header,title=Title,lType=genre,P=p)
    else:
        if "user_id" in session:
            return render_template("notFound.htm",logged=True)
        else:
            return render_template("notFound.htm",title=Title,P=p)

@app.route("/page-not-found")
def nf():
    if "user_id" in session:
        return render_template("notFound.htm",logged=True)
    else:
        return render_template("notFound.htm")

@app.route("/search/<int:no>")
def searchmovie(no):
    data = request.args.get('inp_search','')
    aranan = '%' + data + '%'
    Title=" VFilm | Ara "
    header = f'"{data}" için arama sonuçları'
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM Movies
                    WHERE m_name LIKE ? OR year LIKE ? OR director LIKE ? OR country LIKE ? OR genre LIKE ? OR description LIKE ?
                                        """,(aranan,)*6)
    movies = cursor.fetchall()
    conn.close()
    p = len(movies)/16
    r = math.floor(p)
    if p - r != 0 :
        p = math.ceil(p)
    else:
        p = int(p)
    bag = (16*(no-1),(16*no))
    if movies:
        if "user_id" in session:
            return render_template("movieListSearch.htm",Movies=movies[bag[0]:bag[1]],baslik=header,title=Title,P=p,logged=True)
        else:
            return render_template("movieListSearch.htm",Movies=movies[bag[0]:bag[1]],baslik=header,title=Title,P=p)
    else:
        if "user_id" in session:
            return render_template("notFound.htm",logged=True)
        else:
            return render_template("notFound.htm")


if __name__ == "__main__":
    app.run(host="0.0.0.0",port="6001",debug=False)
