from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Food, Review, Order, Message
from .forms import FoodForm, ReviewForm, MessageForm
from django.shortcuts import redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
import requests, googlemaps
from xml.etree import ElementTree
from datetime import datetime
from users.forms import AddressForm
from users.models import Customer, Staff



def getUserType(user):
    userType = 'VISITOR'
    if user.is_superuser:
        userType = 'MANAGER'
    try:
        if user.staff.user_type == 'CHEF':
            userType = 'CHEF'
        else:
            userType = 'DELIVERY'
    except:
        try:
            if user.customer.user_type == 'CUSTOMER':
                userType = 'CUSTOMER'
        except:
            pass
    return userType


def index(request):

    userType = getUserType(request.user)
    if userType == 'VISITOR':
        foods = Food.objects.all().order_by('-numOrdered')
        context =  {'foods': foods,'user':request.user}
        return render (request, 'menu/index.html', context=context )

    elif userType == 'CHEF':
        messages = Message.objects.filter(target=request.user)
        if request.method == 'GET':
            form = FoodForm()
            context = {'foodForm' : form,'user':request.user, 'messages':messages}

            return render (request, 'menu/chef.html', context=context)
        elif request.method == 'POST':
            form = FoodForm (request.POST or None, request.FILES or None)
            if form.is_valid():
                food = form.save(commit=False)
                food.chef = request.user
                food.save()
                context = {'content':food,'user':request.user, 'messages':messages}
                return redirect('/')
            else:
                return HttpResponse("<p>invalid form</p>")


    elif userType == 'CUSTOMER':
        customer = request.user
        orders = Order.objects.filter(customer=customer,
                    status__in=['pending', 'processed'])
        cuisines = {'American', 'Asian', 'Indian', 'Mexican','Italian'}
        pref = set()
        for order in orders:
            pref.add(order.food.cuisine)
        nonPref = cuisines - pref
        prefFoods = Food.objects.filter(cuisine__in=pref).order_by('numOrdered')
        nonPrefFood = Food.objects.filter(cuisine__in=nonPref).order_by('numOrdered')
        prefFoods |= nonPrefFood
        foods = prefFoods
        context =  {'foods': foods,'user':request.user}
        return render (request, 'menu/customer.html', context=context )

    elif userType == 'DELIVERY':
        messages = Message.objects.filter(target=request.user)
        orders = Order.objects.filter(status = 'pending')
        deliveries = Order.objects.filter(status='processed', delivery=request.user)
        context = { 'orders': orders,
                    'deliveries':deliveries,
                    'messages': messages
                    }
        return render (request, 'menu/delivery.html', context=context)




    elif userType == "MANAGER":
        requests = Customer.objects.filter(is_approved=False)
        jobApps = Staff.objects.filter(is_approved=False)

        customers = Customer.objects.all()
        staff = Staff.objects.all()
        messages = Message.objects.filter(status="unhandled", message_type__in=['Complaint'])
        balances = Message.objects.filter(status="unhandled", message_type='balance')
        context = {'requests':requests,
                    'jobApps':jobApps,
                    'messages':messages,
                    'balances': balances,
                    'customers':customers,
                    'staff':staff
                    }
        return render(request, 'menu/manager.html', context=context)


def food(request, cuisine=None, food=None):

    if request.method == 'POST':
        form = ReviewForm (request.POST or None)
        if form.is_valid():
            review = form.save(commit=False)
            customer = request.user
            foodInstance = Food.objects.get(name=food)
            review.customer= customer
            review.order = Order.objects.get(customer=customer,
                                                    food=foodInstance)
            review.save()
            review.execute()
            review.save()

            return redirect('menu:food', food=food, cuisine=cuisine)
        else:
            return render(request, 'menu/errors.html', {'form':form})

    form = ReviewForm()
    instance = Food.objects.get(name=food)
    is_ordered= False
    if request.user.is_authenticated:
        is_ordered = Order.objects.filter(customer=request.user,
                    food=instance).count() != 0
    orders = Order.objects.filter(food=instance)
    reviews = Review.objects.filter(order__in=orders)
    context =  {
                'food': instance,
                'reviews': reviews,
                'form' : form,
                'user':request.user,
                'isOrdered':is_ordered
                 }
    return render(request, 'menu/food.html', context=context)

