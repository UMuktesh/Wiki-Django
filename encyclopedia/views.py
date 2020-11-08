from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from .forms import UserForm, markdown
from .models import log, creation
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import datetime
import re
from . import util
import markdown2
import random

def register(request):
    if request.method == "GET":
        return render(request, "encyclopedia/register.html", {
            "form": UserForm()
        })
    else:
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            login(request, user)
            messages.success(request, f"You are now registered and logged in as {username}")
            return redirect('/')
        messages.error(request, "Invalid credentials.")
        return

def login_view(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect(reverse("index"))
        return render(request, "encyclopedia/login.html", {
            "form": AuthenticationForm()
        })
    else:
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"You are now logged in as {username}")
                next_url = request.POST['next']
                if not next_url:
                    next_url = '/'
                return redirect(next_url)
        messages.error(request, "Invalid username or password.")
        return

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, f"You are now logged out")
    return redirect("/login")

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "heading": "All Pages"
    })

@login_required
def user(request):
    return render(request, "encyclopedia/user.html", {
        "user": request.user.username,
        "first": request.user.first_name,
        "last": request.user.last_name,
        "email": request.user.email,
        "contribc": creation.objects.filter(username=request.user.username),
        "contribe": log.objects.filter(username=request.user.username)
    })

def wiki(request, title):
    c = util.get_entry(title)
    if c is None:
        title = "404 " + title
        c = '''
# 404 Page Not Found

The requested page is not found    
        '''
    else:
        t = c.splitlines()[0][2:]
        if not t == title:
            return HttpResponseRedirect(reverse('wiki', args=[t])) 
    return render(request, "encyclopedia/wiki.html", {
        "title": title,
        "markdown": markdown2.markdown(c),
        "created": creation.objects.get(wikiname=title)
    })

def logger(request, title):
    logs = log.objects.filter(wikiname=title).all()
    return render(request, "encyclopedia/log.html", {
        "title": title,
        "logs": logs.reverse()
    })

def search(request):
    if request.method == "POST":
        q = request.POST["q"]
        c = util.get_entry(q)
        if c is not None:
            return HttpResponseRedirect(reverse('wiki', args=[q]))
        else:
            wikis = util.list_entries()
            wikis = [wiki for wiki in wikis if q.lower() in wiki.lower()]
            return render(request, "encyclopedia/index.html", {
                "entries": wikis,
                "heading": f"Search results for {q}",
                "search":"Search"
            })
    else:
        return redirect("/")

def rand(request):
    entry = random.choice(util.list_entries())
    return HttpResponseRedirect(reverse('wiki', args=[entry]))

@login_required
def create(request):
    if request.method == "GET":
        return render(request, "encyclopedia/create.html", {
            "form": markdown()
        })
    if request.method == "POST":
        form = markdown(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            wikis = util.list_entries()
            if title.lower() in [wiki.lower() for wiki in wikis]:
                title = "Error " + title
                c = '''
# Page already exists

A page with the title already exists.    
                '''
                return render(request, "encyclopedia/wiki.html", {
                    "title": title,
                    "markdown": markdown2.markdown(c)
                })
            content = form.cleaned_data["content"]
            content = "# " + title + "\n\n" + content
            content = content.splitlines()
            content = "\n".join(content)
            util.save_entry(title, content)
            create = creation(wikiname=title, username=request.user.username, creation=datetime.datetime.now())
            create.save()
            insertLog = log(username=request.user.username, wikiname=title, time=datetime.datetime.now())
            insertLog.save()
        return HttpResponseRedirect(reverse('wiki', args=[title]))

@login_required
def edit(request, title):
    if request.method == "GET":
        content = util.get_entry(title)
        if content is None:
            title = "404 " + title
            c = '''
# 404 Page Not Found

The requested page is not found    
            '''
            return render(request, "encyclopedia/wiki.html", {
                "title": title,
                "markdown": markdown2.markdown(c)
            })
        else:
            t = content.splitlines()[0][2:]
            if not t == title:
                return HttpResponseRedirect(reverse('edit', args=[t]))
            content = content.splitlines()[2:]
            content = "\n".join(content)
            content.replace("\r\n", "\n").replace("\r", "\n")
            content.rstrip()
            return render(request, "encyclopedia/edit.html", {
                "value": content,
                "title": t
            })
    elif request.method == "POST":
        content = request.POST["content"]
        content = "# " + title + "\n\n" + content
        content = content.splitlines()
        content = "\n".join(content)
        util.save_entry(title, content)
        insertLog = log(username=request.user.username, wikiname=title, time=datetime.datetime.now())
        insertLog.save()
        return HttpResponseRedirect(reverse('wiki', args=[title]))