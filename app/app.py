from flask import Flask, render_template, request, jsonify, session
from flask_httpauth import HTTPBasicAuth
from freeplay import SessionInfo
from chat import getCompletion, newConvo, record_customer_feedback
from helperFuncs import generate_random_string
from dotenv import load_dotenv
import os

app = Flask(__name__, template_folder='./frontend/views', static_folder='./frontend/public')
load_dotenv("./.env")
app.secret_key = os.getenv("APP_PASSWORD")

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    if password == os.getenv("APP_PASSWORD"):
        return True
    else:
        print("Invalid password")
        print(password, os.getenv("APP_PASSWORD"))



@app.route('/')
@auth.login_required
def home():
    # start a new convo by instantiating a session
    thread_id = generate_random_string()
    customer_id = auth.current_user()
    session['chat_session'], session['history'] = newConvo(thread_id, customer_id)
    print(session['chat_session'])
    return render_template('index.html')


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.form["user_message"]
    filter = request.form["filter"]
    if filter == "All":
        tag = ["docs", "blogs"]
    else:
        tag = filter
    print(session['chat_session'])
    session_obj = SessionInfo(**session['chat_session'])
    response, session["completion_id"] = getCompletion(message=user_message, history=session['history'],
                                                       session=session_obj, tag=tag)
    # update the history object
    session['history'].append({
        "role": 'user',
        "content": user_message
    })
    session['history'].append({
        "role": 'assistant',
        "content": response
    })
    return jsonify({"response": response})


@app.route("/feedback", methods=["POST"])
def feedback():
    feedback = request.form["feedback"]
    if feedback == 'link_click':
        feedback = {"link_click": True}
    elif feedback == 'thumbs_up':
        feedback = {"customer_satisfaction": "freeplay-positive-feedback"}
    elif feedback == 'thumbs_down':
        feedback = {"customer_satisfaction": "freeplay-negative-feedback"}
    else:
        print("Invalid feedback type")
    
    record_customer_feedback(session["completion_id"], feedback)
    return jsonify({"response": "success"})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)