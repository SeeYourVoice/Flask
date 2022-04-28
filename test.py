from flask import Flask
from flask import request
app = Flask(__name__)


@app.route("/sendFile" , methods=['GET' , 'POST'])
def send_string() :
    if request.method == "POST":
        f = request.files['files'].save("C:/files/" + request.files['files'].filename)
    return "SUCCESS"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555 , debug=True)