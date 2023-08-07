from django.contrib import admin

# Register your models here.
from .models import Node, Edge, GraphProperties, Graph

admin.site.register(Node)
admin.site.register(Edge)
admin.site.register(GraphProperties)
admin.site.register(Graph)
