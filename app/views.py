from rest_framework.decorators import api_view, permission_classes
from django_countries import countries
import time
from threading import Event
import threading
import requests
import signal
from .models import RssDetails,CancelledSubscription,FreeTrialUser,SubscriptionPayment
from django.shortcuts import render, redirect, HttpResponse
from django.utils.encoding import force_str
from django.core.exceptions import MultipleObjectsReturned,ObjectDoesNotExist
from django.http import HttpRequest
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from main.reset_password import send_reset_password_mail
from django.contrib.auth.models import User
from main.send_activation_mail import send_activation_mail
from django.shortcuts import render, redirect
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from .forms import UserInputForm, UserLoginForm, UserSignupForm
from .forms import UpdateAccountForm, ResetAccountForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from datetime import datetime, timedelta
from django.utils import timezone
from threading import Thread, Event
from main.main import job
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import hashlib
import hmac
import subprocess
from django.http import JsonResponse
from .models import RssDetails  
import psutil
from .process_manager import ProcessManager

terminate_signal = Event()
job_thread = None
SECRET_KEY = "Iamapythondeveloper4real22"
LS_API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI5NGQ1OWNlZi1kYmI4LTRlYTUtYjE3OC1kMjU0MGZjZDY5MTkiLCJqdGkiOiI5NWQ1MmUwNmY0OGJiMGFhYmFmZjVkYmQyOWI1YTA1YmE5NmVmZmQyNWMwZWRlZjBhMTE0N2NkZThmODA5MWFiZmYxNDMwYmVhNWJjNmU0YyIsImlhdCI6MTcxNzgzODAwMi4zMjAwMzcsIm5iZiI6MTcxNzgzODAwMi4zMjAwNCwiZXhwIjoyMDMzMzcwODAyLjI4ODAxMSwic3ViIjoiMjE5NzkwNSIsInNjb3BlcyI6W119.eUSkfaA38hC8eqdT3_4ACCaflF8hoIij1MJSo-1UpOv9Q0bcsntSGvMNkdkWczZjlMvHCHMVGbT0eQHYi0ZKAXaIlHIeGyUdPScz1vQkDxvlPIZ25z3VoMQ0KJhiiwvNQQUqjG0zq9djebFGBXfZ5m8CZQ3xjSJgM2QYjuoBwyqL4XwdC6au_Eps_M1Y5mvss2zbxqIBTzHr2gGZFEGTHHnvVsH5G4MGE4hQEts3JO_zClqPlPQLg09Ytnk6EcQKyoSf1rEjvyw5CM7EDoLme4iL3OZ67zPeIHN7WHYGnJ6QkER4FEwYch3TCSNFZcXxf5hLJ-jPUTe14e0cln6fVy33ef8RU4TQP6JM7-UVoH2TJgd0THRmPIVUvZqXiDyNhd4CVVGkGTCiSlpmxph6tBzaZIR9FWhMDLlJ_9PW8TfX2muHR223x2nehP5Ujojk8ziKRPCj90-dNyGOgaqTwxmz4yufG5ansv5c1LSisrj9O7X9vwL_F7pkhpmtpmj-"
# Form for alert
@login_required
def input_form(request):
    if request.method == 'POST':
        form = UserInputForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            rss_url = form.cleaned_data['rss_url']
            user = request.user
            RssDetails.objects.create(user=user, email=email, rss_url=rss_url)
            print('RSSS DATA SAVED')
            subscribed_user = SubscriptionPayment.objects.filter(user_name=user).first()
            if subscribed_user:
                return redirect('main_sub')
            else:
                # Create FreeTrialUser object if the user doesn't have a subscription
                FreeTrialUser.objects.create(user=user)
                return redirect('success')
    else:
        return HttpResponseForbidden("Access Denied: Access to this page is not allowed.")
    return render(request, 'alert.html', {'form': form})

# To run script
def run_job(email, rss_url):
    global terminate_signal
    while not terminate_signal.is_set():
        job(email, rss_url)
        time.sleep(2)
        

