from flask import Flask, render_template, request, jsonify, redirect, url_for
import firebase_admin
import random
from firebase_admin import credentials, auth, firestore
from google.cloud.firestore_v1.base_query import FieldFilter 

app = Flask(__name__)

# --- 1. INITIALIZE FIREBASE ---
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# --- 2. KNOWLEDGE BASE (Exercises & Quotes) ---
exercises_data = [
    # BASKETBALL
    {"name": "Weighted Squats", "sport": "Basketball", "goal": "Strength", "reps": "4 sets of 12", "desc": "Build leg power for rebounding.", "image": "1534438327276-14e5300c3a48"},
    {"name": "Diamond Push-ups", "sport": "Basketball", "goal": "Strength", "reps": "3 sets of 15", "desc": "Develop tricep strength for shooting.", "image": "1571019614242-c5c5dee9f50b"},
    {"name": "Core Planks", "sport": "Basketball", "goal": "Strength", "reps": "3 sets of 1 min", "desc": "Improve core stability.", "image": "1519861531473-9200262188bf"},
    {"name": "Suicide Sprints", "sport": "Basketball", "goal": "Endurance", "reps": "5 rounds", "desc": "High-intensity court sprints.", "image": "1546519638-68e109498ffc"},
    {"name": "Plyometric Box Jumps", "sport": "Basketball", "goal": "Explosiveness", "reps": "4 sets of 10", "desc": "Increase vertical leap.", "image": "1517836357463-d25dfeac3438"},

    # VOLLEYBALL
    {"name": "Shoulder Press", "sport": "Volleyball", "goal": "Strength", "reps": "3 sets of 12", "desc": "Power for spikes.", "image": "1592656670411-2918803b4745"},
    {"name": "Glute Bridges", "sport": "Volleyball", "goal": "Strength", "reps": "3 sets of 20", "desc": "Lower body stability.", "image": "1518310383802-640c2de311b2"},
    {"name": "Lateral Shuffles", "sport": "Volleyball", "goal": "Endurance", "reps": "5 sets of 1 min", "desc": "Defense stamina.", "image": "1574680096145-d05b474e2158"},
    {"name": "Block Jumps", "sport": "Volleyball", "goal": "Explosiveness", "reps": "4 sets of 12", "desc": "Net defense jumping.", "image": "1585851941820-293c052441ca"},

    # BADMINTON
    {"name": "Wrist Flick Drills", "sport": "Badminton", "goal": "Strength", "reps": "4 sets of 25", "desc": "Wrist snap power.", "image": "1613918431208-6752fe4ef71d"},
    {"name": "Shadow Footwork", "sport": "Badminton", "goal": "Endurance", "reps": "4 sets of 3 mins", "desc": "Court movement stamina.", "image": "1626224580194-8fa0d3235986"},
    {"name": "Split Step Jumps", "sport": "Badminton", "goal": "Explosiveness", "reps": "4 sets of 15", "desc": "Reaction jumps.", "image": "1554068865-24cecd4e34b8"},

    # FOOTBALL
    {"name": "Bulgarian Split Squats", "sport": "Football", "goal": "Strength", "reps": "3 sets of 12", "desc": "Kicking leg power.", "image": "1517466787929-bc90951d0974"},
    {"name": "Beep Test Sprints", "sport": "Football", "goal": "Endurance", "reps": "6 rounds", "desc": "Match-day stamina.", "image": "1519861531473-9200262188bf"},
    {"name": "Sprints (30m)", "sport": "Football", "goal": "Explosiveness", "reps": "8 rounds", "desc": "Breakaway speed.", "image": "1510566337590-2fc1f21d0faa"},
    {"name": "Squat Jumps", "sport": "Football", "goal": "Explosiveness", "reps": "3 sets of 15", "desc": "Power for headers.", "image": "1529900748604-07564a03e7a6"}
]

motivational_quotes = [
    "Discipline is doing what needs to be done, even if you don't want to do it.",
    "Hard work beats talent when talent doesn't work hard.",
    "Your health is an investment, not an expense.",
    "Success starts with self-discipline.",
    "Don't stop when you're tired. STOP when you're DONE!",
    "Champions keep playing until they get it right."
]

