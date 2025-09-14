

from flask import Flask,render_template,request,flash,redirect,url_for,session,jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta
from flask_socketio import SocketIO, emit,join_room
from flask_socketio import SocketIO
import os
from flask_cors import CORS
from google import genai
from google.genai import types
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
app=Flask(__name__,template_folder="templates")
CORS(app)
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///fitness.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
socketio = SocketIO(app, cors_allowed_origins="*")
db=SQLAlchemy(app)
clients={}
IST = timezone(timedelta(hours=5, minutes=30))
class Trainer(db.Model):
    trainername=db.Column(db.String("100"),nullable=False, unique=True)
    email=db.Column(db.String(150), nullable=False)
    password=db.Column(db.String(150), nullable=False)
    telephone=db.Column(db.Integer, primary_key=True)
    DOB=db.Column(db.Date, primary_key=True)
#fitness = db.relationship('fitness', backref='user', lazy=True)
class User(db.Model):
    fullname=db.Column(db.String("100"),nullable=False, unique=True)
    email=db.Column(db.String(150), nullable=False)
    password=db.Column(db.String(150), nullable=False)
    telephone=db.Column(db.Integer, primary_key=True)
    DOB=db.Column(db.Date, primary_key=True)
    height=db.Column(db.Integer,primary_key=True)
class chatmessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(50))
    receiver = db.Column(db.String(100))
    message = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(IST).replace(microsecond=0))
@app.route("/")
def index():
    return render_template("genfit.html")    
@app.route("/selectrole", methods=["GET", "POST"])
def selectrole():
    if request.method == "POST":
        role = request.form.get("role")
        if role == "trainer":
            return redirect("/trainersignup")
        elif role == "user":
            return redirect("/usersignup")
    return render_template("selectrole.html")
@app.route("/trainersignup",methods=["GET","POST"])
def trainersignup():
    if request.method == 'POST':
        trainername=request.form.get("name")
        EmailAddress=request.form.get("emailInput")
        telephone=request.form.get("telephone")
        dob_str = request.form.get("DOB")
        experience=request.form.get("experience")
        specilization=request.form.get("Specializations")
        password=generate_password_hash(request.form.get("Password"))
        if Trainer.query.filter_by(trainername=trainername).first():
            flash("The trainer is already exists try another","warning")
            return redirect("/trainersignup")
        else:
            dob_str = datetime.strptime(dob_str, "%Y-%m-%d").date()
            trainer=Trainer(trainername=trainername,email=EmailAddress,telephone=telephone, password= password,DOB=dob_str)
            db.session.add(trainer)
            db.session.commit()
            flash("account created")
            session["trainername"] = trainer.trainername
            session['role'] = 'trainer'
            
            return redirect("/trainerdashboard")
    return render_template("TrainerPages/trainersignup.html") 
@app.route("/trainerlogin",methods=["GET","POST"])  
def login():
    if request.method=="POST":    
        EmailAddress=request.form.get("email")
        password=request.form.get("password")
        trainer = Trainer.query.filter_by(email= EmailAddress).first()
        if trainer and check_password_hash(trainer.password, password):
            flash("Login successful", "success")
            return redirect(url_for("trainerdashboard"))
    return render_template('TrainerPages/trainerlogin.html')    
@app.route("/trainerdashboard")
def trainerdashboard():
    return render_template("TrainerPages/trainerdashboard.html")
@app.route("/usersignup",methods=["GET","POST"])
def usersignup():
    if request.method=="POST":
        fullname=request.form.get("fullname")
        EmailAddress=request.form.get("email")
        telephone=request.form.get("phone")
        dob_str = request.form.get("dob")
        height=request.form.get("height")
        password=generate_password_hash(request.form.get("confirmPassword"))
        if User.query.filter_by(fullname=fullname).first():
            flash("The trainer is already exists try another","warning")
            return redirect("/usersignup")
        else:
            dob_str = datetime.strptime(dob_str, "%Y-%m-%d").date()
            gym_goar=User(fullname=fullname,email=EmailAddress,telephone=telephone,height=height, password= password,DOB=dob_str)
            db.session.add(gym_goar)
            db.session.commit()
            flash("account created")
            session["fullname"]=gym_goar.fullname
        
            return redirect("/userdashboard")
    return render_template("UserPages/usersignup.html")
@app.route("/userlogin",methods=["GET","POST"])
def userlogin():
    if request.method=="POST":    
        EmailAddress=request.form.get("email")
        password=request.form.get("confirmPassword")
        gym_goar = Trainer.query.filter_by(email= EmailAddress).first()
        if gym_goar and check_password_hash(gym_goar.password, password):
            flash("Login successful", "success")
            return redirect(url_for("userdashboard"))
    return render_template('UserPages/Userlogin.html') 
@app.route("/userdashboard")
def userdashboard():
    return render_template("UserPages/userdashboard.html")     
@app.route("/userchat")
def userchat():
    fullname = session.get("fullname")
    return render_template("UserPages/userchat.html",username=fullname)

