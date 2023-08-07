# in grafxapp/forms.py
from django import forms
from .models import Node, Edge, Graph

class GraphForm(forms.Form):
    nodes = forms.IntegerField(label='Number of nodes')
    edges = forms.IntegerField(label='Number of edges')
    # add more fields as needed

class UploadCSVForm(forms.Form):
    csv_file = forms.FileField(label='Wähle eine CSV-Datei')

class NodeForm(forms.ModelForm):
    class Meta:
        model = Node
        fields = ['name', 'weight','branche' ]  # Fügen Sie alle gewünschten Felder hinzu

class EdgeForm(forms.ModelForm):
    def __init__(self, *args, selected_graph=None, **kwargs):
        super(EdgeForm, self).__init__(*args, **kwargs)
        if selected_graph:
            # Beschränken Sie z.B. die Auswahl von Knoten auf diejenigen, die zu einem bestimmten Diagramm gehören
            self.fields['source'].queryset = Node.objects.filter(graph=selected_graph)
            self.fields['target'].queryset = Node.objects.filter(graph=selected_graph)

    class Meta:
        model = Edge
        fields = ['source', 'target', 'weight']