def terminate_process(user):
    if user.username in ProcessManager.processes and ProcessManager.processes[user.username].poll() is None:
        print(f"Terminating process for user: {user.username}, PID: {ProcessManager.processes[user.username].pid}")
        try:
            ProcessManager.processes[user.username].send_signal(signal.SIGTERM)
            ProcessManager.processes[user.username].wait()
            del ProcessManager.processes[user.username]
            print(f"Process terminated successfully for user: {user.username}")
            return True
        except subprocess.TimeoutExpired:
            print(f"Process timed out for user: {user.username}, force killing...")
            ProcessManager.processes[user.username].kill()
            del ProcessManager.processes[user.username]
            return False
    else:
        return False


def check_subscription_and_terminate():
    # Get all users
    users = User.objects.all()
    
    for user in users:
        # Check if the user has a subscription
        subscribed_user = SubscriptionPayment.objects.filter(user_name=user).first()
        
        # Check if the user is on a free trial
        trial_user = FreeTrialUser.objects.filter(user=user).first()
        
        # Check if the user's subscription has expired
        if trial_user and trial_user.start_date + timedelta(days=7) <= timezone.now():
            terminate_process_success = terminate_process(user)
            if terminate_process_success:
                print(f"Process terminated successfully for user: {user.username}")
        
        # Check if the user's monthly subscription has expired
        if subscribed_user and subscribed_user.total_formatted == '$5.00' and subscribed_user.created_at + timedelta(days=29) <= timezone.now():
            terminate_process_success = terminate_process(user)
            if terminate_process_success:
                print(f"Process terminated successfully for user: {user.username}")
        
        # Check if the user's yearly subscription has expired
        if subscribed_user and subscribed_user.total_formatted == '$48.00' and subscribed_user.created_at + timedelta(days=364) <= timezone.now():
            terminate_process_success = terminate_process(user)
            if terminate_process_success:
                print(f"Process terminated successfully for user: {user.username}")


def periodic_subscription_check():
    while True:
        check_subscription_and_terminate()
        time.sleep(300)  # Wait for 1 minute before checking again

# Start the background thread when the Django server starts up
thread = threading.Thread(target=periodic_subscription_check)
thread.start()


        
# pricing
@login_required
def pricing_page(request):
    user = request.user
    month_sub_on = False
    year_sub_on = False
    sub_message = None
    year_sub_message = None
    trial_user = FreeTrialUser.objects.filter(user=user).first()
    if trial_user:
        if trial_user.start_date + timedelta(days=7) <= timezone.now():
            trial_message = 'Your free trial has expired. Please subscribe to continue.'
            terminate_process_success = terminate_process(user)
            if terminate_process_success:
                print(f"Process terminated successfully for user: {user.username}")
            else:
                print(f"Failed to terminate process for user: {user.username}")
        else:
            trial_message = 'Your free trial is already active. Please go back to <a href="dashboard">dashboard</a> to see your stats.'
    else:
        trial_message = None

    # Check if the user already has a subscription
    subscribed_user = SubscriptionPayment.objects.filter(user_name=user).first()
    if subscribed_user:
        if subscribed_user.total_formatted == '$5.00':
            if subscribed_user.created_at + timedelta(days=29) <= timezone.now():
                sub_message = 'Your monthly subscription has expired. Please wait for your subscription to autorenew to continue or click the button below to re-subscribe.'
                terminate_process(user)
            else:
                month_sub_on = True
        elif subscribed_user.total_formatted == '$48.00':
            if subscribed_user.created_at + timedelta(days=364) <= timezone.now():
                year_sub_message = 'Your annual subscription has expired. Please wait for your subscription to autorenew to continue or click the button below to re-subscribe.'
                terminate_process(user)
            else:
                year_sub_on = True

    if request.method == 'POST':
        if 'plan' in request.POST:
            plan = request.POST['plan']
            if plan == 'free':
                return redirect('alert')
            elif plan == 'monthly':
                user_name = request.user.username
                variant_id = '47d5f5f4-eb8d-4872-b460-9800e8c29df8'
                checkout_url = f'https://uptrackr.lemonsqueezy.com/checkout/buy/{variant_id}?checkout[custom][user_name]={user_name}'
                return redirect(checkout_url)
            elif plan == 'annual':
                user_name = request.user.username
                variant_id = 'a0a4ae4e-aabf-4cb2-b1f5-b1324ebab37b'  # Adjust this to your actual variant ID
                checkout_url = f'https://uptrackr.lemonsqueezy.com/checkout/buy/{variant_id}?checkout[custom][user_name]={user_name}'
                return redirect(checkout_url)

    return render(request, 'pricing.html', {'trial_message': trial_message, 'month_sub_on': month_sub_on, 'year_sub_on': year_sub_on, 'sub_message': sub_message, 'year_sub_message': year_sub_message})

