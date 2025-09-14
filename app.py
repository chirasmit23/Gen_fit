from flask import Flask,render_template,request,flash,redirect,url_for,session,jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta
from flask_socketio import SocketIO, emit,join_room, leave_room
from flask_socketio import SocketIO
import os
from flask_migrate import Migrate
from flask_cors import CORS
from google import genai
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

app=Flask(__name__,template_folder="templates")

CORS(app)
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///fitness.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
socketio = SocketIO(app, cors_allowed_origins="*")
db=SQLAlchemy(app)
migrate = Migrate(app, db)
import workouts
clients={}
IST = timezone(timedelta(hours=5, minutes=30))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    telephone = db.Column(db.String(20), nullable=True)
    DOB = db.Column(db.Date, nullable=True)
    height = db.Column(db.Integer, nullable=True)
    subscriptions = db.relationship("Subscription", back_populates="user", lazy=True)
    messages = db.relationship("chatmessage", back_populates="user", lazy=True)
class Gym(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    location = db.Column(db.String(200), nullable=True)
    trainers = db.relationship("Trainer", back_populates="gym", lazy=True)
class Trainer(db.Model):
 
    id = db.Column(db.Integer, primary_key=True)
    trainername = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    telephone = db.Column(db.String(20), nullable=False)
    DOB = db.Column(db.Date, nullable=False)
    gym_id = db.Column(db.Integer, db.ForeignKey("gym.id"), nullable=True)
    gym = db.relationship("Gym", back_populates="trainers")
    subscriptions = db.relationship("Subscription", back_populates="trainer", lazy=True)
    messages = db.relationship("chatmessage", back_populates="trainer", lazy=True)
class chatmessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(IST).replace(microsecond=0))
    sender_role = db.Column(db.String(20), nullable=False)  # 'user' or 'trainer' or 'system'
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey("trainer.id"), nullable=True)
    user = db.relationship("User", back_populates="messages")
    trainer = db.relationship("Trainer", back_populates="messages")    
class Subscription(db.Model):
   
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    trainer_id = db.Column(db.Integer, db.ForeignKey("trainer.id"), nullable=False)
    user = db.relationship("User", back_populates="subscriptions")
    trainer = db.relationship("Trainer", back_populates="subscriptions")
    __table_args__ = (db.UniqueConstraint("user_id", "trainer_id", name="uq_user_trainer"),)

def make_room(user_id, trainer_id):
    a, b = sorted([f"user:{user_id}", f"trainer:{trainer_id}"])
    return f"room_{a}_{b}"
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
@app.route("/trainersignup", methods=["GET", "POST"])
def trainersignup():
    if request.method == 'POST':
        trainername = request.form.get("name")
        EmailAddress = request.form.get("emailInput")
        telephone = request.form.get("telephone")
        dob_str = request.form.get("DOB")
        password = generate_password_hash(request.form.get("Password"))
        if Trainer.query.filter_by(email=EmailAddress).first():
            flash("A trainer with this email already exists", "warning")
            return redirect(url_for("trainersignup"))
        dob = None
        if dob_str:
            dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        trainer = Trainer(trainername=trainername, email=EmailAddress, telephone=telephone, password=password,
                          DOB=dob or datetime.now().date())
        db.session.add(trainer)
        db.session.commit()
        session["role"] = "trainer"
        session["trainer_id"] = trainer.id
        session["trainername"] = trainer.trainername
        flash("Trainer account created successfully", "success")
        return redirect(url_for("trainerdashboard"))
    return render_template("TrainerPages/trainersignup.html")
@app.route("/trainerlogin", methods=["GET", "POST"])
def trainerlogin():
    if request.method == "POST":
        EmailAddress = request.form.get("email")
        password = request.form.get("password")
        trainer = Trainer.query.filter_by(email=EmailAddress).first()
        if trainer and check_password_hash(trainer.password, password):
            session["role"] = "trainer"
            session["trainer_id"] = trainer.id
            session["trainername"] = trainer.trainername
            flash("Login successful", "success")
            return redirect(url_for("trainerdashboard"))
        flash("Invalid credentials", "danger")
    return render_template("TrainerPages/trainerlogin.html")
