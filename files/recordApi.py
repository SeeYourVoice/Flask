import requests
import json

from wordcloud import WordCloud
import boto3
import os

# from konlpy.tag import Kkma


from flask import Flask
from flask import request
app = Flask(__name__)



@app.route("/sendFile" , methods=['GET' , 'POST'])
def send_string() :


    if request.method == "POST":
        # flask서버 이용시 ../recordfile/ -> ./files로 경로 변경
        # f = request.files['files'].save("./files/" + request.files['files'].filename)
        f = request.files['files'].save("../recordfile/" + request.files['files'].filename)
        # f = request.files['files'].save("C:/files/" + request.files['files'].filename)

    class ClovaSpeechClient:
        # Clova Speech invoke URL
        invoke_url = 'https://clovaspeech-gw.ncloud.com/external/v1/2444/3ac52ed2406f35311db879e1cfc606c18817c38f249db118729130a76af210d3'
        # Clova Speech secret key
        secret = 'dabe9d5210854cbab51f3d8fe0b68600'

        def req_url(self, url, completion, callback=None, userdata=None, forbiddens=None, boostings=None,
                    wordAlignment=True, fullText=True, diarization=None):
            request_body = {
                'url': url,
                'language': 'ko-KR',
                'completion': completion,
                'callback': callback,
                'userdata': userdata,
                'wordAlignment': wordAlignment,
                'fullText': fullText,
                'forbiddens': forbiddens,
                'boostings': boostings,
                'diarization': diarization,
            }
            headers = {
                'Accept': 'application/json;UTF-8',
                'Content-Type': 'application/json;UTF-8',
                'X-CLOVASPEECH-API-KEY': self.secret
            }
            return requests.post(headers=headers,
                                 url=self.invoke_url + '/recognizer/url',
                                 data=json.dumps(request_body).encode('UTF-8'))


        def req_object_storage(self, data_key, completion, callback=None, userdata=None, forbiddens=None,
                               boostings=None,
                               wordAlignment=True, fullText=True, diarization=None):
            request_body = {
                'dataKey': data_key,
                'language': 'ko-KR',
                'completion': completion,
                'callback': callback,
                'userdata': userdata,
                'wordAlignment': wordAlignment,
                'fullText': fullText,
                'forbiddens': forbiddens,
                'boostings': boostings,
                'diarization': diarization,
            }
            headers = {
                'Accept': 'application/json;UTF-8',
                'Content-Type': 'application/json;UTF-8',
                'X-CLOVASPEECH-API-KEY': self.secret
            }
            return requests.post(headers=headers,
                                 url=self.invoke_url + '/recognizer/object-storage',
                                 data=json.dumps(request_body).encode('UTF-8'))

        def req_upload(self, file, completion, callback=None, userdata=None, forbiddens=None, boostings=None,
                       wordAlignment=True, fullText=True, diarization=None):
            request_body = {
                'language': 'ko-KR',
                'completion': completion,
                'callback': callback,
                'userdata': userdata,
                'wordAlignment': wordAlignment,
                'fullText': fullText,
                'forbiddens': forbiddens,
                'boostings': boostings,
                'diarization': diarization,
            }
            headers = {
                'Accept': 'application/json;UTF-8',
                'X-CLOVASPEECH-API-KEY': self.secret
            }
            print(json.dumps(request_body, ensure_ascii=False).encode('UTF-8'))
            files = {
                'media': open(file, 'rb'),
                'params': (None, json.dumps(request_body, ensure_ascii=False).encode('UTF-8'), 'application/json')
            }
            response = requests.post(headers=headers, url=self.invoke_url + '/recognizer/upload', files=files)
            return response

    if __name__ == '__main__':
        # res = ClovaSpeechClient().req_url(url='http://example.com/media.mp3', completion='sync')
        # res = ClovaSpeechClient().req_object_storage(data_key='data/media.mp3', completion='sync')

        # flask서버 이용시 ../recordfile/ -> ./files/record.wav 로 변경
        # res = ClovaSpeechClient().req_upload(file='./files/record.wav', completion='sync')
        res = ClovaSpeechClient().req_upload(file='../recordfile/record.wav', completion='sync')
        # res = ClovaSpeechClient().req_upload(file='C:/files/record.wav', completion='sync')

        # print(res.text)

    data = json.loads(res.text)

    # for i in range(len(data['segments'])):
    #     if len(data['segments'][i]['textEdited']) != 0:
    #         print(data['segments'][i]['speaker']['name'] + ":" + data['segments'][i]['textEdited'])

    text_list = []
    for i in range(len(data['segments'])):
        if len(data['segments'][i]['textEdited']) != 0:
            text_list.append(data['segments'][i]['speaker']['name'] + ":" + data['segments'][i]['textEdited'])

    test_result = ""

    for i in text_list:
        test_result = test_result + i + ','

    # print(test_result)



   ################################## 워드클라우드##############################
    text = data['text']

         # 텍스트 명사화(조사제거)

    # kkma = Kkma()
    # text_noun = str(kkma.nouns(text))
    #
    wordcloud = WordCloud(font_path='malgun', background_color='white').generate(text)
    count = str(len(os.listdir("./images")))
    wordcloud.to_file(f"./images/{count}Test.jpg")
    ###########################################################################
    
    
    
    #################### AWS업로드######################
    s3 = boto3.client('s3')

        # 업로드할 파일
    filename = f"./images/{count}Test.jpg"

        # 업로드할 s3 bucket 이름
    bucket_name = 'momoyami'

        # 저장명
        # savename = filename
    savename = filename

    s3.upload_file(filename, bucket_name, savename, ExtraArgs={'ContentType': 'image/jpg'})
    ####################################################

    url = "https://momoyami.s3.us-east-2.amazonaws.com/" + filename




################ DB insert#################################
    import cx_Oracle

    # conn = cx_Oracle.connect('사용자이름/비밀번호@localhost:1521/xe')
    conn = cx_Oracle.connect('ai1_nmr_oracle/smhrd123@project-db-stu.ddns.net:1524/xe')

    # DB연결
    cs = conn.cursor()

    # sql = "insert into t_record_text (col01,col02,col03) values (:1,:2,:3)"
    # cs.execute(sql,('3','3','3'))	# --execute => sql문 실행

    sql = 'insert into t_record_text(REC_TEXT, REC_FULLTEXT, REC_WORDCLOUD) values (:apitext, :fulltest, :url)'
    # cs.execute(sql, test = test_result)

    cs.execute(sql, apitext=test_result, fulltest = data['text'], url = url)

    print(cs.rowcount)

    cs.close()
    conn.commit()
    conn.close()



    return "SUCCESS"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555 , debug=True)