processes = {}

import logging

logger = logging.getLogger(__name__)


from .process_manager import ProcessManager

def start_script(request):
    user = request.user
    rss_user = RssDetails.objects.filter(user=user).first()
    if rss_user:
        pid = ProcessManager.start_process(user, rss_user)
        time.sleep(5)
        if pid is not None:
            return JsonResponse({'message': 'Alert started', 'pid': pid})
        else:
            return JsonResponse({'message': 'Alert is already running'})
    else:
        return JsonResponse({'error': 'RSS details not found for user'}, status=404)

def stop_script(request):
    user = request.user
    if ProcessManager.stop_process(user):
        time.sleep(5)
        return JsonResponse({'message': 'Alert stopped'})
    else:
        return JsonResponse({'error': 'No script is running for this user'}, status=404)











    
# Webhook to get data from lemon squeezy
external_list = []
sub_ids = []
@csrf_exempt
def webhook_callback(request):
    
    if request.method == 'POST':
        # Get the signature from the request headers
        signature = request.headers.get('X-Signature')

        # Calculate the digest using HMAC-SHA256
        digest = hmac.new(SECRET_KEY.encode(), request.body, hashlib.sha256).hexdigest()
        
        # Compare the calculated digest with the received signature
        if hmac.compare_digest(digest, signature):
            print('Compare was correct')
            payload = json.loads(request.body)
            print('PAY LOADDDD ISSSS')
            print(payload)
            # If the signatures match, process the webhook payload
            
            try:
                # Parse the JSON payload
                payload = json.loads(request.body)
                print(f'payload....:::::::::::{payload}')
                meta_data = payload['meta']
                event_name = payload['meta']['event_name']
                external_list.append(meta_data)
                subscription_id = None
                for data in external_list:
                    if 'event_name' in data and data['event_name'] == 'subscription_created':
                        subscription_id = payload['data']['id']
                        sub_ids.append(subscription_id)
                        print('sub id', subscription_id)
                        break
                    
                if event_name == 'subscription_payment_success':
                    custom_data = payload['meta']['custom_data']
                    user_name = custom_data['user_name']
                    subscription_id = payload['data']['attributes']['subscription_id']
                    sub_ids.append(subscription_id)
                    print('SUB IDS....',sub_ids)
                    created_at_str = payload['data']['attributes']['created_at']
                    created_at = datetime.strptime(created_at_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                    total_formatted = payload['data']['attributes']['total_formatted']
                    status = payload['data']['attributes']['status']
                    
                    # Calculate expiration date based on total amount
                    if total_formatted == '$5.00':
                        expiration_date = created_at + timedelta(days=29)
                    elif total_formatted == '$48.00':
                        expiration_date = created_at + timedelta(days=364)
                    else:
                        expiration_date = None

                    # Save data to database
              
                    subscription_payment, created = SubscriptionPayment.objects.get_or_create(
                        user_name=user_name,
                        defaults={
                            'subscription_id':subscription_id,
                            'event_name': event_name,
                            'created_at': created_at,
                            'total_formatted': total_formatted,
                            'status': status,
                            'expiration_date': expiration_date
                        }
                            )

                            # If the object already existed, update its fields with the new data
                    if not created:
                        subscription_payment.subscription_id = subscription_id
                        subscription_payment.event_name = event_name
                        subscription_payment.created_at = created_at
                        subscription_payment.total_formatted = total_formatted
                        subscription_payment.status = status
                        subscription_payment.expiration_date = expiration_date
                        subscription_payment.save()
                        
                    print('Data Saved')
                elif event_name == 'subscription_cancelled':
                    # Handle the cancellation event
                    user_name = payload['meta']['custom_data']['user_name']  # Adjust based on actual payload structure
                    print(f'Subscription cancelled for {user_name}')

                # Construct the JSON response
                response_data = {
                    'status': 'success',
                    'message': 'Webhook processed successfully',
                    'payload': payload  # Include the payload in the response if needed
                }
                
                # Return the JSON response
                return JsonResponse(response_data, status=200)

            except json.JSONDecodeError:
                # If the payload is not valid JSON, respond with a bad request status code
                print('400 ERROR........')
                return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
        else:
            # If the signatures don't match, respond with an unauthorized status code
            print('401 ERROR........')
            return JsonResponse({'error': 'Invalid signature'}, status=401)
    else:
        # If the request method is not POST, respond with a method not allowed status code
        print('405 ERROR........')
        return JsonResponse({'error': 'Method not allowed'}, status=405)



@csrf_exempt
def cancel_subscription(request):
    if request.method == 'POST':
        user = request.user  # Make sure this adjusts based on your user authentication setup
        terminate_process(user)
        subscribed_user = SubscriptionPayment.objects.filter(user_name=user).first()
        if subscribed_user:
            print('SUB_ID is ,', subscribed_user.subscription_id)
            # Call the API to cancel the subscription
            url = f"https://api.lemonsqueezy.com/v1/subscriptions/{subscribed_user.subscription_id}"
            headers = {'Authorization': f'Bearer {LS_API_KEY}'}
            response = requests.delete(url, headers=headers)
            if response.status_code == 200:  # Assuming 204 means deletion was successful
                # Move the subscription to CancelledSubscription
                cancelled_subscription = CancelledSubscription(
                    subscription_id=subscribed_user.subscription_id,
                    user_name=subscribed_user.user_name,
                    event_name=subscribed_user.event_name,
                    created_at=subscribed_user.created_at,
                    total_formatted=subscribed_user.total_formatted,
                    status='cancelled',
                    expiration_date=subscribed_user.expiration_date)

                cancelled_subscription.save()
                # Delete from SubscriptionPayment
                subscribed_user.delete()

                return JsonResponse({'status': 'success', 'message': 'Subscription cancelled successfully'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Failed to cancel subscription'}, status=500)
        else:
            return JsonResponse({'status': 'error', 'message': 'No subscription found'}, status=404)

    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)



# Sign Up
allowed_domains = [
    'gmail.com',
    'outlook.com',
    'hotmail.com',
    'yahoo.com',
    'aol.com',
    'icloud.com',
    'protonmail.com',
    'zoho.com',
    'yandex.com',
    'gmx.com',
    'mail.com',
    'live.com',
    'tutanota.com',
    'protonmail.ch',
    'fastmail.com',
    'hey.com',
    'pm.me',
    'mailfence.com',
    'mailinator.com',
    'guerrillamail.com',
    'mailinator.net',
    'mailsac.com',
    'guerrillamailblock.com',
    'pokemail.net',
    'guerrillamail.org',
    'guerrillamail.net',
    'guerrillamail.de',
    'guerrillamail.biz',
    'guerrillamail.com',
    'guerrillamail.info',
    'guerrillamailblock.com'
]


def sign_up(request):
    countries_list = countries
    error_message = None
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            full_name = form.cleaned_data['full_name']
            password = form.cleaned_data['password']
            
            email_domain = email.split('@')[-1]
            print(email_domain)
            if email_domain not in allowed_domains:
                error_message = "Email domain is not allowed. Please use an email from a recognized domain."
                return render(request, 'signup.html', {'message': error_message, 'form': form, 'countries': countries_list})

            
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                error_message = "Email address is already in use. Please use a different email address."
                return render(request, 'signup.html', {'message': error_message, 'form': form, 'countries': countries_list})

            try:
                user = User.objects.create_user(username=username, email=email, password=password, is_active=False)
                user.first_name = full_name
                user.save()
            except IntegrityError:
                error_message = "Username already exists. Please choose a different username."
                return render(request, 'signup.html', {'message': error_message})            
            # Generate token for email verification
            username = user.username
            token = default_token_generator.make_token(user) 
            current_domain = HttpRequest.get_host(request)
            activation_link = f'{request.scheme}://{current_domain}{reverse("activate", kwargs={"uidb64": urlsafe_base64_encode(force_bytes(user.pk)), "token": token})}'
            send_activation_mail(email, username, activation_link)
            # Redirect to a page indicating successful signup
            return render(request, 'signup_success.html')
    else:
        form = UserSignupForm()
    return render(request, 'signup.html', {'countries': countries_list, 'form': form})


# Resend Activation mail
def resend_activation_mail(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Handle the case where the user with the provided email doesn't exist
            error_message = 'User with this email address does not exist.'
            return render(request, 'resend_activation_mail.html', {'error_message': error_message})
        except MultipleObjectsReturned:
            error_message = 'Multiple users found with this email address. Please contact support.'
            return render(request, 'resend_activation_mail.html', {'error_message': error_message})
        # Generate token for email verification
        username = user.username
        token = default_token_generator.make_token(user)
        current_domain = request.get_host()
        activation_link = f'{request.scheme}://{current_domain}{reverse("activate", kwargs={"uidb64": urlsafe_base64_encode(force_bytes(user.pk)), "token": token})}'
        # Send activation email
        send_activation_mail(email, username,activation_link)
        # Display success message
        message = """Activation email has been sent successfully
                        """
        return render(request, 'resend_activation_mail.html',{'message':message})
    else:
        return render(request, 'resend_activation_mail.html')

# Activate Account      
def activate_account(request, uidb64, token):
    form = UserLoginForm()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        # Activate user account
        user.is_active = True
        user.save()
        return render(request, 'activation_successful.html')
    else:
        return render(request, 'login.html', {'message': "Unable to actiavte your account <a href='/resend_activation'>Click here to resend activation link</a>", 'form': form})


#User Login
def log_in(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = User.objects.get(username=username)
            # Check password validity here and handle login accordingly
        except ObjectDoesNotExist:
            error_message = "User does not exist. Please register or check your credentials."
            return render(request, 'login.html', {'message': error_message})
        user = authenticate(request, username=username, password=password)
        user_check  =  User.objects.get(username=username)
        if user is not None:
            if user.is_active:
                login(request, user)
                # Redirect to the home page
                return redirect('home')
        elif user is None and not user_check.is_active:
                # Account is not activated
                message = "Account not activated. <a href='/resend_activation'>Click here to resend activation link</a>"
                return render(request, 'login.html', {'message': message})
        elif user is None and user_check.is_active:
            # Invalid login credentials
            message = """Invalid login credentials. \n
                        """
            return render(request, 'login.html', {'message': message})
        elif user is None and user_check is None:
            comment = get_object_or_404(username=username)
            messages.error(request, 'User does not exist.')
          
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})


#Logout
def log_out(request):
    logout(request)
    return redirect('login')



# Update Account
@login_required
def update_account(request):
    if request.method == 'POST':
        form = UpdateAccountForm(request.POST)

        if form.is_valid():
            # Update user information
            request.user.username = form.cleaned_data.get('username', request.user.username)
            request.user.email = form.cleaned_data.get('email', request.user.email)
            request.user.full_name = form.cleaned_data.get('full_name')
            request.user.country = form.cleaned_data.get('country')
            # Update password only if it's provided in the form
            new_password = form.cleaned_data.get('password')
            if new_password:
                request.user.set_password(new_password)
            request.user.save()
            # Update the session with the new user details
            update_session_auth_hash(request, request.user)

            messages.success(request, 'Your account has been updated successfully!')
            logout(request)  # Logout the user after updating
            return redirect('login')  # Redirect to the login page after update
    else:
        form = UpdateAccountForm()
    return render(request, 'update_account.html', {'form': form})


# Send Password Reset Link to mail
def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Handle the case where the user with the provided email doesn't exist
            return render(request, 'reset_password.html', {'error_message': 'User with this email address does not exist.'})
        except MultipleObjectsReturned:
            error_message = 'Multiple users found with this email address. Please contact support.'
            return render(request, 'resend_activation_mail.html', {'error_message': error_message})
        
        # Generate password reset token
        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))  # Encode the user's primary key
        reset_url = request.build_absolute_uri(reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token}))
        username = user.username
        # Send password reset email
        send_reset_password_mail(email, username, reset_url)
        # Redirect to a page indicating that the password reset email has been sent
        return render(request, 'reset_password.html',{'message':'We have sent a reset link to your email. Please click on the link to reset your password.'})
    else:
        return render(request, 'reset_password.html')


