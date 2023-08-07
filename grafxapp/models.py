from django.db import models

class Graph(models.Model):
    name = models.CharField(max_length=200, unique=True)
    creation_date = models.DateTimeField(auto_now_add=True)

class Node(models.Model):
    name = models.CharField(max_length=100)
    graph = models.ForeignKey(Graph, on_delete=models.CASCADE, null=True)
    # Hinzufügen eines Gewichtungsfeldes für die Knoten
    weight = models.FloatField(default=1.0)
    centrality = models.FloatField(default=0.0)
    degree = models.IntegerField(default=0) 
    # ... (andere Felder)
    class Meta:
        unique_together = ['name', 'graph']

class Edge(models.Model):
    source = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="source_edges")
    target = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="target_edges")
    graph = models.ForeignKey(Graph, on_delete=models.CASCADE, null=True)
    weight = models.FloatField()
    # ... (andere Felder)

class GraphProperties(models.Model):
    graph = models.OneToOneField(Graph, on_delete=models.CASCADE, null=True)
    average_degree = models.FloatField(default=0)
    diameter = models.IntegerField(default=0)
    clustering_coefficient = models.FloatField(default=0)
    # ... (andere Felder)
