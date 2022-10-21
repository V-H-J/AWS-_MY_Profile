from flask import Flask, render_template, request, flash, redirect,url_for, jsonify, session 
from flask import Response,send_file
from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
import pymysql
import boto3
import json
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import os
from datetime import datetime



app = Flask(__name__)

app.config['S3_KEY'] = "AKIA6BGE6E65ZS7P2MZK"
app.config['S3_SECRET'] = "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"
app.config['AWS_REGION'] = "us-east-2"

app.config['SECRET_KEY'] = "vhj"

s3 = boto3.client(
   "s3",
   aws_access_key_id=app.config['S3_KEY'],
   aws_secret_access_key=app.config['S3_SECRET'],
   region_name= app.config['AWS_REGION']
)


ENDPOINT="database-1.cum7eogqifjn.us-east-2.rds.amazonaws.com"
PORT="3306"
USR="admin"
PASSWORD="VHJmysql19"
DBNAME="finalproject"

conn = pymysql.connect(
        host= ENDPOINT, 
        user = USR, 
        password = PASSWORD,
        database = DBNAME,
                )

cur =conn.cursor()


class MyForm(FlaskForm):
    userfirstname = StringField('   First Name   ')
    userlastname = StringField('Last Name')
    useremail = StringField('Email / User-Name')
    password1 = StringField('Password')
    register = SubmitField('Register')


class MyForm1(FlaskForm):
    userlogin_name = StringField('User Name/ Email')
    userlogin_pass =  StringField('Password')
    submit = SubmitField('login')



@app.route('/notfound')
def notfound():
     return render_template("usernotfound.html")




###### login ####

@app.route('/', methods=['GET','POST'])
def login():
    
    form1=MyForm1()

    login_username = request.form.get("email")
    login_userpass = request.form.get("password")
    try:
            conn =  pymysql.connect(host=ENDPOINT, user=USR, password=PASSWORD, database=DBNAME)
            cur = conn.cursor()
            
            if form1.validate_on_submit():
                login_username = form1.userlogin_name.data
                login_userpass = form1.userlogin_pass.data

                har_qry= "SELECT * FROM hari_userdetails Where email ='"+login_username+"' AND password = '"+login_userpass+"';"
                print(har_qry)

                cur.execute("SELECT * FROM hari_userdetails;")

                har_query_results = cur.fetchall()
                print(har_query_results)

                cur.execute("SELECT * FROM hari_userdetails Where email ='"+login_username+"' AND password = '"+login_userpass+"';")
                
                har_query_results = cur.fetchall()
                print(har_query_results)
                if len(har_query_results)==1:
                    return render_template("upload.html")
                else:
                    return redirect("/notfound")
    except Exception as e:
            print("Database connection failed due to {}".format(e))
            return redirect("/")
    return  render_template('login.html',form=form1)



### signup ###

@app.route ('/signup', methods=['GET','POST'])
def main1():

    user_fname = False
    user_lname = False
    user_email = False
    passwords = False

    form = MyForm()
    if form.validate_on_submit():
        user_fname = form.userfirstname.data
        user_lname = form.userlastname.data
        user_email = form.useremail.data
        passwords = form.password1.data

        print(user_fname, user_lname, user_email, passwords)

        conn =  pymysql.connect(host=ENDPOINT, user=USR, password=PASSWORD, database=DBNAME)
        cur = conn.cursor()

        cur.execute("INSERT INTO hari_userdetails(firstname,lastname,email,password) VALUES('"+user_fname+"', '"+user_lname+"','"+user_email+"','"+passwords+"');")
        print("Insert Success")
        conn.commit()
        
        form.userfirstname.data = ''
        form.userlastname.data = ''
        form.useremail.data = ''
        form.password1.data = ''
               
        return redirect('/')

    return  render_template('signup.html',form=form)





##### upload file ###

BUCKET_NAME='vhjfinalproject'


@app.route('/upload',methods=['post'])
def upload():
    
    variable  = request.form.get('variable')
    emails = variable.split(',')

    emails = [email.strip() for email in emails]

    datetime_now = datetime.now().strftime("%Y%m%d%HH%MM%S")
    topic =create_topic(f"topic_name_{datetime_now}".replace(" ",""))


    for i in emails:
        subscribe(topic["TopicArn"], i)

    if request.method == 'POST':
        allfiles = request.files['file']
        if allfiles:
                file_example = secure_filename(allfiles.filename)
                allfiles.save(file_example)
                s3.upload_file(
                    Bucket = BUCKET_NAME,
                    Filename=file_example,
                    Key = file_example
                )
                message = " File is Uploaded to s3 !!!!!"
    
        Filename= f"https://{BUCKET_NAME}.s3.us-east-2.amazonaws.com/{file_example}" 

        conn =  pymysql.connect(host=ENDPOINT, user=USR, password=PASSWORD, database=DBNAME)
        cur = conn.cursor()

        cur.execute("INSERT INTO hari_filedetails(filename,fileurl) VALUES('"+file_example+"', '"+Filename+"');")
        print("Insert Success")
        conn.commit()

        return render_template("verifyemail.html",  topic=topic["TopicArn"], Filename=Filename)

    return render_template("upload.html",message =message)



def create_topic(topic_1):
     
    sns = boto3.client("sns", 
    region_name='us-east-2', 
    aws_access_key_id=app.config['S3_KEY'],
    aws_secret_access_key=app.config['S3_SECRET']
    )
    print(topic_1)
    topic = sns.create_topic(Name=topic_1)
    return topic


def subscribe(topic, email):

    sns = boto3.client("sns", 
    region_name='us-east-2', 
    aws_access_key_id=app.config['S3_KEY'],
    aws_secret_access_key=app.config['S3_SECRET']
    )

    subscription = sns.subscribe(Protocol='email', Endpoint=email, TopicArn =topic)

    return subscription



@app.route('/verifyemail',methods=['post'])
def emailsns():
    if request.method == "POST":
        topic = request.form["topic"]
        Filename = request.form["filename"]
        lambda_client = boto3.client('lambda',
        aws_access_key_id=app.config['S3_KEY'],
        aws_secret_access_key=app.config['S3_SECRET'],
        region_name='us-east-2')

        lambda_payload={"TOPIC_ARN":topic, "MESSAGE":Filename}
        lambda_client.invoke(FunctionName='lambdatest1',
                        Payload=json.dumps(lambda_payload))

        return render_template("verifyemails.html")


if __name__ == "__main__":
    
    app.run(host='0.0.0.0')