# Confirm Reset Password fro mail
def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        user = None
    except Exception as e:
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password = request.POST.get('password')
            user.set_password(password)
            user.save()
            message = 'Your password has been successfully reset. You can now login with your new password'
            return render(request, 'password_reset_confirm.html', {'message': message})
        else:
            # If request method is not POST, render the form without the message
            return render(request, 'password_reset_confirm.html')
    else:
        # Handle invalid or expired token
        messages.error(request, 'Invalid or expired password reset link.')
        return redirect('password_reset')    
    



#-----------------------------Rendering 1 page  ----------------------------------------------------------------------#
@login_required
def base_view(request):
    return render(request, 'base.html')


@login_required
def display_html(request):
    sub_status = None
    sub_end_date = None
    expiration_date_passed = None
    alert_status = 'OFF'  # Set the default alert status to 'OFF'
    user = request.user

    # Check if a process is running for the user
    if user.username in ProcessManager.processes and ProcessManager.processes[user.username].poll() is None:
        alert_status = 'ON'

    subscribed_user = SubscriptionPayment.objects.filter(user_name=user).first()
    cancelled_user = CancelledSubscription.objects.filter(user_name=user).first()
    trial_user = FreeTrialUser.objects.filter(user=user).first()

    if subscribed_user:
        if subscribed_user.total_formatted == '$5.00' and subscribed_user.expiration_date <= timezone.now():
            ProcessManager.stop_process(user)
            sub_status = 'OFF'
            sub_end_date = subscribed_user.expiration_date
        elif subscribed_user.total_formatted == '$48.00' and subscribed_user.expiration_date <= timezone.now():
            ProcessManager.stop_process(user)
            sub_status = 'OFF'
            sub_end_date = subscribed_user.expiration_date
        else:
            sub_status = 'ON'
            sub_end_date = subscribed_user.expiration_date
    elif cancelled_user:
        if cancelled_user.expiration_date <= timezone.now():
            sub_status = 'Cancelled and Expired'
            expiration_date_passed = True
            cancelled_user.delete()
        else:
            sub_status = 'Cancelled Not Expired'
            expiration_date_passed = False
    elif trial_user:
        if trial_user.start_date + timedelta(days=7) <= timezone.now():
            ProcessManager.stop_process(user)
            print('Script has been stopped')
            sub_status = 'Free Trial Expired'
        else:
            sub_status = 'Your free trial is already active.'
    else:
        sub_status = 'User Not Subscribed'
        sub_end_date = 'None'

    context = {
        'username': user.username,
        'email': user.email,
        'joining_date': user.date_joined,
        'subscription_status': sub_status,
        'subscription_expiration_date': sub_end_date,
        'expiration_date': expiration_date_passed,
        'button_label': 'Start Alert',
        'alert_status': alert_status
    }
    return render(request, 'dashboard.html', context)


@login_required
def get_alert_status(request):
    print("get_alert_status called")
    user = request.user
    if user.username in ProcessManager.processes and ProcessManager.processes[user.username].poll() is None:
        alert_status = 'ON'
    else:
        alert_status = 'OFF'
    print(f"Returning alert_status: {alert_status}")
    return JsonResponse({'alert_status': alert_status})





def base_2_view(request):
    return render(request, 'base_html_2.html')

def main_sub(request):
    return render(request, 'main_sub.html')

def reset_password(request):
    return render(request, 'reset_password.html')

def home_page(request):
    return render(request, 'index.html')

def success_page(request):
    return render(request, 'success.html')

def sigup_sucess_page(request):
    return render(request, 'signup_success.html')

def page_404(request):
    return render(request, '404.html')