def cuisine(request, cuisine=None):
    foods = Food.objects.filter(cuisine=cuisine)
    context = {
                'name': cuisine,
                'foods' : foods
            }
    return render(request, 'menu/cuisine.html', context)



def search(request):
    q = request.GET['q'].lower()
    results = Food.objects.filter(Q(description__icontains=q) |
     Q(name__icontains=q) | Q(cuisine__icontains=q) ).order_by('-avg_rating')
    context = {'foods':results, 'term': q}
    return render (request,'menu/searchResults.html', context)

def cart(request):
    customer = request.user
    if (request.method == 'POST'):
        form = request.POST
        if form['action'] == 'placeOrder':
            return placeOrder(request)

        elif form['action'] == 'addToCart':
            quantity = form['q']
            food = form['food']
            instance = Order()
            instance.food = Food.objects.get(name=food)
            instance.customer = customer
            instance.quantity = quantity
            instance.save()
            orders = Order.objects.filter(customer=customer)
            cartOrders = orders.filter(status='cart')
            numCart = cartOrders.count
            context = {'customer':customer, 'orders': cartOrders,'numCart':numCart,'broke': False}
            return render (request,'menu/cart.html',context=context)


    orders = Order.objects.filter(customer=customer, status='cart').order_by('time_stamp')
    numCart = orders.count()
    context = {'customer':customer, 'orders':orders,'broke': False,'numCart':numCart}
    return render(request,'menu/cart.html', context=context)

def placeOrder(request):
    # broke = False
    discount = 0.1
    customer = request.user.customer
    orders = Order.objects.filter(customer=request.user,
                status='cart')
    total_price = 0.0
    num_orders = 0
    for order in orders:
        for i in range (order.quantity):
            total_price += order.food.price
            num_orders += 1
            order.food.numOrdered +=1
            order.food.save()

    if customer.is_vip:
        total_price *= (1-discount)

    if (total_price > customer.balance):
        context = {'customer':request.user, 'orders':orders, 'broke': True}
        return render (request, 'menu/cart.html',context=context)
    customer.spending += total_price
    customer.numOrders += num_orders
    customer.balance -= total_price
    customer.save()
    customer.check_status()
    customer.save()
    for order in orders:
        order.status = 'pending'
        order.food.save()
        order.save()
    return HttpResponse ('Order placed')

def checkout(request):
    if request.method == 'POST':
        form = request.POST
        if form['action'] == 'confirm':
            form = AddressForm(request.POST or None)
            if not form.is_valid():
                return HttpResponse("invalid form")
            data = form.cleaned_data
            template =  "<AddressValidateRequest USERID=\"796CCNY00182\">\
                             <IncludeOptionalElements>true</IncludeOptionalElements>\
                             <ReturnCarrierRoute>true</ReturnCarrierRoute>\
                             <Address ID=\"0\">\
                                 <FirmName />\
                                 <Address1></Address1>\
                                 <Address2></Address2>\
                                 <City></City>\
                                 <State></State>\
                                 <Zip5></Zip5>\
                                 <Zip4></Zip4>\
                             </Address>\
                         </AddressValidateRequest> "

            xml = ElementTree.fromstring(template)
            xml[2][1].text = ''
            xml[2][2].text = data['street']
            xml[2][3].text = data['city']
            xml[2][4].text = data['state']
            xml[2][5].text = str (data['zipcode'])


            xml = ElementTree.tostring(xml)
            payload = {'API':'VERIFY', 'XML': xml}
            r = requests.get('http://production.shippingapis.com/ShippingAPI.dll', params=payload)
            tree = ElementTree.fromstring(r.content)
            # for i in tree[0]:
            #     print i.text

            address = ''
            for i in range (0,3):
                try:
                    address += tree[0][i].text +', '
                except:
                    pass
            try:
                address += tree[0][3].text
            except:
                pass
            customer = request.user.customer
            customer.address = address
            customer.save()

            return placeOrder(request)

        elif form['action'] == 'address':
            context = {'form':AddressForm}
            return render (request, 'menu/checkout.html', context=context)

def renderMap(request):
    if request.method == 'POST':
        delivery = request.user
        form = request.POST
        orderID = form['submit']
        order = Order.objects.get(id=orderID)
        order.status = 'processed'
        order.delivery = delivery
        order.save()
        customer = order.customer
        gmaps = googlemaps.Client(key='AIzaSyA2Ox7RLPRORwsCnOvu-i4aHMvvQiWXUB4')
        origin = "160 Convent Ave New York NY 10031"
        destination = customer.customer.address


        context = {'origin':origin, 'destination':destination}

        return render (request, 'menu/map.html', context=context)


