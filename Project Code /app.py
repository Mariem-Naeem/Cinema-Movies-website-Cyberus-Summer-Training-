
from flask import Flask , redirect, url_for, render_template,request,flash,session,render_template_string
import db
import utils
import validators
connection =db.connect_to_database()
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address



app = Flask(__name__ )
app.secret_key= "rtfyguijomk,l#89651268"
Limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["50 per minute"])
@app.route("/")
def index():
    if 'username' in session:
        if session['username'] == 'admin':
             return render_template("index.html",gadgets=db.get_all_gadget(connection),username=session['username'])
        else:
             return render_template("index.html",gadgets=db.get_all_gadget(connection),username=session['username'])
    return "you aren not logged in"

@app.route("/login", methods = ["GET","POST"])
@Limiter.limit("5 per minute")
def login():
    if request.method =="POST":
       username =request.form["username"]
       password =request.form["password"]
       user =db.get_user(connection,username)
       if user:
           if utils.is_pass_match(password,user[2]):
                session['username']=user[1]
                session['user_id']=user[0]
                return redirect(url_for("index"))
           else:
                flash("Wrong cardinals","danger")
                return render_template("login.html")
       else:
            flash("Invalid username and password","danger")       
            return render_template("login.html")
       
    return render_template("login.html")

@app.route("/register", methods = ["GET","POST"])
def register():
   if request.method =="POST":
       username =request.form["username"]
       password =request.form["password"]
       if not utils.is_strong_password(password):
            flash("Sorry You Entered a weak Password Please Choose a stronger one", "danger")
            return render_template('register.html')
       is_found =db.get_user(connection,username)
       if is_found:
           flash("User is already created","danger")
           return render_template("register.html")
       db.add_user(connection,username,password)
       flash("User Created Successfully","success")
       return redirect(url_for("login"))
   else:
       return render_template("register.html")
   


@app.route("/upload", methods =["GET","POST"])
def upload():
    if 'username' in session:
        if not session['username'] == 'admin':
             flash(" you are not admin","danger")
             return redirect(url_for("index"))
        
    
    if request.method == "POST":
            gadgetimage=request.files['image']
            if not gadgetimage or gadgetimage.filename == ' ':
                flash("Image is required","danger")
                return render_template("upload-gadget.html")
            if not validators.allowed_file(gadgetimage.filename) or not validators.allowed_file_size(gadgetimage):
                flash("Invalid File is Uploaded", "danger")
                return render_template("upload-gadget.html")

            title = request.form['movie name']
            description = request.form['description']
            price= request.form['price']
            gadgetimage = request.files['image']
            image_url =f"uploads/{gadgetimage.filename}"
            gadgetimage.save("static/"+image_url)
            user_id = session['user_id']
            db.add_gadget(connection,user_id,title,description,price,image_url)
            return redirect(url_for("index"))
    return render_template("upload-gadget.html")

@app.route("/delete/<gadget_id>", methods =["POST","GET"])
def delete(gadget_id):
    if 'username' in session:
        if not session['username'] == 'admin':
             flash(" you are not admin","danger")
             return redirect(url_for("index"))
        else: 
             db.delete_gadget(connection,gadget_id)
             flash("You delete Successfully ","success")
             return redirect(url_for("index"))
        
        


@app.route('/gadget/<gadget_id>')
def getGadget(gadget_id):
    gadget =db.get_gadget(connection,gadget_id)
    comments = db.get_comment_for_gadget(connection,gadget[0])


    return  render_template("gadget.html", gadget=gadget, comments=comments)     
    
@app.route('/add-comment/<gadget_id>', methods=['POST'])
def addComment(gadget_id):
	text = request.form['Review']
	user_id = session['user_id']
	db.add_comment(connection, gadget_id, user_id, text)
	return redirect(url_for("getGadget", gadget_id=gadget_id))

@app.route('/buy-gadget/<gadget_id>',methods=['POST'])
def buy_item(gadget_id):
    gadget = db.get_gadget(connection, gadget_id)
    is_sold = db.is_gadget_sold(connection,gadget_id)
    if is_sold == 0:
       if gadget:
            db.mark_gadget_as_sold(connection, gadget[0])
            flash(f"Congratulations You have bought the item !","success")
            return redirect(url_for("getGadget", gadget_id=gadget_id))
       else:
            return redirect(url_for("getGadget", gadget_id=gadget_id))
    else:
        flash("Sorry the item is already sold", "danger")
        return redirect(url_for('getGadget', gadget_id=gadget_id))


@app.route('/search', methods=['GET'])
def search_route():
    query = request.args.get('query')
    results = db.search(connection,query)  
    return render_template('search.html', query=query, results=results,gadgets=db.get_all_gadget(connection))


@app.route('/profile')
def profile():
	if 'username' in session:
		return render_template("profile.html", user=db.get_user(connection, session['username']))

	flash("You are Not Logged In", "danger")
	return redirect(url_for("login"))

@app.route('/withdraw')
def withdraw():
	if 'username' in session:
		return render_template("withdraw.html", user=db.get_user(connection, session['username']))

	flash("You are Not Logged In", "danger")
	return redirect(url_for("login"))



@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


if __name__ =="__main__":
    db.init_db(connection)
    db.seed_admin_user(connection)
    db.init_gadget_table(connection)
    db.init_comments_table(connection)
    app.run(debug=True)
    
      