@app.route("/trainerchat")
def trainerchat():
    trainername = session.get("trainername")
    return render_template("TrainerPages/trainerchat.html",username=trainername)
@app.route("/trainerlist")
def trainerlist():
    return render_template("TrainerPages/trainerlists.html")


@socketio.on("join")
def on_join(data):
    username = data["username"]
    room = data["room"]
    join_room(room)
    clients[request.sid] = {"username": username, "room": room}
    past_messages = chatmessage.query.filter_by(receiver=username).all()
    for msg in past_messages:
        emit("receive_message", {"sender": msg.sender, "message": msg.message}, to=request.sid)

    emit("receive_message", {
        "sender": "System",
        "message": f"{username} has entered the room."
    }, room=room)
@socketio.on("send_message")
def handle_send_message(data):
    message = data["message"]
    receiver = data.get("receiver")
    user_info = clients.get(request.sid)
    if user_info:
        room = user_info["room"]
        sender = user_info["username"]
        emit("receive_message", {
            "sender": sender,
            "message": message
        }, room=room)
        new_msg = chatmessage(sender=sender, receiver=receiver, message=message)
        db.session.add(new_msg)
        db.session.commit()
from google.genai import types
@app.route("/chatbot", methods=["POST", "GET"]) 

def chatbot():
    if request.method == "POST":
        UPLOAD_FOLDER = "uploads"
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        textInput = request.form.get("msg")
        imageInput = request.files.get("image")

        load_dotenv()
        api_key = os.getenv("My_gemini_api_key")

        if not api_key:
            return jsonify({"error": "API key not found"})

        client = genai.Client(api_key=api_key)
        grounding_tool = types.Tool(
        google_search=types.GoogleSearch()
    )
        config = types.GenerateContentConfig(
        tools=[grounding_tool]
    )


        if imageInput:
            image_path = os.path.join(UPLOAD_FOLDER, imageInput.filename)
            imageInput.save(image_path)
            my_file = client.files.upload(file=image_path)

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[my_file, f"{textInput}"]
            )
        else:
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[f"{textInput}"],
                config=config
                
            )
        
        if response.text:
            return jsonify({"reply": response.text})
        else:
            return jsonify({"reply": "No response from AI."})
    return render_template("UserPages/AIchatbox.html")
@app.route("/dietplan")
def dietplan():
    return render_template("UserPages/dietplan.html")
@app.route("/supplement")
def supplement_plan():
    return render_template("UserPages/supplements.html")
@app.route("/exercise")
def exercise():
    return render_template("UserPages/exercise.html")
@app.route("/streching")
def streching():
    return render_template("UserPages/stretching.html")
@app.route("/My_Plan")
def My_Plan():
    return render_template("UserPages/My_Plan.html")
@app.route("/skullcrushers")
def skullcrushers():
    return render_template("tricepsworkoutdetails/skullcrushers.html")
@app.route("/dumbbelloverheadextension")
def dumbbelloverheadextension():
    return render_template("tricepsworkoutdetails/dumbbelloverheadextension.html")
@app.route("/ezbarcablepushdown")
def ezbarcablepushdown():
    return render_template("tricepsworkoutdetails/ezbarcablepushdown.html")
@app.route("/ropepushdown")
def ropepushdown():
    return render_template("tricepsworkoutdetails/ropepushdown.html")
@app.route("/seatedoverheaddumbbeltextension")
def seatedoverheaddumbbeltextension():
    return render_template("tricepsworkoutdetails/seatedoverheaddumbbeltextension.html")
@app.route("/lyingtricepextension")
def lyingtricepextension():
    return render_template("tricepsworkoutdetails/lyingtricepextension.html")
@app.route("/crossbodycableextension")
def crossbodycableextension():
    return render_template("tricepsworkoutdetails/crossbodycableextension.html")
@app.route("/dips")
def dips():
    return render_template("tricepsworkoutdetails/dips.html")
@app.route("/diamondpushup")
def diamondpushup():

    return render_template("tricepsworkoutdetails/diamondpushup.html")
@app.route("/benchdips")
def benchdips():
    return render_template("tricepsworkoutdetails/benchdips.html")
@app.route("/close_grip_brench_press")
def close_grip_brench_press():
    return render_template("tricepsworkoutdetails/closegripbenchpress.html")
@app.route("/closegrippushup")
def closegrippushup():
    return render_template("tricepsworkoutdetails/closegrippushup.html")
@app.route("/ropeburnouts")
def ropeburnouts():
    return render_template("tricepsworkoutdetails/ropeburnouts.html")
@app.route("/pushupburnout")
def pushupburnout():
    return render_template("tricepsworkoutdetails/pushupburnout.html")
@app.route("/dropsetcablepushdowns")
def dropsetcablepushdowns():
    return render_template("tricepsworkoutdetails/dropsetcablepushdowns.html")

@app.route("/halfrepsskullcrusher")
def halfrepsskullcrusher():
    return render_template("tricepsworkoutdetails/halfrepsskullcrusher.html")
@app.route("/shoulderworkout")
def shoulderworkout():
    return render_template("UserPages/shoulderworkout.html")
