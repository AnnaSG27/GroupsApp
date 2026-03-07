from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.forms import AuthenticationForm

from .forms import RegisterForm


User = get_user_model()


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
    else:
        form = AuthenticationForm()

    # style and placeholders for login form fields
    for name, field in form.fields.items():
        attrs = field.widget.attrs
        attrs.update({
            "class": "form-control input-dark",
        })
        if name == "username":
            attrs["placeholder"] = "Tu usuario"
        elif name == "password":
            attrs["placeholder"] = "••••••••"

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect("dashboard")

    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})