@app.route("/trainerdashboard")
def trainerdashboard():
    # if session.get("role") != "trainer" or not session.get("trainer_id"):
    #     flash("Trainer allready exist try again")
    #     return redirect(url_for("trainerlogin"))
    trainer_id = session["trainer_id"]
    users = (User.query.join(Subscription, Subscription.user_id == User.id)
             .filter(Subscription.trainer_id == trainer_id)
             .order_by(User.fullname.asc()).all())
    return render_template("TrainerPages/trainerdashboard.html", users=users)
@app.route("/usersignup", methods=["GET", "POST"])
def usersignup():
    if request.method == "POST":
        fullname = request.form.get("fullname")
        EmailAddress = request.form.get("email")
        telephone = request.form.get("phone")
        dob_str = request.form.get("dob")
        height = request.form.get("height")
        password = generate_password_hash(request.form.get("confirmPassword"))
        if User.query.filter_by(email=EmailAddress).first():
            flash("A user with this email already exists", "warning")
            return redirect(url_for("usersignup"))
        dob = None
        if dob_str:
            dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        user = User(fullname=fullname, email=EmailAddress, telephone=telephone, height=height, password=password, DOB=dob)
        db.session.add(user)
        db.session.commit()
        session["role"] = "user"
        session["user_id"] = user.id
        session["username"] = user.fullname
        flash("User account created", "success")
        return redirect(url_for("userdashboard"))
    return render_template("UserPages/usersignup.html")
@app.route("/userlogin", methods=["GET", "POST"])
def userlogin():
    if request.method == "POST":
        EmailAddress = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=EmailAddress).first()
        if user and check_password_hash(user.password, password):
            session["role"] = "user"
            session["user_id"] = user.id
            session["username"] = user.fullname
            flash("Login successful", "success")
            return redirect(url_for("userdashboard"))
        flash("Invalid credentials", "danger")
    return render_template("UserPages/Userlogin.html")
@app.route("/userdashboard")
def userdashboard():
    if session.get("role") != "user" or not session.get("user_id"):
        return redirect(url_for("userlogin"))
    return render_template("UserPages/userdashboard.html", username=session.get("username"))
@app.route("/trainerlist")
def trainerlist():
    trainers = Trainer.query.order_by(Trainer.trainername.asc()).all()
    user_id = session.get("user_id")
    subscribed_to = {  }
    if user_id:
        subs = Subscription.query.with_entities(Subscription.trainer_id).filter_by(user_id=user_id).all()
        subscribed_ids = {tid for (tid,) in subs}
        subscribed_to = {t.id: (t.id in subscribed_ids) for t in trainers}
    return render_template("TrainerPages/trainerlists.html", trainers=trainers, subscribed_to=subscribed_to)
@app.route("/subscribe/<int:trainer_id>", methods=["POST"])
def subscribe(trainer_id):
    if session.get("role") != "user" or not session.get("user_id"):
        flash("Please log in as a user to subscribe.", "warning")
        return redirect(url_for("userlogin"))
    user_id = session["user_id"]
    trainer = Trainer.query.get_or_404(trainer_id)
    existing = Subscription.query.filter_by(user_id=user_id, trainer_id=trainer.id).first()
    if existing:
        flash("You are already subscribed to this trainer.", "info")
    else:
        sub = Subscription(user_id=user_id, trainer_id=trainer.id)
        db.session.add(sub)
        db.session.commit()
        flash(f"Subscribed to {trainer.trainername}.", "success")
    return redirect(url_for("trainerlist"))
@app.route("/unsubscribe/<int:trainer_id>", methods=["POST"])
def unsubscribe(trainer_id):
    if session.get("role") != "user" or not session.get("user_id"):
        flash("Please log in as a user.", "warning")
        return redirect(url_for("userlogin"))
    user_id = session["user_id"]
    sub = Subscription.query.filter_by(user_id=user_id, trainer_id=trainer_id).first()
    if sub:
        db.session.delete(sub)
        db.session.commit()
        flash("Unsubscribed.", "info")
    else:
        flash("You were not subscribed.", "warning")
    return redirect(url_for("trainerlist"))
