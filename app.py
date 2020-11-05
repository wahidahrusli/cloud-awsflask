from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_bootstrap import Bootstrap
from filters import datetimeformat, file_type
from resources import get_bucket, get_bucket_list, get_s3_client, get_s3_resources, get_dynamodb_resources, get_dynamodb_client, get_table_list, get_table_name, get_table
from boto3.dynamodb.conditions import Key, Attr

app = Flask(__name__)
Bootstrap(app)
app.secret_key='secret'
app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.filters['file_type'] = file_type

# Browser
@app.route('/')
def index():
    return render_template('index.html')

## S3 ##

# 'GET': Display list of buckets
# 'POST': Get choosen bucket
@app.route('/buckets', methods=['GET', 'POST'])
def buckets():
    if request.method == 'POST':
        bucket = request.form['bucket']
        session['bucket'] = bucket
        return redirect(url_for('files'))
    else:
        buckets = get_bucket_list()
        return render_template('buckets.html', buckets=buckets)

# Create & add buckets
@app.route('/addbucket', methods=['POST'])
def addbucket():
    bucket_name = request.form['bucket_name']

    s3 = get_s3_client()
    s3.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={
            'LocationConstraint': 'ap-southeast-1'
        }
    )

    flash('Bucket added succesfully.')
    return redirect(url_for('buckets'))

# Delete bucket
@app.route('/deletebucket', methods=['POST'])
def deletebucket():
    bucket_name = request.form['bucket_name']

    s3 = get_s3_resources()
    s3.Bucket(bucket_name).delete()

    flash('Bucket deleted succesfully.')
    return redirect(url_for('buckets'))

# Display list of objects
@app.route('/files')
def files():
    my_bucket = get_bucket()
    summaries = my_bucket.objects.all()

    return render_template('files.html', my_bucket=my_bucket, files=summaries)

# Upload item to bucket
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    bucket = request.form['bucket']
    session['bucket'] = bucket

    s3 = get_s3_resources()
    my_bucket = s3.Bucket(bucket)
    my_bucket.Object(file.filename).put(Body=file)

    flash('File uploaded succesfully.')
    return redirect(url_for('files'))


# Delete item in a bucket
@app.route("/delete", methods=['POST'])
def delete():
    key = request.form['key']
    bucket = request.form['bucket']
    session['bucket'] = bucket

    s3 = get_s3_resources()
    my_bucket = s3.Bucket(bucket)
    my_bucket.Object(key).delete()

    flash('File deleted successfully.')
    return redirect(url_for('files'))


## DYNAMODB

# 'GET': Display list of table
# 'POST': Get chosen table
@app.route("/dynamodb", methods=['GET', 'POST'])
def dynamodb():
    if request.method == 'POST':
        table = request.form['table']
        session['table'] = table
        return redirect(url_for('table'))
    else:
        tables = get_table_list()
        return render_template('dynamo.html', tables=tables)

# Create & add table - Only works with smartphone attributes
@app.route("/addtable", methods=['POST'])
def addtable():
    table_name = request.form['table_name']

    dynamo = get_dynamodb_client()
    dynamo.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'name',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'KeyType': 'N'
            },
            {
                'AttributeName': 'name',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )

    flash('Table added successfully.')
    return redirect(url_for('dynamodb'))

# Delete table
@app.route("/deletetable", methods=["POST"])
def deletetable():
    table_name = request.form['table_name']
    print(table_name)

    dynamo = get_dynamodb_resources()
    table = dynamo.Table(table_name)
    table.delete()

    flash('Table deleted successfully.')
    return redirect(url_for('dynamodb'))
    

# 'GET': Display list of items
# 'POST': Filter items
@app.route("/table", methods=["GET","POST"])
def table():
    table = get_table()

    if request.method == 'POST':
        attributes = request.form['attributes']
        filter_word = request.form['filter_word']
        print(attributes, filter_word)

        if filter_word == "" or filter_word == None:        
            response = table.scan()
            items = response['Items']
        else:
            response = table.scan(
                FilterExpression=Attr(attributes).eq(filter_word)
            )
            items = response['Items']
            print(items)
    else:
        response = table.scan()
        items = response['Items']

    return render_template('table.html', table=table, items=items)

# Add item to table
@app.route("/additem", methods=["POST"])
def additem():
    table = get_table()

    id_sp = request.form['id']
    name = request.form['name']
    display = request.form['display']
    cpu = request.form['CPU']
    ram = request.form['RAM']
    battery = request.form['battery']
    dimensions = request.form['dimensions']
    weight = request.form['weight']
    
    table.put_item( 
        Item={
            'id': int(id_sp),
            'name': name,
            'display': display,
            'CPU': cpu,
            'RAM': ram,
            'battery': battery,
            'dimensions': dimensions,
            'weight': weight
        }
    )

    flash('Item added successfully.')
    return redirect(url_for('table'))

# Delete item in a table
@app.route("/deleteitem", methods=["POST"])
def deleteitem():
    table = get_table()

    id_sp = request.form['id']
    name = request.form['name']

    table.delete_item(
        Key={
            'id': int(id_sp),
            'name': name
        }
    )

    flash('File deleted successfully.')
    return redirect(url_for('table'))


if __name__ == '__main__':
    app.run()