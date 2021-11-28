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
#   403 - Empty Dataset                        #
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
    return render(request, "simpleDataApp/index.html")


def computeScreen(request):
    ListOfDatasetNames = []
    dataSetQuery = DatasetName.objects.all()
    if request.method == "GET":
        print(list(dataSetQuery.values()))
        #print(dsNames)
        return render(request, "simpleDataApp/plotPage.html", {'dsNames' : dataSetQuery})

    else:
        computedValue = computeValue(request)
        if computedValue == 403:
            return render(request, "simpleDataApp/plotPage.html", {'info': 'alert-warning', 'dsNames': dataSetQuery})
    return render(request, "simpleDataApp/plotPage.html", {'minOrmax': computedValue,
                  'dsNames': dataSetQuery})


def computeValue(request):
    dbconnection = create_engine('sqlite:///db.sqlite3').connect()
    # selectQuery = "SELECT *FROM " + request.POST['dataSet'] + ";"
    try:
        dataSet = pd.read_sql( request.POST['dataSet'], dbconnection)
    except KeyError:
        messages.info(request, "Select Dataset first, in Compute Form")
        return 403
    try:
        columnName = request.POST['columnNameForCompute']
        columns = list(dataSet[columnName])
    except KeyError:
        messages.info(request, "Please Enter a Valid Column Name in Compute Form")
        return 403
    if int(request.POST['computeMode']) == 0:
        return min(columns)
    else:
        return max(columns)


def uploadScreen(request):
    if request.method == "GET":
        dataSetQuery = DatasetName.objects.all()
        return render(request, "simpleDataApp/upload.html", {'dsNames' : dataSetQuery})
    else:
        return uploadCSVFile(request)


def uploadCSVFile(request):
    datasetName = request.POST['datasetName']
    # CUSTOM ALERT MESSAGE BASED ON FORM VALIDATION
    alertType = 'alert-success'
    dataSetQuery = DatasetName.objects.all()
    # Validation of the Form Fields - This must be actually be done at the Client Side, but for time being, I Proceeded.
    try:
        uploadedFile = request.FILES['file']

    # EMPTY FILE CASE
    except KeyError:
        alertType= "alert-warning"
        messages.info(request, 'Dude, Upload a .csv file')
        return render(request, "simpleDataApp/upload.html", {'info':alertType,
                                                             'dsNames': dataSetQuery})

    # INCORRECT FORMAT CASE
    if not uploadedFile.name.endswith('.csv'):
        alertType = "alert-warning"
        messages.info(request, 'Dude, Please upload only  .csv File')
        return render(request, "simpleDataApp/upload.html", {'info':alertType,
                                                             'dsNames': dataSetQuery})

    # SUCCESSFULLY UPLOADED OR NOT CASE
    elif saveUploadedFile(datasetName, request.FILES['file']) == 300:
        alertType = "alert-success"
        datasetUploaded = DatasetName(name=datasetName)
        datasetUploaded.save()
        messages.info(request, 'Alright, Dataset ' + str(datasetName) + ' is created/updated.')
    else:
        alertType = "alert alert-danger"
        messages.info(request, 'Oh No, Looks like Dataset ' + str(datasetName) +
                      ' already exists, please use another name')
    return render(request, "simpleDataApp/upload.html", {'info':alertType, 'dsNames': dataSetQuery})


def saveUploadedFile(datasetName, csvFile):

    dsNames = DatasetName.objects.all()
    for name in dsNames:
        if datasetName == name.name:
            return 301
    # USING DATAFRAME TO READ UPLOADED CSV FILE
    dataframeCSV = pd.read_csv(csvFile)
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
    dataSetQuery = DatasetName.objects.all()
    try:
        dsNameForGraph = request.GET['dataSetPlot']
    except KeyError:
        messages.info(request, "Choose a Dataset from the list in Plot Graph Form")
        return render(request, "simpleDataApp/plotPage.html", {'info': 'alert-warning','dsNames': dataSetQuery})
    try:
        col1ForGraph = request.GET['column1Plot']
    except KeyError:
        messages.info(request, "Please enter a valid Column1 in the Plot Graph Form")
        return render(request, "simpleDataApp/plotPage.html", {'info': 'alert-warning',
                                                               'dsNames': dataSetQuery})
    try:
        col2ForGraph = request.GET['column2Plot']
    except KeyError:
        messages.info(request, "Please enter a valid Column2 in the Plot Graph Form")
        return render(request, "simpleDataApp/plotPage.html", {'info': 'alert-warning',
                                                               'dsNames': dataSetQuery})
    firstCol25Val, secondCol25Val = get25ValOfDataset(dsNameForGraph, col2ForGraph, col1ForGraph,request)
    if firstCol25Val == 4 and secondCol25Val == 4:
        messages.info(request, "PLease enter a valid Column Name in Plot Graph")
        return render(request, "simpleDataApp/plotPage.html", {'info': "alert-warning",
                                                               'dsNames': dataSetQuery})
    for eachVal in range(0, len(firstCol25Val)):
        try:
            firstCol25Val[eachVal] = float(firstCol25Val[eachVal])
            secondCol25Val[eachVal] = float(secondCol25Val[eachVal])
        except ValueError:
            messages.info(request, "Selected Columns are not Valid to Plot a Graph !")
            return render(request, "simpleDataApp/plotPage.html", {'info': "alert-danger",
                                                                   'dsNames': dataSetQuery})

    return render(request, "simpleDataApp/plotPage.html", {"col1Values": firstCol25Val,
                                                           "col2Values": secondCol25Val,
                                                           "dsNames": dataSetQuery,
                                                           "plotStatus" : "success"})


# A separate Method allows us to increase the values from 25 to more in Future.
def get25ValOfDataset(datasetName, col2Name, col1Name,request):
    errorCode, dbconnection = getDatabaseConnection()
    selectQuery = "SELECT *FROM " + datasetName + ";"
    dataSet = pd.read_sql(selectQuery, dbconnection)
    print(dataSet)
    try:
        col1Values = list(dataSet[col1Name].head(25))
        col2Values = list(dataSet[col2Name].head(25))
    except KeyError:
        return 4, 4
    print(type(col2Values))
    return col1Values, col2Values




    """
    print(secondCol25Val)                                                                           
    createQuery = "CREATE TABLE [IF NOT EXISTS] " + str(datasetName) + " ( "

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










    

        