@app.route("/userchat/<int:trainer_id>")
def userchat(trainer_id):
    if session.get("role") != "user" or not session.get("user_id"):
        flash("Please log in as a user to chat.", "warning")
        return redirect(url_for("userlogin"))
    user_id = session["user_id"]
    if not Subscription.query.filter_by(user_id=user_id, trainer_id=trainer_id).first():
        flash("Subscribe to this trainer to start chatting.", "warning")
        return redirect(url_for("trainerlist"))
    trainer = Trainer.query.get_or_404(trainer_id)
    msgs = (chatmessage.query.filter_by(user_id=user_id, trainer_id=trainer_id).order_by(chatmessage.timestamp.asc()).all())
    room = make_room(user_id, trainer_id)
    return render_template("UserPages/userchat.html",
                           trainer=trainer,
                           messages=msgs,
                           room=room,

                           user_id=user_id,
                           trainer_id=trainer_id,
                           username=session.get("username"))
@app.route("/trainerchat/<int:user_id>", methods=["GET"])
def trainerchat(user_id):
    # if session.get("role") != "trainer" or not session.get("trainer_id"):
    #     return redirect(url_for("trainerlogin"))
    trainer_id = session["trainer_id"]
    if not Subscription.query.filter_by(user_id=user_id, trainer_id=trainer_id).first():
        flash("This user is not your subscriber.", "warning")
        return redirect(url_for("trainerdashboard"))
    user = User.query.get_or_404(user_id)
    msgs = (chatmessage.query.filter_by(user_id=user_id, trainer_id=trainer_id).order_by(chatmessage.timestamp.asc()).all())
    room = make_room(user_id, trainer_id)
    return render_template("TrainerPages/trainerchat.html",
                           user=user,
                           messages=msgs,
                           room=room,
                           user_id=user_id,
                           trainer_id=trainer_id,
                           username=session.get("trainername"))
@app.post("/userchat/<int:trainer_id>/send")
def user_send_message(trainer_id):
    # if session.get("role") != "user" or not session.get("user_id"):
    #     return redirect(url_for("userlogin"))
    user_id = session["user_id"]
    if not Subscription.query.filter_by(user_id=user_id, trainer_id=trainer_id).first():
        flash("You must subscribe first.", "warning")
        return redirect(url_for("trainerlist"))
    
    content = request.form.get("message", "").strip()
    if content:
        db.session.add(chatmessage(content=content, sender_role="user", user_id=user_id, trainer_id=trainer_id))
        db.session.commit()
    return redirect(url_for("userchat", trainer_id=trainer_id))
@app.post("/trainerchat/<int:user_id>/send")
def trainer_send_message(user_id):
    # if session.get("role") != "trainer" or not session.get("trainer_id"):
    #     return redirect(url_for("trainerlogin"))
    trainer_id = session["trainer_id"]

    if not Subscription.query.filter_by(user_id=user_id, trainer_id=trainer_id).first():
        flash("You can only chat with your subscribers.", "warning")
        return redirect(url_for("trainerdashboard"))
    content = request.form.get("message", "").strip()
    if content:
        db.session.add(chatmessage(content=content, sender_role="trainer", user_id=user_id, trainer_id=trainer_id))
        db.session.commit()
    return redirect(url_for("trainerchat", user_id=user_id))
@app.route("/userlist")
def userlist():
    # if session.get("role") != "trainer":
    #     return redirect(url_for("trainerlogin"))
    trainer_id = session["trainer_id"]

    subscribed_users = (db.session.query(User).join(Subscription, Subscription.user_id == User.id)
                        .filter(Subscription.trainer_id == trainer_id).all())
    return render_template("TrainerPages/userlist.html", users=subscribed_users)
clients = {  }  
@socketio.on("leave")
def on_leave(data):
    room = data.get("room")
    leave_room(room)
    clients.pop(request.sid, None)
import logging
logging.basicConfig(level=logging.DEBUG)

@socketio.on("join")
def on_join(data):
    room = data.get("room")
    username = data.get("username")

    sender_role = data.get("sender_role")
    user_id = data.get("user_id")
    trainer_id = data.get("trainer_id")
    logging.debug(f"[Join] SID={request.sid} username={username} room={room} role={sender_role} user_id={user_id} trainer_id={trainer_id}")
    if not room or not username:
        logging.warning("[JOIN] missing room or username, ignoring join")
        return
    join_room(room)
    clients[request.sid] = {"username": username  ,"room": room, "role": sender_role}
    system_msg = chatmessage(content=f"{username} joined the chat.", sender_role="system", user_id=user_id, trainer_id=trainer_id)


    db.session.add(system_msg)
    db.session.commit()
    load = {
        "id": system_msg.id,
        "content": system_msg.content,
        "sender_role": "system",
        "sender_name": "System",
        "timestamp": system_msg.timestamp.isoformat()
    }
    logging.debug(f"[JOIN] emitting system join to room={room} payload={load}")
    emit("receive_message", load, room=room)
