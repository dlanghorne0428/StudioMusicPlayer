from django.core.management.base import BaseCommand
from App.models import Song


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Updating dance type strings')
        songs = Song.objects.all()
        for s in songs:
            if s.dance_type == 'Gen' or s.dance_type == "N/A":
                s.dance_type = "NoAlt"
            elif s.dance_type == "Bac":
                s.dance_type = "Bchat"
            elif s.dance_type == "Bol":
                s.dance_type = "Bolo"
            elif s.dance_type == "Jiv":
                s.dance_type = "Jive"       
            elif s.dance_type == "Mer":
                s.dance_type = "Meren"   
            elif s.dance_type == "PD":
                s.dance_type = "Paso"  
            elif s.dance_type == "Pea":
                s.dance_type = "Pbody"    
            elif s.dance_type == "Q":
                s.dance_type = "Qstep"     
            elif s.dance_type == "Rum":
                s.dance_type = "Rumba"
            elif s.dance_type == "Sam":
                s.dance_type = "Samba"    
            elif s.dance_type == "Tan":
                s.dance_type = "Tango"  
            elif s.dance_type == "VW":
                s.dance_type = "VWal"   
            elif s.dance_type == "Wal":
                s.dance_type = "Waltz"   
            elif s.dance_type == "Sho":
                s.dance_type = "Show"              
                
            if s.alt_dance_type == 'Gen' or s.alt_dance_type == "N/A":
                s.alt_dance_type = "NoAlt"  
            elif s.alt_dance_type == "Bac":
                s.alt_dance_type = "Bchat"        
            elif s.alt_dance_type == "Bol":
                s.alt_dance_type = "Bolo"    
            elif s.alt_dance_type == "Jiv":
                s.alt_dance_type = "Jive"                   
            elif s.alt_dance_type == "Mer":
                s.alt_dance_type = "Meren"  
            elif s.alt_dance_type == "PD":
                s.alt_dance_type = "Paso"       
            elif s.alt_dance_type == "Pea":
                s.alt_dance_type = "Pbody" 
            elif s.alt_dance_type == "Q":
                s.alt_dance_type = "Qstep" 
            elif s.alt_dance_type == "Rum":
                s.alt_dance_type = "Rumba"                 
            elif s.alt_dance_type == "Sam":
                s.alt_dance_type = "Samba"
            elif s.alt_dance_type == "Tan":
                s.alt_dance_type = "Tango"
            elif s.alt_dance_type == "VW":
                s.alt_dance_type = "VWal"    
            elif s.alt_dance_type == "Wal":
                s.alt_dance_type = "Waltz"  
            elif s.alt_dance_type == "Sho":
                s.alt_dance_type = "Show" 
                
            s.save()
            
        