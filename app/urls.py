from django.urls import path,re_path
from .views import sign_up
from .views import log_in
from .views import log_out
from .views import update_account
from .views import input_form
from .views import start_script, stop_script,get_alert_status
from .views import (
    base_2_view,
    webhook_callback,
    home_page,
    base_view,
    reset_password,
    success_page,
    pricing_page,
    sigup_sucess_page,
    activate_account,
    resend_activation_mail,
    password_reset_request,
    password_reset_confirm,
    sign_up,
    log_in,
    input_form,
    log_out,
    update_account,
    main_sub,
    display_html,
    page_404,
    cancel_subscription,
)
urlpatterns = [
    path('signup', sign_up, name='signup'),
    path('login', log_in, name='login'),
    path('alert', input_form, name='alert'),
    path('base', base_view, name='base'),
    path('', home_page, name='home'),
    path('base2', base_2_view, name='base2'),
    path('reset_password', reset_password, name='reset_password'),
    path('success', success_page, name='success'),
    path('pricing', pricing_page, name='pricing'),
    path('logout', log_out, name='logout'),
    path('update_account', update_account, name='update_account'),
    path('signup_successful', sigup_sucess_page, name='signup_successful'),
    path('activate/<uidb64>/<token>/', activate_account, name='activate'),
    path('resend_activation', resend_activation_mail, name='resend_activation_mail'),
    path('password-reset/', password_reset_request, name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),
    path('webhook/', webhook_callback, name='webhook_callback'),
    path('sub_success/', main_sub, name='main_sub'),
    path('dashboard/', display_html, name='dashboard'),
    path('404/', page_404, name='404'),
    path('cancel-subscription/', cancel_subscription, name='cancel-subscription'),
    path('start/', start_script, name='start_script'),
    path('stop/', stop_script, name='stop_script'),
    path('get_alert_status/', get_alert_status, name='get_alert_status')
]

    

    

