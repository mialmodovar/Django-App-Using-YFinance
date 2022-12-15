# Django-App-Using-YFinance
## Group 10 - Module ECS781P - Cloud Computing
### Miguel Almodovar, Venkatraman, Satyam Sharma, Shaurya Rana

## Funtionality



We have built an app with Django which dynamically hits the YFinance RestAPI and displays the stocks details, charts and summaries for the stock ticker entered in the search bar. As displayed in the screenshots below the the user can filter by stock ticker name and date range. The data is retrieved based on the follwoing two ways - 

### System Design - 

<img width="494" alt="image" src="https://user-images.githubusercontent.com/85103905/207682421-811495d8-69d0-43ee-929d-10a08dbe3e8c.png">


## 1. Dynamic REST API

### a) Each search query hits the RestAPI and returns the results via HTML. These are then rendered as summary stats and charts on the webpage. 


<img width="946" alt="image" src="https://user-images.githubusercontent.com/85103905/207667383-0b918a9f-7201-4dca-87d6-345086380061.png">

### 1.1 - Gets stock info from external api and returns it via html

```
@login_required(login_url= 'login')
def stock(request,pk):
    #gets object Ticker from the ticker given in the url and gets the info and last close for it.
    stock = yf.Ticker(pk)
    close = "{:.2f}".format(stock.history(period='1d').Close.values.tolist()[0])
    #sends the current day and the day corresponding to a week ago to load the plot (could be done in js)
    today = datetime.date.today().strftime('%m-%d-%Y')
    week_ago = (datetime.date.today() - datetime.timedelta(days=21)).strftime('%m-%d-%Y')
    context = { 'ticker': pk,'today': today, 'week_ago': week_ago, 'stock':stock.info, 'close':close}
    return render(request,'stocks.html',context)
```

### b) The stocks historical price data is recived as a JSON file using an AJAX request (via a REST based GET command) and then displayed in a candlestick chart using JavaScript. 
This url can also serve regular non-ajax requests, as shown below:

```
r=requests.get('http://127.0.0.1:8000/get/stock?ticker=GOOG&start=11-24-2022&finish=12-15-2022')
print(r.json())
```

```
{'GOOG': {'index': ['2022-11-25 00', '2022-11-28 00', '2022-11-29 00', '2022-11-30 00', '2022-12-01 00', '2022-12-02 00', '2022-12-05 00', '2022-12-06 00', '2022-12-07 00', '2022-12-08 00', '2022-12-09 00', '2022-12-12 00', '2022-12-13 00', '2022-12-14 00'], 'close': [97.5999984741211, 96.25, 95.44000244140625, 101.44999694824219, 101.27999877929688, 100.83000183105469, 99.87000274658203, 97.30999755859375, 95.1500015258789, 93.94999694824219, 93.06999969482422, 93.55999755859375, 95.8499984741211, 95.30999755859375], 'open': [98.46499633789062, 97.19999694824219, 96.0, 95.12000274658203, 101.4000015258789, 99.37000274658203, 99.81500244140625, 99.66999816894531, 96.7699966430664, 95.69000244140625, 93.9000015258789, 93.08999633789062, 98.06999969482422, 95.54000091552734], 'high': [98.94000244140625, 97.83000183105469, 96.38999938964844, 101.44999694824219, 102.58999633789062, 101.1500015258789, 101.75, 100.20999908447266, 97.30999755859375, 95.87000274658203, 94.48999786376953, 93.875, 99.80000305175781, 97.22000122070312], 'low': [97.52999877929688, 95.88999938964844, 94.38999938964844, 94.66999816894531, 100.66999816894531, 99.16999816894531, 99.3550033569336, 96.76000213623047, 95.0250015258789, 93.80000305175781, 93.0199966430664, 91.9000015258789, 95.37999725341797, 93.94000244140625]}}
```
### 1.2 - Gets stock history price from external api and returns it as json

```
@login_required(login_url= 'login')
def loadstock(request):
    #function to handle ajax request for the plot of price history
    pk = request.GET.get("ticker", None)
    start = datetime.datetime.strptime(request.GET.get("start", None), '%m-%d-%Y')
    finish = datetime.datetime.strptime(request.GET.get("finish", None), '%m-%d-%Y')
    if(start > finish):
        return JsonResponse({'error':'Finish date is sooner than start date'},status=400)
    stock = yf.Ticker(pk)
    if stock is None:
        return JsonResponse({'error':'Ticker not found'},status=404)
    data = stock.history(start = start.strftime('%Y-%m-%d'), end = finish.strftime('%Y-%m-%d'))
    index = list(data.index.strftime('%Y-%m-%d %H'))
    print(index)
    close = data.Close.values.tolist()
    print(close)
    open = data.Open.values.tolist()
    high = data.High.values.tolist()
    low = data.Low.values.tolist()
    return JsonResponse( {pk :{'index': index, 'close': close, 'open': open,'high': high, 'low': low}}, status = 200)
```

### 1.3. Setting up the URLs 

```
from django.urls import path

from pages import views

urlpatterns = [
path('',views.index,name='index'),
path('search',views.search,name='search'),
path('stock/<str:pk>',views.stock,name='stock'),
path('get/stock', views.loadstock, name = "loadstock"),
path('login',views.loginPage,name='login'),
path('logout',views.logoutUser,name='logout'),
path('register',views.registerPage,name='register')    
]
```

## 2. User Management - 

There is a user management system in place using a PostgreSQL DB as the backend for storing persistent user data.
The below code snippets otline how the users are created, logged in and their data persisted on the backend DB.


### 2.1- Create user operation

```
@uauthenticated_user
def registerPage(request):
    form = UserForm()
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Your account was created')
            return redirect('login')
        messages.error(request, 'Your password or user is invalid')
        return redirect('register')
    context = {'form' : form}
    return render(request, 'register.html', context)
```

### 2.2 -Reading the user details and logging them in

```
@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username= request.POST.get('username')
        password= request.POST.get('password')
        user= authenticate(request, username=username, password=password)
        if user == None:
             messages.error(request, 'Login information incorrect')
             return redirect('login')
        login(request,user)
        return redirect('index')
    context = {}
    return render(request, 'login.html',context)
```


## 3. Security measures
The Crypto Summariser aims to provide secured services to the customers. At the moment, we have implemented four security measures on our app to make sure to put customers at ease.
#### Application serving over https

Our application supports connection through HTTPS protocol with our certificate stored securely on the server.
```
#!/usr/bin/env bash

export FLASK_APP=app_auth
export FLASK_DEBUG=1
python -m flask run --cert=cert.pem --key=key.pem

````

#### User accounts and access management with hash-based authentication

We use sha256 encryption, provided by default with django built-in authentication system.

![image](https://user-images.githubusercontent.com/53450442/207747779-b286cb57-a96d-4d4e-afa4-e38b7175d6dd.png)


#### Securing the database with role-based policies

![image](https://user-images.githubusercontent.com/53450442/207748840-de56efe1-2f9b-43da-91fb-cb1413b696ff.png)

