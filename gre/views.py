from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import RegisterForm, WordForm
from .models import Word, Category
from collections import defaultdict
import requests
import json
import random
from bokeh.plotting import figure
from bokeh.embed import components
from math import pi
from bokeh.models import ColumnDataSource
from bokeh.transform import factor_cmap
import pandas as pd
from bokeh.palettes import Category20c
from bokeh.plotting import figure
from bokeh.transform import cumsum

TEST_DATA = {
    "categories":
        ["equality", "harmony", "aggressive", "calm", "impartial"],
    "words":
        [["Commensurate", "Corresponding in size or degree", "Enter Example Here", "equality"],
         ["Carity", "Generosity and helpfulness especially toward the needy or suffering",
             "Enter Example Here", "equality"],
         ["Accord", "Be harmonious or consistent with",
             "Enter Example Here", "harmony"],
         ["Conformity", "Behaviour in accordance with socially accepted conventions",
             "Enter Example Here", "harmony"],
         ["Bellicose", "Demonstrating aggression and willingness to fight",
             "Enter Example Here", "aggressive"],
         ["Fractious", "Difficult to control", "Enter Example Here", "aggressive"],
         ["Aplomb", "Self-confidence or assurance", "Enter Example Here", "calm"],
         ["Equanimity", "Calmness and composure", "Enter Example Here", "calm"],
         ["Egalitarian", "Person who supports the principle of equality",
             "Enter Example Here", "impartial"],
         ["Equitable", "Fair and impartial", "Enter Example Here", "impartial"]]

}


def index(request):
    return render(request, 'gre/main.html', {})


def register_user(request):

    page = 'register'
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()

            user.save()
            login(request, user)
            return redirect('main')
        else:
            messages.error(request, 'An error occured during registration.')

    context = {'page': page, 'form': form, 'messages': messages}
    return render(request, 'gre/signup.html', context)


def login_user(request):

    if request.user.is_authenticated:
        return redirect('main')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User Does Not Exist')
        else:
            user = authenticate(request, username=username, password=password)
            if user.id == 8:
                Word.objects.filter(learner=user.id).delete()
                Category.objects.filter(learner=user.id).delete()

                test_cat = TEST_DATA['categories']
                test_word = TEST_DATA['words']

                for cat in test_cat:
                    Category.objects.create(
                        category_name=cat,
                        learner=user
                    )

                for word in test_word:
                    cat = Category.objects.get(category_name=word[3])
                    Word.objects.create(
                        word_name=word[0],
                        meaning=word[1],
                        example=word[2],
                        learner=user,
                        category=cat
                    )

            if user is not None:
                login(request, user)
                return redirect('user-profile', pk=request.user.id)
            else:
                messages.error(
                    request, 'User does not exist or Password is incorrect')

    return render(request, 'gre/login.html', {})


def logout_user(request):
    logout(request)
    return redirect('main')


def show_error(request):
    return render(request, 'gre/error.html', context={})


@login_required(login_url='login')
def user_profile(request, pk):

    if request.user.id != int(pk):
        return redirect('error')

    if 'sortbycat' not in request.session:
        request.session["sortbycat"] = False

    words = Word.objects.filter(learner=pk).order_by('word_name')
    categories = Category.objects.filter(learner=pk).order_by('category_name')

    if request.POST or request.session["sortbycat"]:

        request.session["sortbycat"] = not request.session["sortbycat"]

    words_and_cats = defaultdict(list)

    for word in words:
        words_and_cats[word.category].append(word)

    if request.session["sortbycat"]:
        words = dict(words_and_cats)

    st = messages.get_messages(request)

    context = {'words': words, 'categories': categories,
               'messages': st, 'sortbycat': request.session["sortbycat"]}
    return render(request, 'gre/user_profile.html', context)


