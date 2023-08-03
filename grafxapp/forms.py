# in grafxapp/forms.py
from django import forms

class GraphForm(forms.Form):
    nodes = forms.IntegerField(label='Number of nodes')
    edges = forms.IntegerField(label='Number of edges')
    # add more fields as needed
