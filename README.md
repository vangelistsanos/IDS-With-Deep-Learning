# University of East London

## Μητροπολιτικό Κολλέγιο

### MSc Artificial Intelligence

## "Ανίχνευση διαδικτυακών Επιθέσεων με χρήση νευρωνικών δικτύων"



### Φοιτητής : Τσάνος Βαγγέλης
### Επιβλέπων Καθηγητής : Δρ. Λάλος Πέτρος



**Δομή**
 -  /backend  : το flask api για χρήση απο το dashboard + artifacts απο το tabnet
 
 -  /frontend : svelte dashboard για simulation κίνησης και οπτικοποίηση
 
 -  /models   : google colab κώδικας των μοντέλων + αξιολόγηση + EDA


**Σημείωσεις**
1. Τα dataset που χρησιμοποιήσαμε και για τον κώδικα του dashboard και για την εκπαίδευση των μοντέλων βρίσκονται στο παρακάτω link 
https://www.kaggle.com/datasets/mrwellsdavid/unsw-nb15 

2. Για την εκπαίδευση των μοντέλων καθώς και για την ανάλυση των dataset χρησιμοποιήσαμε google colab και google drive
Στο google drive θα πρέπει να ανεβούν δύο αρχεία που βρίσκονται στο προηγούμενο link με ονόματα
                  
- UNSW_NB15_training-set.csv
- UNSW_NB15_testing-set.csv

Αυτά πρέπει να βρίσκονται μέσα στο path του google drive
/content/drive/My Drive/UNSW-NB15/

Επίσης θα πρέπει να δώθούν δικαιώματα στο google drive προκειμένου να τα διαβάσει.

3. Για την εκπαίδευση όλων των μοντέλων χρησιμοποιήσαμε T4 + GPU με High RAM. Ειδικά για το CNN μοντέλο είναι απαραίτητο.

4. Για να τρέξουν τα hyperparameter tunings θα πρέπει να αλλαχτούν τα παρακάτω
   απο
   
   `USE_TUNER = False`

   `FRACTION = 1.0 #100%`

   σε
   
    `USE_TUNER = True`
   
    `FRACTION = 0.3 #30%`



## Features
 - Προσομοίωση κίνησης με δεδομένα απο το test dataset  UNSW_NB15_testing-set.csv
 - Αναγνώρισης επίθεσης
 - Στατιστικά επιθέσεων

## Installation
 -- (backend)
 
 `cd .../backend` 
 
 `pip install -r requirements.txt`
 

 -- (frontend)
 
 `cd .../frontend`
 
 `npm install`
 
## Run
 --Start API (back end)
 
  `cd .../backend` 
  
  `python app.py`

 --Start Dashboard (front end)
 
 `cd .../frontend`
 
 `npm run dev`





