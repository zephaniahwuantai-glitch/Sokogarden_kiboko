from flask import *
import pymysql
from flask_cors import CORS
import os #it allow python code to talk/communicate with the os(linux,windows,macos)
app= Flask(__name__)
CORS(app)#allows request from external origins
#configure our upload folder
app.config['UPLOAD_FOLDER']='static/images'
@app.route('/api/signup',methods=['POST'])
def signup():
    # extract values posted in the request and store them in variables
    username=request.form['username']
    email=request.form['email']
    password=request.form['password']
    phone=request.form['phone']

    # connect to our database
    connection=pymysql.connect(host='localhost',user='root',password='',database='dailyyoghurts_kiboko')
     # initialize the connection
    cusor=connection.cursor()

    # do the sql query to insert the data of the four columns
    sql='insert into users(username,email,password,phone) values(%s,%s,%s,%s)'
    # create data to replace the placeholders
    data=(username,email,password,phone)
    cusor.execute(sql,data)
# we need to commit/save changes
    connection.commit()

    return jsonify({'success':'Thankyou for joning'})
    # initialize the connection
    cusor=connection.cursor

    # singin route
@app.route('/api/signin',methods=['POST'])
def signin():
    username=request.form['username']
    password=request.form['password']

    connection=pymysql.connect(host='localhost',user='root',password='',database='dailyyoghurts_kiboko')

    cursor=connection.cursor(pymysql.cursors.DictCursor)
    sql='select * from users where username=%s and password=%s'
    data=(username,password)
    cursor.execute(sql,data)

    count=cursor.rowcount
    if count==0:
        return jsonify({'message':'login failed'})
    else:
        user=cursor.fetchone()
        #remove the password key
        user.pop('password', None)
        return jsonify({'message':'login successful','user':user})
    #Add products
@app.route('/api/addproduct',methods=['POST'])
def addproduct():
    #exract data from the request
    product_name=request.form['product_name']
    product_description=request.form['product_description']
    product_cost=request.form['product_cost']
    product_photo=request.files['product_photo']
    #get the image file name
    filename=product_photo.filename
    #specify computer path where the image will be saved
    photo_path=os.path.join(app.config['UPLOAD_FOLDER'],filename)
    #save the above path
    product_photo.save(photo_path)
    
#conect to our database
    connection=pymysql.connect(host='localhost',user='root',password='',database='dailyyoghurts_kiboko')
    #connect cursor
    cursor=connection.cursor(pymysql.cursors.DictCursor)

    # do the sql query to insert the data of the four columns
    sql='insert into product_details(product_name,product_description,product_cost,product_photo) values(%s,%s,%s,%s)'
    # create data to replace the placeholders
    data=(product_name,product_description,product_cost,filename)
    cursor.execute(sql,data)
# we need to commit/save changes
    connection.commit()

    return jsonify({'success':'Thankyou for adding product'})
# get products
@app.route('/api/get_product_details')
def get_product_details():
# connection
    connection=pymysql.connect(host='localhost',user='root',password='',database='dailyyoghurts_kiboko')
    # creating a cursor object
    cursor=connection.cursor(pymysql.cursors.DictCursor)
    sql='select * from product_details'
    # execute sql
    cursor.execute(sql)
    # get product in form of a dictionary
    product_details=cursor.fetchall()
    # return product
    return jsonify(product_details)
# Mpesa Payment Route 
import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth

@app.route('/api/mpesa_payment', methods=['POST'])
def mpesa_payment():
        if request.method == 'POST':
            # Extract POST Values sent
            amount = request.form['amount']
            phone = request.form['phone']

            # Provide consumer_key and consumer_secret provided by safaricom
            consumer_key = "GTWADFxIpUfDoNikNGqq1C3023evM6UH"
            consumer_secret = "amFbAoUByPV2rM5A"

            # Authenticate Yourself using above credentials to Safaricom Services, and Bearer Token this is used by safaricom for security identification purposes - Your are given Access
            api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"  # AUTH URL
            # Provide your consumer_key and consumer_secret 
            response = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
            # Get response as Dictionary
            data = response.json()
            # Retrieve the Provide Token
            # Token allows you to proceed with the transaction
            access_token = "Bearer" + ' ' + data['access_token']

            #  GETTING THE PASSWORD
            timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')  # Current Time
            passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'  # Passkey(Safaricom Provided)
            business_short_code = "174379"  # Test Paybile (Safaricom Provided)
            # Combine above 3 Strings to get data variable
            data = business_short_code + passkey + timestamp
            # Encode to Base64
            encoded = base64.b64encode(data.encode())
            password = encoded.decode()

            # BODY OR PAYLOAD
            payload = {
                "BusinessShortCode": "174379",
                "Password":password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": "1",  # use 1 when testing
                "PartyA": phone,  # change to your number
                "PartyB": "174379",
                "PhoneNumber": phone,
                "CallBackURL": "https://coding.co.ke/api/confirm.php",
                "AccountReference": "SokoGarden Online",
                "TransactionDesc": "Payments for Products"
            }

            # POPULAING THE HTTP HEADER, PROVIDE THE TOKEN ISSUED EARLIER
            headers = {
                "Authorization": access_token,
                "Content-Type": "application/json"
            }

            # Specify STK Push  Trigger URL
            url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  
            # Create a POST Request to above url, providing headers, payload 
            # Below triggers an STK Push to the phone number indicated in the payload and the amount.
            response = requests.post(url, json=payload, headers=headers)
            print(response.text) # 
            # Give a Response
            return jsonify({"message": "An MPESA Prompt has been sent to Your Phone, Please Check & Complete Payment"})


if __name__=='__main__': 
    app.run(debug=True)