@app.route("/legsworkout")
def legsworkout():
    return render_template("UserPages/legsworkout.html")

@app.route("/workout/chest")
def chest_workout():
    return render_template("UserPages/chestworkout.html")

@app.route("/workout/back")
def back_workout():
    return render_template("UserPages/backworkout.html")

@app.route("/workout/biceps")
def biceps_workout():
    return render_template("UserPages/bicepsworkout.html")

@app.route("/workout/triceps")
def triceps_workout():
    return render_template("UserPages/tricepsworkout.html")

@app.route("/workout/shoulder")
def shoulder_workout():
    return render_template("UserPages/shoulderworkout.html")

@app.route("/workout/legs")
def legs_workout():
    return render_template("UserPages/legsworkout.html")
@app.route("/overheadbarbellpress")
def overheadbarbellpress():
    return render_template("shoulderworkoutdetails/overheadbarbellpress.html")

@app.route("/seateddumbbellpress")
def seateddumbbellpress():
    return render_template("shoulderworkoutdetails/seateddumbbellpress.html")

@app.route("/pushpress")
def pushpress():
    return render_template("shoulderworkoutdetails/pushpress.html")

@app.route("/machineshoulderpress")
def machineshoulderpress():
    return render_template("shoulderworkoutdetails/machineshoulderpress.html")
@app.route("/dumbbelllateralraise")
def dumbbelllateralraise():
    return render_template("shoulderworkoutdetails/dumbbelllateralraise.html")

@app.route("/cablelateralraise")
def cablelateralraise():
    return render_template("shoulderworkoutdetails/cablelateralraise.html")

@app.route("/leaninglateralraise")
def leaninglateralraise():
    return render_template("shoulderworkoutdetails/leaninglateralraise.html")

@app.route("/machinelateralraise")
def machinelateralraise():
    return render_template("shoulderworkoutdetails/machinelateralraise.html")
@app.route("/reversepecdeck")
def reversepecdeck():
    return render_template("shoulderworkoutdetails/reversepecdeck.html")

@app.route("/reardeltfly")
def reardeltfly():
    return render_template("shoulderworkoutdetails/reardeltfly.html")

@app.route("/facepulls")
def facepulls():
    return render_template("shoulderworkoutdetails/facepulls.html")

@app.route("/inclinereversefly")
def inclinereversefly():
    return render_template("shoulderworkoutdetails/inclinereversefly.html")
@app.route("/burnoutlaterals")
def burnoutlaterals():
    return render_template("shoulderworkoutdetails/burnoutlaterals.html")

@app.route("/shoulderpressburnout")
def shoulderpressburnout():
    return render_template("shoulderworkoutdetails/shoulderpressburnout.html")

@app.route("/uprightrowburnout")
def uprightrowburnout():
    return render_template("shoulderworkoutdetails/uprightrowburnout.html")

@app.route("/halfrepslateralraise")
def halfrepslateralraise():
    return render_template("shoulderworkoutdetails/halfrepslateralraise.html")
@app.route("/barbellbacksquat")
def barbellbacksquat():
    return render_template("legworkoutdetails/barbelbacksquat.html")

@app.route("/frontsquat")
def frontsquat():
    return render_template("legworkoutdetails/frontsquat.html")

@app.route("/romaniandeadlift")
def romaniandeadlift():
    return render_template("legworkoutdetails/romaniandeadlift.html")

@app.route("/bulgariansplitsquat")
def bulgariansplitsquat():
    return render_template("legworkoutdetails/bulgariansplitsquat.html")


@app.route("/legextension")
def legextension():
    return render_template("legworkoutdetails/legextension.html")

@app.route("/hacksquat")
def hacksquat():
    return render_template("legworkoutdetails/hacksquat.html")

@app.route("/heelevatedgobletsquat")
def heelevatedgobletsquat():
    return render_template("legworkoutdetails/heelevatedgobletsquat.html")

@app.route("/stepups")
def stepups():
    return render_template("legworkoutdetails/stepups.html")

@app.route("/seatedlegcurl")
def seatedlegcurl():
    return render_template("legworkoutdetails/seatedlegcurl.html")

@app.route("/hipthrust")
def hipthrust():
    return render_template("legworkoutdetails/hipthrust.html")

@app.route("/cablepullthrough")
def cablepullthrough():
    return render_template("legworkoutdetails/cablepullthrough.html")

@app.route("/glutekickback")
def glutekickback():
    return render_template("legworkoutdetails/glutekickback.html")


@app.route("/standingcalfraise")
def standingcalfraise():
    return render_template("legworkoutdetails/standingcalfraise.html")

@app.route("/seatedcalfraise")
def seatedcalfraise():
    return render_template("legworkoutdetails/seatedcalfraise.html")

@app.route("/jumpsquats")
def jumpsquats():
    return render_template("legworkoutdetails/jumpsquats.html")

@app.route("/walkinglunges")
def walkinglunges():
    return render_template("legworkoutdetails/walkinglunges.html")
if __name__ == "__main__":
    with app.app_context():
        db.create_all() 
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