@socketio.on("send_message")
def handle_send_message(data):
    room = data.get("room")

    content = data.get("content") or data.get("message")
    sender_role = data.get("sender_role")

    sender_name = data.get("sender_name") or data.get("username")
    user_id = data.get("user_id")
    trainer_id = data.get("trainer_id")

    logging.debug(f"[Send] SID={request.sid} room={room} sender_role={sender_role} sender_name={sender_name} content={content}")
    if not room or not content or not sender_role:
        logging.warning("[Send] missing required fields;ignoring")
        return
    msg = chatmessage(content=content, sender_role=sender_role, user_id=user_id, trainer_id=trainer_id)
    db.session.add(msg)
    db.session.commit()
    load = {
        "id": msg.id,

        "content": msg.content,
        "sender_role": msg.sender_role,
        "sender_name": sender_name or msg.sender_role,
        "timestamp": msg.timestamp.isoformat()
    }
    logging.debug(f"[Send] broadcasting msg id={msg.id} to room={room} payload={load}")
    emit("receive_message", load, room=room)
from werkzeug.utils import secure_filename
from PIL import Image    
@app.route("/chatbot", methods=["POST", "GET"])
def chatbot():
    if request.method == "POST":
        UPLOAD_FOLDER = "uploads"
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        textInput = request.form.get("msg", "").strip()
        imageInput = request.files.get("image")

        # load .env and API key
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("My_gemini_api_key")
        if not api_key:
            app.logger.error("API key missing")
            return jsonify({"reply": "Error: API key not found on server."}), 500

        # Create client explicitly with API key (recommended)
        try:
            client = genai.Client(api_key=api_key)
        except Exception as e:
            app.logger.exception("Failed to create genai client")
            return jsonify({"reply": f"Error initializing AI client: {str(e)}"}), 500

        try:
            # If image was uploaded, save and open as PIL Image (docs example supports PIL Image)
            if imageInput:
                filename = secure_filename(imageInput.filename)
                image_path = os.path.join(UPLOAD_FOLDER, filename)
                imageInput.save(image_path)

                # Open with PIL (the SDK example shows passing a PIL image object directly)
                try:
                    pil_image = Image.open(image_path).convert("RGB")
                except Exception as e:
                    app.logger.exception("PIL failed to open image")
                    return jsonify({"reply": f"Error reading uploaded image: {str(e)}"}), 400

                # Compose prompt: prefer user text but provide fallback
                prompt = textInput or "Please describe the food in this image and estimate calories."

                # Call generate_content like the docs: contents = [prompt, pil_image]
                # (This pattern is shown in the official Python examples.)
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[prompt, pil_image]
                )
            else:
                prompt = textInput or "Hello!"
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )

            # Extract text safely from response (cover SDK variants)
            reply_text = None
            if hasattr(response, "text") and response.text:
                reply_text = response.text
            else:
                # Try candidates -> content -> parts -> text (docs show this structure)
                try:
                    if getattr(response, "candidates", None):
                        cand = response.candidates[0]
                        parts = getattr(cand.content, "parts", None) or getattr(cand.content, "parts", [])
                        if parts:
                            # parts may be list of objects or dicts
                            first_part = parts[0]
                            # support object or dict
                            reply_text = getattr(first_part, "text", None) or first_part.get("text") if isinstance(first_part, dict) else None
                except Exception:
                    app.logger.debug("response parsing fallback failed", exc_info=True)

            if not reply_text:
                # Log entire response server-side for debugging (do NOT expose sensitive info in prod)
                app.logger.info("Full AI response object: %s", repr(response))
                return jsonify({"reply": "No text returned by AI. Check server logs for response structure."}), 500

            return jsonify({"reply": reply_text})

        except Exception as e:
            # Log trace for debugging
            tb = traceback.format_exc()
            app.logger.error("Exception calling genai: %s\n%s", str(e), tb)
            # Return the error message so frontend sees it while debugging
            return jsonify({"reply": f"AI call error: {str(e)}"}), 500

    # GET -> render chat page
    return render_template("UserPages/AIchatbox.html")

workouts.register_workout_routes(app)
if __name__ == "__main__":
    
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)
