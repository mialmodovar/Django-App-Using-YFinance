# Django-App-Using-YFinance
## Group 10 - Module ECS781P - Cloud Computing
### Miguel Almodovar, Venkatraman, Satyam Sharma, Shaurya Rana

## Funtionality

We have built an app with Django which dynamically hits the YFinance RestAPI and displays the stocks details, charts and summaries for the stock ticker entered in the search bar. As displayed in the screenshot below the the user can filter by stock ticker name and date range. The data is retrieved based on the follwoing two ways - 

1) Each search query hits the RestAPI and returns the results via html and then rendered as summary stats and boxplots on the webpage.  

<img width="946" alt="image" src="https://user-images.githubusercontent.com/85103905/207667383-0b918a9f-7201-4dca-87d6-345086380061.png">

2) The stocks historical price data is recived as a JSON file using an AJAX request.

<img width="957" alt="image" src="https://user-images.githubusercontent.com/85103905/207668800-3a359d69-50e3-4642-8ea9-54394630b825.png">



## Rest API
### 1- Create user operation
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
### 2-Reading user details and logging them in
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
### 3- Gets stock info from external api and returns it via html
```
@login_required(login_url= 'login')
def stock(request,pk):
    #gets object Ticker from the ticker given in the url and gets the info and last close for it.
    stock = yf.Ticker(pk)
    close = "{:.2f}".format(stock.history(period='1d').Close.values.tolist()[0])
    #sends the current day and day corresponding to a week ago to load the plot (could be done in js)
    today = datetime.date.today().strftime('%m-%d-%Y')
    week_ago = (datetime.date.today() - datetime.timedelta(days=21)).strftime('%m-%d-%Y')
    context = { 'ticker': pk,'today': today, 'week_ago': week_ago, 'stock':stock.info, 'close':close}
    return render(request,'stocks.html',context)
```
### 4- Gets stock history price from external api and returns it as json
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