# --- 3. AUTHENTICATION ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login_page')
def login_page():
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    try:
        user = auth.create_user(email=data.get('email'), password=data.get('password'))
        db.collection('users').document(user.uid).set({
            'name': data.get('name'),
            'email': data.get('email'),
            'role': 'varsity',
            'profile_completed': False,
            'created_at': firestore.SERVER_TIMESTAMP
        })
        return jsonify({"message": "Success", "uid": user.uid}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    try:
        # Hahanapin ang user sa Firestore gamit ang email
        users_ref = db.collection('users').where(filter=FieldFilter('email', '==', email)).limit(1).stream()
        user_data = None
        uid = None
        for doc in users_ref:
            user_data = doc.to_dict()
            uid = doc.id
            
        if user_data:
            return jsonify({"message": "Login Successful", "uid": uid}), 200
        else:
            return jsonify({"error": "User not found. Please register first."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# --- 4. PROFILE & STATS ---

@app.route('/profile/<uid>')
def profile(uid):
    return render_template('profile.html', uid=uid)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    data = request.json
    try:
        db.collection('users').document(data.get('uid')).update({
            'sport': data.get('sport'),
            'goal': data.get('goal'),
            'height': data.get('height'),
            'weight': data.get('weight'),
            'profile_completed': True
        })
        return jsonify({"message": "Success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/profile_view/<uid>')
def profile_view(uid):
    try:
        user_doc = db.collection('users').document(uid).get().to_dict()
        h = float(user_doc.get('height', 0)) / 100
        w = float(user_doc.get('weight', 0))
        bmi = round(w / (h * h), 1) if h > 0 else 0
        logs = db.collection('workout_logs').where(filter=FieldFilter('uid', '==', uid)).get()
        return render_template('profile_view.html', user=user_doc, uid=uid, bmi=bmi, total=len(logs))
    except Exception as e:
        return str(e), 500

# --- 5. AI DASHBOARD LOGIC ---

@app.route('/dashboard/<uid>')
def dashboard(uid):
    try:
        user_ref = db.collection('users').document(uid)
        user_doc = user_ref.get().to_dict()
        if not user_doc: return "User not found", 404

        # AI Health Analysis
        h = float(user_doc.get('height', 0)) / 100
        w = float(user_doc.get('weight', 0))
        bmi = round(w / (h * h), 1) if h > 0 else 0
        
        bmi_status, color_class = "Normal", "text-green-400"
        if bmi < 18.5: bmi_status, color_class = "Underweight", "text-yellow-400"
        elif bmi > 24.9: bmi_status, color_class = "Overweight", "text-red-400"

        # AI Coach Quote
        daily_quote = random.choice(motivational_quotes)

        # Progress Calculation
        logs_count = len(db.collection('workout_logs').where(filter=FieldFilter('uid', '==', uid)).get())

        return render_template('dashboard.html', 
                             user=user_doc, uid=uid, bmi=bmi, 
                             bmi_status=bmi_status, color_class=color_class, 
                             progress=logs_count, quote=daily_quote)
    except Exception as e:
        return str(e), 500

# --- 6. AI RECOMMENDATIONS & TRACKING ---

@app.route('/get_recommendation/<uid>')
def get_recommendation(uid):
    try:
        user_doc = db.collection('users').document(uid).get().to_dict()
        user_sport, user_goal = user_doc.get('sport'), user_doc.get('goal')
        
        all_matches = [ex for ex in exercises_data if ex['sport'] == user_sport and ex['goal'] == user_goal]
        if not all_matches:
            all_matches = [ex for ex in exercises_data if ex['sport'] == user_sport]

        # Random Selection of 4 Drills
        num_to_select = min(len(all_matches), 4)
        recommendations = random.sample(all_matches, num_to_select)
        return jsonify(recommendations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/log_workout', methods=['POST'])
def log_workout():
    data = request.json
    try:
        db.collection('workout_logs').add({
            'uid': data.get('uid'),
            'drill_name': data.get('drill_name'),
            'timestamp': firestore.SERVER_TIMESTAMP,
            'status': 'Completed'
        })
        return jsonify({"message": "Logged"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/history/<uid>')
def history(uid):
    try:
        user_doc = db.collection('users').document(uid).get().to_dict()
        logs_ref = db.collection('workout_logs').where(filter=FieldFilter('uid', '==', uid)).order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
        
        logs = []
        for doc in logs_ref:
            ld = doc.to_dict()
            if ld.get('timestamp'):
                ld['date_formatted'] = ld['timestamp'].strftime('%b %d, %Y - %I:%M %p')
            logs.append(ld)
        return render_template('history.html', logs=logs, user=user_doc, uid=uid)
    except Exception as e:
        return str(e), 500

# --- 7. RUN SERVER ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)