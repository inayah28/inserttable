from django.shortcuts import render
from django.http import HttpResponse
from .models import Matkul
from .models import Matkur
from .models import Profesi
from .models import Profesi_Matkul
from .models import Profesi_Matkur
import csv
from .modNormalize import normalize
from collections import Counter
from django.http import Http404
def index(request):
    profesi = Profesi.objects.all()
    context = {
        'Profesis':profesi,
        'judul':'TEKNIK INFORMATIKA',
    }
    if request.method == 'POST':
        nama_profesi = request.POST['name_profesi']
       
        profesi_matkul = Profesi_Matkul.objects.filter(profesi=nama_profesi)
        profesi_matkur = Profesi_Matkur.objects.filter(profesi=nama_profesi)
        
        context = {
            'Profesi_Matkuls' :profesi_matkul,
            'Profesi_Matkurs' :profesi_matkur,
            'profesi':nama_profesi,
           
        }
       
        if not profesi_matkul:          
            data_profesi = {
                'ADVANCE ANIMATOR':'cekprofesi/data/profesi/uk_aa.csv',
                'LEAD PROGRAMMER':'cekprofesi/data/profesi/uk_lp.csv',
                'NETWORK ADMINISTRATOR':'cekprofesi/data/profesi/uk_na.csv',
                         
            }
            data_rps = {
                'cekprofesi/data/matkul/sap_ap1.csv':('IT045201','Algoritma dan Pemrograman 1','2'),
                'cekprofesi/data/matkul/sap_ap2.csv':('IT045202','Algoritma dan Pemrograman 2','2'),
                'cekprofesi/data/matkul/sap_ap3.csv':('IT045203','Algoritma dan Pemrograman 3','2'),
                'cekprofesi/data/matkul/sap_gk1.csv':('AK045205','Grafik Komputer 1','3'),
                'cekprofesi/data/matkul/sap_gk2.csv':('AK045206','Grafik Komputer 2','2'),
                'cekprofesi/data/matkul/sap_pbo.csv':('AK045213','Pemrograman Berbasis Objek','2'),
                'cekprofesi/data/matkul/sap_pm.csv':('AK045215','Pemrograman Multimedia',''),
                'cekprofesi/data/matkul/sap_skk.csv':('IT045237','Sistem Keamanan Komputer','2'),
                'cekprofesi/data/matkul/sap_pj.csv': ('AK045214', 'Pemrograman Jaringan','2'),
                'cekprofesi/data/matkul/sap_rpl2.csv': ('AK045227', 'REKAYASA PERANGKAT LUNAK 2','2'),
                'cekprofesi/data/matkul/sap_rpl1.csv': ('AK045226', 'REKAYASA PERANGKAT LUNAK 1','2')
            }
            for profesi1, dataset_profesi in data_profesi.items():
                if request.POST.get('name_profesi') == profesi1:
                    with open (dataset_profesi, 'r', encoding = 'utf-8')as csv_file:
                        csv_reader = csv.reader(csv_file)
                        next(csv_reader)
                        list_kw_profesi = []
                        for row in csv_file:
                            usenorm = normalize()
                            text_norm = usenorm.tokenize(row)
                            list_kw_profesi.extend(text_norm)
                        keyword_profesi = Counter(list_kw_profesi)

            profesi_matkul = []
            for dataset_rps, matkul1 in data_rps.items():
                with open(dataset_rps, 'r', encoding = "utf-8") as csv_file:
                    csv_reader = csv.reader(csv_file)
                    next(csv_reader)

                    list_kw_rps = []
                    for row in csv_file:
                        usenorm = normalize()
                        text_norm = usenorm.tokenize(row)
                        list_kw_rps.extend(text_norm)
                    keyword_rps = Counter(list_kw_rps)

                    def jaccard_similarity(x, y):
                        intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
                        union_cardinality = len(set.union(*[set(x), set(y)]))
                        return intersection_cardinality/float(union_cardinality)

                    hasil = jaccard_similarity(list_kw_profesi, list_kw_rps)
                    hasil_percen = '{0:.0%}'.format(hasil)
                    kata_sama = set.intersection(*[set(list_kw_profesi), set(list_kw_rps)])

                    print ('Hasil Similarity Profesi '+request.POST.get('name_profesi')+ ' dan matkul ' +matkul1[1]+ ' adalah ...')
                    print ('  ' +hasil_percen+ '\n')

                if hasil > 0:
                    profesi_matkul.append(matkul1)
                    print('daftar kata penting untuk profesi '+request.POST.get('name_profesi') + '\n')
                    print(str (list_kw_profesi)+ '\n\n')
                    print('daftar kata penting mata kuliah '+matkul1[1]+ '\n')
                    print(str(list_kw_rps)+ '\n\n')
                    print('jumlah masing masing kata penting profesi ' +request.POST.get('name_profesi')+ '\n')
                    print(str(len(keyword_profesi))+ '\n\n')
                    print('jumlah masing masing kata di sap matakuliah ' +matkul1[1]+'\n')
                    print(str(len(keyword_rps))+ '\n\n')
                    print('Hasil Similarity Profesi ' + request.POST.get('name_profesi') + ' dan sap matakuliah ' +matkul1[1]+ ' adalah \n')
                    print('('+str(len(kata_sama))+' / ('+str(len(keyword_rps))+' + '+str(len(keyword_profesi))+' - '+str(len(kata_sama))+'))* 100% = '+hasil_percen+ '\n\n')
                    print('kode unit yang sama di profesi '+request.POST.get('name_profesi')+ ' dan sap matkul ' +matkul1[1]+ ': \n')
                    print(str(kata_sama)+ '\n\n')
                    print('###\n\n')

            #insert matkul ke tabel Profesi_Matkul       
            for i in profesi_matkul:
                insert_table = Profesi_Matkul(profesi=request.POST.get('name_profesi'),kdmk=i[0],matkul=i[1],semester=i[2],presentase=hasil_percen)
                insert_table.save()
