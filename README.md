# dropbox-books-trick

dependencies:
/cvmfs/sft.cern.ch/lcg/views/LCG_108/x86_64-el9-gcc15-opt/setup.sh o ambienti similari
da installare in locale: binari firefox e geckodriver

comando di test su lxplus:
python3 blessed_new3.py --geckodriver /afs/cern.ch/work/r/rgargiul/gecko/geckodriver --url "https://www.dropbox.com/scl/fi/5wysmbfkvb69ks6f1ntq9/Arabia-Francesco-Saverio-Sorrento-Napoli-Tip.-della-Regia-Universit-1899.pdf?rlkey=6wj0r6l64tzdko6ut7ado4i10&e=4&st=39baj82d&dl=0"


per la lista:

wget https://www.bibliotecastoricasorrentina.it/biblioteca-digitale-penisola-sorrentina -O lista.html
cat lista.html | grep dropbox | grep pdf | awk -F 'href="' '{print "\""$2}' | awk -F '</a>' '{print $1"\""}' | sed s/\"\ rel=\"noopener\"\>/\",\"/g > lista.csv
