import io
import pandas as pd
import sqlite3
from django.db import models
from django.db import connection as sqlite3db, OperationalError
from django.contrib import messages
from django.shortcuts import render
from django.apps import apps
from .models import Dataset, DatasetName
from sqlalchemy import create_engine


################################################
#           Error Codes Used for DeBug         #
#   300 = Successfully Saved CSV File          #
#   301 = Dataset already exists               #
#   400 = Successful Connection to DB          #
#   401 - Connection Failed with Some Error    #
# ###############################################

# Custom Dictionary add Method



class CustomDictionary(dict):
    # __init__ function
    def __init__(self):
        self = dict()

    # Function to add key:value
    def add(self, key, value):
        self[key] = value


# Create your views here.


def homeScreen(request):
    return render(request, "simpleDataApp/navBar.html")


def computeScreen(request):
    ListOfDatasetNames = []
    dataSetQuery = DatasetName.objects.all()
    if request.method == "GET":
        print(list(dataSetQuery.values()))
        #print(dsNames)
        return render(request, "simpleDataApp/plotPage.html", {'dsNames' : dataSetQuery})

    else:
        computedValue = computeValue(request)
    return render(request, "simpleDataApp/plotPage.html", {'minOrmax': computedValue,
                  'dsNames': dataSetQuery})


def computeValue(request):
    dbconnection = create_engine('sqlite:///db.sqlite3').connect()
    # selectQuery = "SELECT *FROM " + request.POST['dataSet'] + ";"
    dataSet = pd.read_sql( request.POST['dataSet'], dbconnection)
    columnChoice = request.POST['columnChoice']
    columns = list(dataSet.columns.values)
    if int(request.POST['computeMode']) == 0:
        return min(dataSet[columns[int(columnChoice)]])
    else:
        return max(dataSet[columns[int(columnChoice)]])


def uploadScreen(request):
    if request.method == "GET":
        dataSetQuery = DatasetName.objects.all()
        return render(request, "simpleDataApp/upload.html", {'dsNames' : dataSetQuery})
    else:
        return uploadCSVFile(request)


def uploadCSVFile(request):
    datasetName = request.POST['datasetName']
    datasetUploaded = DatasetName(name=datasetName)
    datasetUploaded.save()
    print(datasetName)
    uploadedFile = io.StringIO()
    alertType = {
        'info': 'alert-success'
    }
    try:
        uploadedFile = request.FILES['file']
    except KeyError:
        alertType['info'] = "alert-warning"
        messages.info(request, 'Dude, Upload a .csv file')
        return render(request, "simpleDataApp/upload.html", alertType)
    if not uploadedFile.name.endswith('.csv'):
        alertType['info'] = "alert-warning"
        messages.info(request, 'Dude, Please upload only  .csv File')
        return render(request, "simpleDataApp/upload.html", alertType)
    elif saveUploadedFile(datasetName, request.FILES['file']) == 300:
        alertType['info'] = "alert-success"
        messages.info(request, 'Alright, Dataset ' + str(datasetName) + ' is created/updated.')
    else:
        alertType['info'] = "alert alert-danger"
        messages.info(request, 'Oh No, Looks like Dataset ' + str(datasetName) +
                      ' already exists, please use another name')
    return render(request, "simpleDataApp/upload.html", alertType)


def saveUploadedFile(datasetName, csvFile):
    dataframeCSV = pd.read_csv(csvFile)
    datasetQueries = []
    for index in range(0, len(dataframeCSV.index)):
        eachRow = list(dataframeCSV.iloc[index])
        datasetQueries.append(Dataset(column1=float(eachRow[0]), column2=float(eachRow[1])))
    Dataset.objects.bulk_create(datasetQueries)
    tableHeaders = list(dataframeCSV.columns.values)
    errorCode, dbconn = getDatabaseConnection()
    try:
        dataframeCSV.to_sql(datasetName, con=dbconn, if_exists='append', index=False)
        return 300
    except ValueError:
        return 301
    dbconn.commit()


def getDatabaseConnection():
    try:
        conn = sqlite3.connect("db.sqlite3")
    except sqlite3.Error as connError:
        print("Error While : Opening Connection : " + (' '.join(connError.args)))
        return 401
    return 400, conn


def plotGraph(request):
    dsNameForGraph = request.GET['dataSetPlot']
    col1ForGraph = request.GET['column1Plot']
    col2ForGraph = request.GET['column2Plot']
    firstCol25Val, secondCol25Val = get25ValOfDataset(dsNameForGraph, col2ForGraph, col1ForGraph)
    print(firstCol25Val)
    dataSetQuery = DatasetName.objects.all()
    return render(request, "simpleDataApp/plotPage.html", {"col1Values" : firstCol25Val,
                                                           "col2Values": secondCol25Val,
                                                           "dsNames" : dataSetQuery})


def get25ValOfDataset(datasetName, col2Name, col1Name):
    errorCode, dbconnection = getDatabaseConnection()
    selectQuery = "SELECT *FROM " + datasetName + ";"
    dataSet = pd.read_sql(selectQuery, dbconnection)
    print(dataSet)
    col1Values = list(dataSet[col1Name].head(25))
    col2Values = list(dataSet[col2Name].head(25))
    print(type(col2Values))
    return col1Values, col2Values























    """
    print(secondCol25Val)                                                                            createQuery = "CREATE TABLE [IF NOT EXISTS] " + str(datasetName) + " ( "

    # Assigning the Columns headers from the CSV file to Query String
    for eachHeader in range(0, len(tableHeaders)):
        if eachHeader != (len(tableHeaders) - 1):
            createQuery = createQuery + tableHeaders[eachHeader] + " REAL, "
        else:
            createQuery = createQuery + tableHeaders[eachHeader] + " REAL"
    print(createQuery)
    createQuery = createQuery + ");"
    cursor = sqlite3db.cursor()
    try:
        cursor.execute(createQuery)
    except OperationalError:
        return 301
    
    if errorCode == 401:
        return 401
    else:
    """










    

        