@login_required(login_url='login')
def add_word(request, pk):

    if request.user.id != int(pk):
        return redirect('error')

    form = WordForm()
    categories = Category.objects.all()
    # context = {'categories': categories}
    context = {}
    if request.method == 'POST' and 'searchword' in request.POST:
        word = request.POST.get('word_to_search')
        data = requests.get(
            f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')

        if data.status_code == 404:
            nodata = True

            word_data = {
                'word': None,
                'meaning': None,
                'example': None
            }
            enableTA = 'disabled'

        else:
            nodata = False
            enableTA = 'enabled'
            data = data.text
            data_json = json.loads(data)[0]
            word = data_json["word"]
            meaning = data_json["meanings"][0]["definitions"][0]["definition"]

            example_list = data_json["meanings"]
            example = "Enter your own example"
            for e in example_list:
                for i in e["definitions"]:
                    if "example" in i:
                        example = i["example"]
                        break

            word_data = {
                'word': word,
                'meaning': meaning,
                'example': example
            }

        context = {'word_data': word_data, 'enableTA': enableTA,
                   'form': form, 'nodata': nodata}

    elif request.method == 'POST' and 'saveword' in request.POST or 'anotherone' in request.POST:
        form = WordForm(request.POST)

        if form.is_valid():
            word_cat = request.POST.get('category') or None
            if word_cat:
                word_cat = Category.objects.get(id=word_cat)
            Word.objects.create(
                word_name=request.POST.get('word_name'),
                meaning=request.POST.get('meaning'),
                example=request.POST.get('example'),
                learner=request.user,
                category=word_cat,

            )

            if 'anotherone' in request.POST:
                return redirect('add-word', pk=request.user.id)
            else:
                return redirect('user-profile', pk=request.user.id)

        else:
            return render(request, 'gre/add_word.html', {'form': form, 'enableTA': 'disabled'})
    else:

        form = WordForm()
        context = {'form': form, 'enableTA': 'disabled'}
    context["categories"] = categories
    return render(request, 'gre/add_word.html', context)


@login_required(login_url='login')
def add_category(request, pk):

    if request.user.id != int(pk):
        return redirect('error')

    categories = Category.objects.all()

    if request.method == "POST":
        category = request.POST.get('category_name')
        category = category.lower()
        Category.objects.create(
            category_name=category,
            learner=request.user
        )

        if 'savecategory' in request.POST:
            return redirect('user-profile', pk=pk)
        else:
            return redirect('add-category', pk=pk)

    context = {'categories': categories}
    return render(request, 'gre/add_category.html', context)


@login_required(login_url='login')
def word_details(request, word_id, pk):

    if request.user.id != int(pk):
        return redirect('error')

    categories = Category.objects.all()

    words = Word.objects.filter(learner=pk).order_by('word_name')
    word_data = Word.objects.get(id=word_id)

    if request.method == 'POST':
        request.session["sortbycat"] = not request.session["sortbycat"]

    words_and_cats = defaultdict(list)

    for word in words:
        words_and_cats[word.category].append(word)

    if request.session["sortbycat"]:
        words = dict(words_and_cats)

    context = {'word_data': word_data, 'words': words,
               'categories': categories, 'sortbycat': request.session["sortbycat"]}

    return render(request, 'gre/word_details.html', context)


@login_required(login_url='login')
def delete_word(request, pk, word_id):

    if request.user.id != int(pk):
        return redirect('error')

    word = Word.objects.filter(id=word_id).values()[0]

    if request.method == 'POST':
        id, word = Word.objects.filter(id=word_id).delete()
        messages.success(request, "Successfully Deleted")
        return redirect('user-profile', pk=pk)

    context = {'word': word}
    return render(request, 'gre/delete_word.html', context)


@login_required(login_url='login')
def delete_cat(request, pk, cat_id):
    if request.user.id != int(pk):
        return redirect('error')

    cat = Category.objects.filter(id=cat_id).values()[0]

    if request.method == 'POST':
        id, cat = Category.objects.filter(id=cat_id).delete()
        messages.success(request, "Successfully Deleted")
        return redirect('user-profile', pk=pk)
    context = {'cat': cat}
    return render(request, 'gre/delete_cat.html', context)


@login_required(login_url='login')
def edit_word(request, pk, word_id):

    if request.user.id != int(pk):
        return redirect('error')

    word = Word.objects.get(id=word_id)
    categories = Category.objects.all()

    if request.method == 'POST':
        if request.POST.get('example') == '' or request.POST.get('meaning') == '':
            messages.error(request, "Cannot be empty")
        else:
            word_cat = request.POST.get('category') or None
            if not word_cat:
                word_cat = word.category or None

            else:
                word_cat = Category.objects.get(id=word_cat)

            Word.objects.filter(id=word_id).update(
                meaning=request.POST.get('meaning'),
                example=request.POST.get('example'),
                category=word_cat
            )
            messages.success(request, "Word Details Updated!")
            return redirect('user-profile', pk=pk)

    else:
        form = WordForm()

    context = {'categories': categories, 'word': word, 'form': form}
    return render(request, 'gre/edit_word.html', context)


def quiz_home(request, pk):

    if request.user.id != int(pk):
        return redirect('error')

    if request.POST:
        ans = request.POST

        if ans["answer"] == ans["choice"]:
            messages.success(request, "Correct!")
        else:
            messages.error(request, "Wrong!")

    words = Word.objects.all().filter(learner=request.user)
    if len(words) < 4:
        return redirect('error')

    exhaust_data = list(words)[:10]
    option_data = list(words)[:10]

    temp = option_data.copy()
    q = random.choice(exhaust_data)
    exhaust_data.remove(q)
    temp.remove(q)
    other_op = [q]

    for _ in range(3):
        t = random.choice(temp)
        other_op.append(t)
        temp.remove(t)

    random.shuffle(other_op)

    context = {'other_op': other_op, 'word': q}
    return render(request, 'gre/quiz_home.html', context)


def progress(request, pk):
    if request.user.id != int(pk):
        return redirect('error')

    graph = figure(title="Words added in Past Month", height=610)
    graph.xaxis.axis_label = "Days"

    graph.yaxis.axis_label = "No. of Words"
    graph.xaxis.axis_label_text_font_size = '15pt'
    graph.yaxis.axis_label_text_font_size = '15pt'

    x = [i + 1 for i in range(30)]
    y = [random.uniform(5, 10) for _ in range(30)]

    line_color = "red"
    line_dash_offset = 1

    legend_label = "Words Added"

    graph.line(x, y,
               line_color=line_color,
               line_dash_offset=line_dash_offset,
               legend_label=legend_label,
               line_width=2,
               )

    script, div = components(graph)

    x = {
        'Categorized': random.randint(40, 90),
        'Uncategorized': random.randint(10, 70),
    }

    data = pd.Series(x).reset_index(name='value').rename(
        columns={'index': 'country'})
    data['angle'] = data['value']/data['value'].sum() * 2*pi
    data['color'] = ('#0000ff', '#ff0000')

    p = figure(height=300, title="No. of Words which are assigned a category", toolbar_location=None,
               tools="hover", tooltips="@country: @value", x_range=(-0.5, 1.0))

    p.wedge(x=0, y=1, radius=0.3,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend_field='country', source=data)

    p.axis.axis_label = None
    p.axis.visible = False
    p.grid.grid_line_color = None

    script1, div1 = components(p)

    categories = [
        'Prediction',
        'Sign/Warning',
        'Causing Fear',
        'Very Angry',
        'Detailed Knowledge',
        'Shocking',
        'Atractive',
        'Awkward',
        'Spread',
        'Talented'
    ]

    counts = [random.randint(2, 9) for _ in range(len(categories))]

    source = ColumnDataSource(data=dict(categories=categories, counts=counts))

    q = figure(x_range=categories, height=300,
               toolbar_location=None, title="Category Counts")

    q.vbar(x='categories', top='counts', width=0.8, source=source, legend_field="categories",
           line_color='white', fill_color=factor_cmap('categories', palette=Category20c[len(categories)], factors=categories))

    q.xgrid.grid_line_color = None
    q.y_range.start = 0
    q.y_range.end = 9
    q.legend.orientation = "horizontal"
    q.legend.location = "top_center"

    script2, div2 = components(q)
    context = {'script': script, 'div': div, 'div1': div1,
               'script1': script1, 'div2': div2, 'script2': script2}

    return render(request, 'gre/progress.html', context)