def handleRequest(request,param=None):
    if len(param) == 0 :
        return redirect('/')
    action = param[0]
    userType = param[1]
    id = param[2:]
    if userType == 'c':
        user = Customer.objects.get(id=id)
    elif userType == 's':
        user = Staff.objects.get(id=id)

    elif userType == 'u' and action == 'b':
        userType = getUserType (request.user)

        if userType == "CUSTOMER":
            message = Message.objects.get(source=request.user,
                        message_type='balance')
            value = int (message.reason)
            message.status = "handled"
            message.save()
            request.user.customer.balance +=value
            request.user.customer.save()

        else:
            message = Message.objects.get(source=request.user,
                        message_type='balance')
            value = int (message.reason)
            message.status = "handled"
            message.save()
            request.user.staff.salary +=value
            request.user.staff.save()

    else:
        return redirect ('/')

    if action == 'p':
            user.approve()
            user.save()
    elif action == 'd':
        user.user.delete()

    return redirect ('/')


def profile(request, id=None):
    if request.method == 'POST':
        form = MessageForm(request.POST or None)
        if not form.is_valid():
            return HttpResponse("invalid form")
        data = form.cleaned_data
        feedback = data['feedback']
        service = data['service']
        content = data['content']
        order = Order.objects.get(id=id)
        delivery = order.delivery
        chef = order.food.chef
        customer =request.user
        message = Message()
        message.reason = content
        message.source = customer
        if (service == 'food'):
            message.target = chef
        elif (service == 'delivery'):
            message.target = delivery
        if feedback == 'Complaint':
            message.message_type = 'Complaint'
        elif feedback == 'Complement':
            message.message_type = 'Complement'
        message.save()
        return HttpResponse('Thanks for your feedback')

    else:
        customer = request.user
        deliveredOrders = customer.orders.filter(status='processed')
        pendingOrders = customer.orders.filter(status='pending')
        messages = Message.objects.filter(target=customer)
        context = {
                    'delivered':deliveredOrders,
                    'pending' : pendingOrders,
                    'form':MessageForm,
                    'messages':messages
                    }
        return render (request, 'menu/customerProfile.html', context=context)


def deliveryFeedback(request,param=None):
            if request.method == "POST":
                form = request.POST
                customer= Order.objects.get(id=param).customer
                message = Message()
                message.message_type = form['optradio']
                message.reason = form['content']
                message.source = request.user
                message.target = customer
                message.save()
                return HttpResponse("Thanks for feedback!")

def resolution(self, param):
    action = param[0]
    messageID= int(param[1:])
    message = Message.objects.get(id=messageID)
    message.message_type = 'Warning'
    message.status = 'Reviewed'
    sourceType = getUserType(message.source)
    destType = getUserType(message.target)

    if action == 'a':
        if sourceType == "CUSTOMER":
            if message.source.customer.is_vip:
                message.target.staff.rep -= 2
            else:
                message.target.staff.rep -= 1
            message.target.staff.save()
            message.target.staff.check_status()

        elif sourceType == "DELIVERY":
            message.target.customer.rep-=1
            message.target.customer.save()
            message.target.customer.check_status()

    elif action == 'd':
        if sourceType == "CUSTOMER":
            message.source.customer.rep -= 1
            message.source.customer.save()
            message.source.customer.check_status()

        elif sourceType == "DELIVERY":
            message.source.staff.rep-=1
            message.source.staff.save()
            message.source.staff.check_status()

        message.target, message.source = message.source, message.target

    message.save()
    return redirect('/')

def userAccounts (request, param=None):
    usertype = param[0]
    action = param [1:3]
    id = param [3:]
    if usertype == 's':
        staff = Staff.objects.get(id =id)
        if action == 'pp':
            staff.salary+=100
            staff.save()
        elif action == 'dd':
            staff.salary-=100
            staff.rep -= 3
            staff.save()
        elif action == 'ff':
            staff.user.delete()


    elif usertype == 'c':
        customer = Customer.objects.get(id =id)
        if action == 'nv':
            customer.is_vip = False
            customer.save()
        elif action == 'yv':
            customer.is_vip = True
            customer.save()
        elif action == 'dd':
            customer.user.delete()

    return redirect('/')
