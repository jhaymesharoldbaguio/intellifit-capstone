from flask import Flask, render_template, request, jsonify, redirect, url_for
import firebase_admin
from firebase_admin import credentials, auth, firestore

app = Flask(__name__)

# --- 1. INITIALIZE FIREBASE ---
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# --- 2. AI KNOWLEDGE BASE (Exercises) ---
# --- PINALAWAK NA AI KNOWLEDGE BASE ---
exercises_data = [
    # --- BASKETBALL ---
    # Goal: Explosiveness
    {"name": "Plyometric Jumps", "sport": "Basketball", "goal": "Explosiveness", "reps": "3 sets of 10", "desc": "Jump onto a box or platform to increase vertical leap."},
    {"name": "Depth Jumps", "sport": "Basketball", "goal": "Explosiveness", "reps": "4 sets of 8", "desc": "Step off a box and immediately jump upward upon landing."},
    {"name": "Rim Touches", "sport": "Basketball", "goal": "Explosiveness", "reps": "3 sets of 15", "desc": "Jump and try to touch the rim or backboard repeatedly."},
    
    # Goal: Endurance
    {"name": "Suicide Sprints", "sport": "Basketball", "goal": "Endurance", "reps": "5 rounds", "desc": "Sprint to the free-throw line, mid-court, and back."},
    {"name": "Full Court Layup Drill", "sport": "Basketball", "goal": "Endurance", "reps": "10 mins", "desc": "Continuous layups from one end of the court to the other."},
    {"name": "Defensive Slides", "sport": "Basketball", "goal": "Endurance", "reps": "4 sets of 1 min", "desc": "Stay low and slide side-to-side across the court."},
    
    # Goal: Strength
    {"name": "Weighted Squats", "sport": "Basketball", "goal": "Strength", "reps": "4 sets of 12", "desc": "Build leg power for post-up and rebounding."},
    {"name": "Push-ups (Explosive)", "sport": "Basketball", "goal": "Strength", "reps": "3 sets of 15", "desc": "Build upper body strength for passing and shooting."},
    {"name": "Plank with Leg Lifts", "sport": "Basketball", "goal": "Strength", "reps": "3 sets of 1 min", "desc": "Core strength for balance while driving to the hoop."},

    # --- VOLLEYBALL ---
    # Goal: Explosiveness
    {"name": "Block Jumps", "sport": "Volleyball", "goal": "Explosiveness", "reps": "3 sets of 15", "desc": "Rapid jumping at the net to simulate blocking."},
    {"name": "Broad Jumps", "sport": "Volleyball", "goal": "Explosiveness", "reps": "4 sets of 10", "desc": "Jump forward as far as possible to build leg power."},
    
    # Goal: Endurance
    {"name": "Lateral Shuffles", "sport": "Volleyball", "goal": "Endurance", "reps": "4 sets of 1 min", "desc": "Quick side-to-side movements for floor defense."},
    {"name": "Mountain Climbers", "sport": "Volleyball", "goal": "Endurance", "reps": "3 sets of 45 secs", "desc": "Build stamina and core stability."},
    
    # Goal: Strength
    {"name": "Shoulder Press", "sport": "Volleyball", "goal": "Strength", "reps": "3 sets of 10", "desc": "Strengthen shoulders for more powerful spikes."},
    {"name": "Glute Bridges", "sport": "Volleyball", "goal": "Strength", "reps": "3 sets of 20", "desc": "Strengthen glutes for better jumping and stability."}
]

# --- 3. ROUTES (PAGES) ---

@app.route('/')
def index():
    return render_template('index.html')

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

@app.route('/dashboard/<uid>')
def dashboard(uid):
    user_doc = db.collection('users').document(uid).get()
    if user_doc.exists:
        return render_template('dashboard.html', user=user_doc.to_dict(), uid=uid)
    return "User not found", 404

# --- 4. AI & LOGGING LOGIC ---

@app.route('/get_recommendation/<uid>')
def get_recommendation(uid):
    try:
        user_doc = db.collection('users').document(uid).get().to_dict()
        user_sport = user_doc.get('sport')
        user_goal = user_doc.get('goal')

        # AI Recommendation Logic
        recommendations = [ex for ex in exercises_data if ex['sport'] == user_sport and ex['goal'] == user_goal]
        
        # Fallback kung walang mahanap
        if not recommendations:
            recommendations = [ex for ex in exercises_data if ex['sport'] == user_sport]
            
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


# --- LOGIN PAGE ---
@app.route('/login_page')
def login_page():
    return render_template('login.html')

# --- LOGIN LOGIC (Simulated for Capstone) ---
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    
    try:
        # Hahanapin natin ang user sa Firestore gamit ang email
        users_ref = db.collection('users').where('email', '==', email).limit(1).stream()
        user_data = None
        uid = None
        
        for doc in users_ref:
            user_data = doc.to_dict()
            uid = doc.id
            
        if user_data:
            return jsonify({"message": "Login Successful", "uid": uid}), 200
        else:
            return jsonify({"error": "User not found. Please register."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# --- PROFILE VIEW (Stats Page) ---
@app.route('/profile_view/<uid>')
def profile_view(uid):
    try:
        user_doc = db.collection('users').document(uid).get().to_dict()
        
        # Calculate BMI (Body Mass Index) - Maganda itong feature sa Capstone!
        height_m = float(user_doc.get('height', 0)) / 100
        weight_kg = float(user_doc.get('weight', 0))
        bmi = 0
        if height_m > 0:
            bmi = round(weight_kg / (height_m * height_m), 1)
            
        # Bilangin ang total workouts na natapos
        logs = db.collection('workout_logs').where('uid', '==', uid).get()
        total_workouts = len(logs)
        
        return render_template('profile_view.html', user=user_doc, uid=uid, bmi=bmi, total=total_workouts)
    except Exception as e:
        return str(e), 500
        # --- 7. HISTORY PAGE (Para sa Discipline Tracking) ---
@app.route('/history/<uid>')
def history(uid):
    try:
        # Kunin ang data ng user
        user_doc = db.collection('users').document(uid).get().to_dict()
        
        # Kunin ang lahat ng natapos na workout ni user (naka-sort by latest)
        # Gagamit tayo ng .order_by() para sa timestamp
        logs_ref = db.collection('workout_logs').where('uid', '==', uid).order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
        
        logs = []
        for doc in logs_ref:
            log_data = doc.to_dict()
            # I-format natin ang timestamp para mabasa ng tao sa HTML
            if 'timestamp' in log_data and log_data['timestamp']:
                log_data['date_formatted'] = log_data['timestamp'].strftime('%b %d, %Y - %I:%M %p')
            logs.append(log_data)

        return render_template('history.html', logs=logs, user=user_doc, uid=uid)
    except Exception as e:
        # Kung mag-error dahil sa "Index", ibig sabihin kailangan i-click yung link sa Termux logs
        return str(e), 500
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
@app.route('/history/<uid>')
def history(uid):
    try:
        # Kunin ang lahat ng logs ni user, i-sort by date (latest first)
        logs_ref = db.collection('workout_logs').where('uid', '==', uid).order_by('timestamp', direction=firestore.Query.DESCENDING)
        logs = [doc.to_dict() for doc in logs_ref.stream()]
        
        # Kunin din ang user info para sa header
        user_data = db.collection('users').document(uid).get().to_dict()
        
        return render_template('history.html', logs=logs, user=user_data, uid=uid)
    except Exception as e:
        return str(e), 500