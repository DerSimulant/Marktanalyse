from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse
from django.shortcuts import get_object_or_404
# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

from .forms import GraphForm
import networkx as nx
from .forms import UploadCSVForm
from .models import Node, Edge
from io import TextIOWrapper
import csv
from .models import Node, Edge, GraphProperties




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

#CSV hochladen und Daten in Datenbank speichern
def upload_csv(request):
    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():

            # Löschen der alten Daten aus der Datenbank
            Node.objects.all().delete()
            Edge.objects.all().delete()
            GraphProperties.objects.all().delete()

            csv_file = TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8')
            reader = csv.reader(csv_file, delimiter=';', quotechar='"')

            nodes = {} # um doppelte Knoten zu vermeiden

            # Überspringe die Überschriftszeile
            next(reader)

            for row in reader:
                # Zerlege die Zeile in die drei Werte
                node1_name, node2_name, weight = row[0].split(';')

                # Knoten erstellen oder abrufen, wenn sie bereits existieren
                node1 = nodes.get(node1_name) or Node.objects.create(name=node1_name)
                node2 = nodes.get(node2_name) or Node.objects.create(name=node2_name)

                # Kante erstellen
                Edge.objects.create(source=node1, target=node2, weight=float(weight))

                # Knoten im Wörterbuch speichern
                nodes[node1_name] = node1
                nodes[node2_name] = node2

            calculate_and_save_graph_properties()

            return redirect('grafxapp:display_graph')
    else:
        form = UploadCSVForm()
    return render(request, 'grafxapp/upload_graph.html', {'form': form})




#Informationen zum Graphen aus der Datenbank abrufen
from django.shortcuts import render
import json
from .models import Edge

def display_graph(request):
    edges = Edge.objects.select_related('source', 'target').all()
    graph_data = {
        'nodes': [],
        'links': [
            {
                'source': edge.source.name,
                'target': edge.target.name,
                'weight': edge.weight
            }
            for edge in edges
        ]
    }

    # Extract unique nodes from the list of edges
    nodes_set = set()
    for link in graph_data['links']:
        nodes_set.add(link['source'])
        nodes_set.add(link['target'])
    graph_data['nodes'] = [{'id': node} for node in nodes_set]

    return render(request, 'grafxapp/graph.html', {'graph_data': graph_data})

#werte berehcnen für den Graphen
def calculate_and_save_graph_properties():
    # Erstellen Sie einen leeren ungerichteten Graphen mit networkx
    nx_graph = nx.Graph()

    # Fügen Sie die Knoten und Kanten aus der Datenbank hinzu
    edges = Edge.objects.all()
    for edge in edges:
        nx_graph.add_edge(edge.source.name, edge.target.name, weight=edge.weight)

    # Berechnen Sie die Kennwerte
    degree_values = dict(nx_graph.degree())
    average_degree = sum(degree_values.values()) / len(degree_values)
    diameter = nx.diameter(nx_graph)
    clustering_coefficient = nx.average_clustering(nx_graph)
    # Weitere Kennwerte, die Sie berechnen möchten

    # Speichern Sie die Kennwerte in der Datenbank
    graph_properties, created = GraphProperties.objects.get_or_create(
        defaults={
            'average_degree': 0.0,  # Setzen Sie hier den gewünschten Standardwert
            'diameter': diameter,
            'clustering_coefficient': clustering_coefficient,
            # Setzen Sie hier weitere Standardwerte für andere Felder, falls erforderlich
        }
    )

    # Aktualisieren Sie die berechneten Kennwerte
    graph_properties.average_degree = average_degree
    graph_properties.save()
    # Fügen Sie den Code hinzu, um weitere Kennwerte in properties zu speichern

    return HttpResponse("Graphentheoretische Kennwerte wurden berechnet und in der Datenbank gespeichert.")
















