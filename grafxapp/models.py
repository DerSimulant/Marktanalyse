from django.db import models

class Graph(models.Model):
    name = models.CharField(max_length=200, unique=True)
    creation_date = models.DateTimeField(auto_now_add=True)

class Node(models.Model):
    name = models.CharField(max_length=100) #Unternehmensname
    graph = models.ForeignKey(Graph, on_delete=models.CASCADE, null=True)
    # Hinzufügen eines Gewichtungsfeldes für die Knoten
    weight = models.FloatField(default=1.0) #Unternehmensgröße oder z.B. Prestigewert
    centrality = models.FloatField(default=0.0)
    degree = models.IntegerField(default=0) 
    BRANCH_CHOICES = [
        ('UNK', 'Unbekannt'),
        ('IT', 'Informationstechnologie'),
        ('FIN', 'Finanzen'),
        ('HEA', 'Gesundheit'),
        ('CAR', 'Automobilindustrie'),
        ('CON', 'Bauwesen'),
        ('CHE', 'Chemie'),
        ('EL', 'Elektrizität'),
        ('LOG', 'Logistik'),
        ('TOUR', 'Tourismus'),
        ('AGR', 'Landwirtschaft'),
        ('EDU', 'Bildung'),
        ('ENE', 'Energie'),
        ('FAS', 'Mode'),
        ('FOO', 'Lebensmittel und Getränke'),
        ('GOV', 'Regierung und öffentliche Verwaltung'),
        ('MED', 'Medien'),
        ('MIN', 'Bergbau'),
        ('PHAR', 'Pharma'),
        ('REA', 'Immobilien'),
        ('RET', 'Einzelhandel'),
        ('SPOR', 'Sport'),
        ('TEL', 'Telekommunikation'),
        ('TRAV', 'Reisen'),
        ('ENT', 'Unterhaltung'),

        # ... fügen Sie hier weitere Branchen hinzu
    ]
    branche = models.CharField(max_length=4, choices=BRANCH_CHOICES, default='UNK')
    # ... (andere Felder)
    def __str__(self):
        return self.name 
    #ggf Branche hinzufügen, Umsatzrendite, Gesamtumsatz etc., Lokation können bei Konkurrenz interessant sein und mit d3 auf einer map zu sehen 
    #zusätzlich zum Upload ein UI um durch Forms die Daten zu erstellen oder auch um Unternehmen zu einem bestehenden Graphen hinzuzufügen
    class Meta:
        unique_together = ['name', 'graph']

class Edge(models.Model):
    source = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="source_edges")
    target = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="target_edges")
    graph = models.ForeignKey(Graph, on_delete=models.CASCADE, null=True)
    weight = models.FloatField() #positive Werte in Grün, Gewicht dauer der Beziehung, negative Werte rot entspricht Konkurrenz, Gewichte = Feindschaftsgrad
    # ... (andere Felder)

class GraphProperties(models.Model):
    graph = models.OneToOneField(Graph, on_delete=models.CASCADE, null=True)
    average_degree = models.FloatField(default=0)
    diameter = models.IntegerField(default=0)
    clustering_coefficient = models.FloatField(default=0)
    # ... (andere Felder)
