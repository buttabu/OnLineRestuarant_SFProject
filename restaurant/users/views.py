from django.shortcuts import render,redirect , HttpResponse
from django.contrib.auth import logout,authenticate, login
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from menu.models import Food
from .forms import *
from .models import *


@csrf_exempt
def register(request, src=None):

    if request.method == 'GET':
        if src == 'staff':
            user_form= UserForm()
            userProfile_form = StaffForm()
        else:
            user_form = UserForm()
            userProfile_form = CustomerForm()

        return render(request, 'menu/register.html',
         {'uform': user_form, 'pform': userProfile_form})

    elif request.method == 'POST':
        if src == 'staff':
            user_form = UserForm(request.POST or None)
            userProfile_form = StaffForm(request.POST or None)
        else:
            user_form = UserForm (request.POST or None)
            userProfile_form = CustomerForm(request.POST or None)


        if (user_form.is_valid() and userProfile_form.is_valid()
         and user_form.cleaned_data['password'] ==
          user_form.cleaned_data['confirm_password']):
            user = user_form.save()
            user.set_password(user.password)
            profile = userProfile_form.save(commit=False)
            profile.user = user
            profile.is_approved = 0
            profile.user.save()
            profile.save()

        elif user_form.data['password'] != user_form.data['confirm_password']:
            user_form.add_error('confirm_password', 'Password did not match')
        else:
            print (user_form.errors, userProfile_form.errors)

        return render (request, 'menu/success.html')

@csrf_exempt
def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username = username, password=password)
        if user == None:
            return HttpResponse("Invalid Login Information")
        if user.is_active:
            try:
                if user.staff.is_approved:
                    login(request, user)
                    return redirect('/')
                else:
                    if user.staff.fired == True:
                        return HttpResponse ("You've been fired")
                    return HttpResponse ("Inactive Account")
            except:
                try:
                    if user.customer.is_approved:
                        login(request, user)
                        return redirect('/')
                    else:
                        if user.customer.deregistered == True:
                            return HttpResponse ("You've been deregistered ")
                        return HttpResponse ("Inactive Account")
                except:
                    login(request, user)
                    return redirect('/')

    elif request.user.is_authenticated():
        return redirect ('/')
    else:
        return render (request,'menu/loginPage.html')

def signout(request):
    logout(request)
    return redirect('/')
