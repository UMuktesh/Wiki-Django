from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django import forms
import re
from . import util
import markdown2
import random
import re

class markdown(forms.Form):
    title = forms.CharField(label="Title", max_length=30)
    content = forms.CharField(widget=forms.Textarea, label="Content")

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "heading": "All Pages"
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
        "markdown": markdown2.markdown(c)
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
        return HttpResponseRedirect(reverse('wiki', args=[title]))

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
        return HttpResponseRedirect(reverse('wiki', args=[title]))