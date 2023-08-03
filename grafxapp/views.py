from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse

# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

from .forms import GraphForm
import networkx as nx






# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

def graph(request):
    return render(request, 'grafxapp/graph.html')

def index(request):
    return render(request, 'grafxapp/index.html')

# Create an `about` view to render a static about page
def about(request):
    return render(request, 'grafxapp/about.html')


# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, 'grafxapp/contact.html')

# Create a `login_request` view to handle sign in request
# Define the login_request view
def login_request(request):

    # Check if the request method is POST
    if request.method == 'POST':
        
        # If it's a POST request, get the username and password from the request
        username = request.POST['username']
        password = request.POST['password']
        
        # Use Django's built-in authenticate function to check if the provided
        # username and password correspond to a valid user
        user = authenticate(username=username, password=password)

        # If the user is valid (i.e., authenticate didn't return None),
        if user is not None:
            
            # Use Django's built-in login function to log the user in
            login(request, user)
            
            # Redirect the user to the index page
            # We use the reverse function to get the URL associated with the 'index' view
            return HttpResponseRedirect(reverse('grafxapp:index'))
        
        # If the user is not valid (i.e., authenticate returned None),
        else:
            
            # Render the login page again, but this time include an error message
            return render(request, 'grafxapp/login.html',  {'error': 'Invalid login'})
    
    # If the request method is not POST (e.g., it's a GET request),
    else:
        
        # Render the login page without an error message
        return render(request, 'grafxapp/login.html')

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('grafxapp:index')
    
    # für Weiterleitung zu anderer Page: return HttpResponseRedirect(reverse('djangoapp:homepage'))

# Create a `registration_request` view to handle sign up request

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)
        login(request, user)
        return redirect('grafxapp:index')
    else:
        return render(request, 'grafxapp/registration.html')



# Form für die Dtaeneingabe der Netzwerke


def graph_form(request):
    if request.method == 'POST':
        form = GraphForm(request.POST)
        if form.is_valid():
            # Create graph
            G = nx.gnm_random_graph(form.cleaned_data['nodes'], form.cleaned_data['edges'])

            # Calculate the centrality values for each node
            centrality = nx.degree_centrality(G)

            # Add the centrality values to the node data
            for node in G.nodes():
                G.nodes[node]['centrality'] = centrality[node]

            # Serialize the graph to a JSON format
            data = nx.node_link_data(G)

            # Save the graph in a JSON file
            with open('grafxapp/static/graph.json', 'w') as f:
                json.dump(data, f)

            return redirect('grafxapp:graph')  # redirect to the graph rendering page
    else:
        form = GraphForm()
    return render(request, 'grafxapp/graph_form.html', {'form': form})














