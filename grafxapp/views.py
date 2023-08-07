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
from .models import Node, Edge, GraphProperties, Graph
from django.db import transaction



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


@transaction.atomic
def upload_csv(request):
    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            # Erstellen eines neuen Graphen-Eintrags
            graph = Graph.objects.create(name=f"Graph-{datetime.now().strftime('%Y%m%d%H%M%S')}")

            csv_file = TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8')
            reader = csv.reader(csv_file, delimiter=';')

            nodes = {}  # um doppelte Knoten zu vermeiden

            # Überspringe die Überschriftszeile
            next(reader)

            for row in reader:
                node1_name, node1_weight, node2_name, node2_weight, weight = row

                if node1_name not in nodes:
                    node1, _ = Node.objects.get_or_create(name=node1_name, graph=graph, defaults={"weight": float(node1_weight)})
                    nodes[node1_name] = node1
                else:
                    node1 = nodes[node1_name]

                if node2_name not in nodes:
                    node2, _ = Node.objects.get_or_create(name=node2_name, graph=graph, defaults={"weight": float(node2_weight)})
                    nodes[node2_name] = node2
                else:
                    node2 = nodes[node2_name]

                Edge.objects.create(source=node1, target=node2, weight=float(weight), graph=graph)

                calculate_and_save_graph_properties(graph)


            return redirect('grafxapp:display_graph')
    else:
        form = UploadCSVForm()
    return render(request, 'grafxapp/upload_graph.html', {'form': form})





#Informationen zum Graphen aus der Datenbank abrufen
from django.shortcuts import render
import json
from .models import Edge

def display_graph(request):
    # Wenn ein Graph ausgewählt wurde
    selected_graph_id = request.GET.get('graph_id')
    if selected_graph_id:
        selected_graph = Graph.objects.get(pk=selected_graph_id)
    else:
        selected_graph = None

    # Wenn kein Graph ausgewählt ist, nehmen Sie den neuesten Graphen
    if not selected_graph:
        selected_graph = Graph.objects.last()

    # Abrufen von Kanten und Knoten des ausgewählten Graphen
    edges = Edge.objects.select_related('source', 'target').filter(graph=selected_graph)
    nodes = Node.objects.filter(graph=selected_graph)

    graph_data = {
        'nodes': [{'id': node.name, 'weight': node.weight, 'degree': node.degree, 'centrality': node.centrality} for node in nodes],
        'links': [
            {
                'source': edge.source.name,
                'target': edge.target.name,
                'weight': edge.weight
            }
            for edge in edges
        ]
    }

    # Alle verfügbaren Graphen holen
    all_graphs = Graph.objects.all()
    graph_properties = GraphProperties.objects.filter(graph=selected_graph).first()
    return render(request, 'grafxapp/graph.html', {
        'graph_data': graph_data,
        'all_graphs': all_graphs,
        'selected_graph': selected_graph,
        'graph_properties': graph_properties
    })


#werte berehcnen für den Graphen
def calculate_and_save_graph_properties(graph):
    # Erstellen Sie einen leeren ungerichteten Graphen mit networkx
    nx_graph = nx.Graph()

    # Fügen Sie die Knoten und Kanten aus der Datenbank hinzu
    edges = Edge.objects.filter(graph=graph)
    for edge in edges:
        nx_graph.add_edge(edge.source.name, edge.target.name, weight=edge.weight)

    # Berechnen Sie die Kennwerte
    # Durchschnittlicher Grad
    degree_values = dict(nx_graph.degree())
    if degree_values:
        average_degree = sum(degree_values.values()) / len(degree_values)
    else:
        average_degree = 0

    # Durchmesser
    # Durchmesser
    if nx_graph.nodes() and nx_graph.edges() and nx.is_connected(nx_graph):
        diameter = nx.diameter(nx_graph)
    else:
        diameter = 0  # oder einen anderen Platzhalterwert

    # Clustering-Koeffizient
    if nx_graph.nodes():
        clustering_coefficient = nx.average_clustering(nx_graph)
    else:
        clustering_coefficient = 0

    # Zentralität
    if nx_graph.nodes() and nx_graph.edges():
        centrality_values = nx.betweenness_centrality(nx_graph, weight='weight')
    else:
        centrality_values = {}

# Knotengrad (dies wurde bereits oben berechnet, also brauchen wir es hier nicht nochmal)
# degree_values = dict(nx_graph.degree())


    for node_name in nx_graph.nodes():
        node = Node.objects.get(name=node_name, graph=graph)
        node.centrality = centrality_values.get(node_name, 0)
        node.degree = degree_values.get(node_name, 0)
        node.save()

    # Speichern Sie die Kennwerte in der Datenbank
    graph_properties, created = GraphProperties.objects.get_or_create(graph=graph)
    graph_properties.average_degree = average_degree
    graph_properties.diameter = diameter
    graph_properties.clustering_coefficient = clustering_coefficient
    graph_properties.save()


    # Fügen Sie den Code hinzu, um weitere Kennwerte in properties zu speichern

    return HttpResponse("Graphentheoretische Kennwerte wurden berechnet und in der Datenbank gespeichert.")
















