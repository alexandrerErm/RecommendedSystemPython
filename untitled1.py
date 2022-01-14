#import libraries
import pandas as pd
import numpy as np
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
from nltk.stem import PorterStemmer
import nltk
import math
import sys
import rbo

#Book Rating csv
#τα μεταφερω τα δεδομενα μου σε dataframe για καλυτερη επεξεργασια μεγαλων δεδομενων
dataRatings = pd.read_csv("BX-Book-Ratings2.csv",header=0,encoding = 'unicode_escape')
dataRatings = dataRatings.sort_values(by=['User-ID'])
dataGroup = dataRatings.groupby('User-ID')
dataUserCount = dataGroup.count()
dataUserCount.__delitem__('ISBN')
dataGroup = dataRatings.groupby('ISBN')
dataIsbnCount = dataGroup.count()
dataIsbnCount.__delitem__('User-ID')

#Users csv
dataUsers = pd.read_csv("BX-Users2.csv",header=0,encoding = 'unicode_escape')
dataUsers = dataUsers.sort_values(by=['User-ID'])
dataUsers = dataUsers.drop(dataUsers.iloc[:,2:5], axis=1 )

#Books csv
path = r'C:\Users\alexe\OneDrive\Documents\Παμακ\Ανακτηση Πληροφοριας\Eργασια 2 παραλαγη\BX-Books2.csv'
dataIsbn = pd.read_csv(path,header=0, encoding= 'latin-1')
dataIsbn = dataIsbn.sort_values(by=['ISBN'])
dataIsbn = dataIsbn.drop(dataIsbn.iloc[:,5:], axis=1 )

#remove from users those who have not rate 5 and more books
dataRatings = pd.merge(dataRatings, dataUserCount , on='User-ID')
dataUsers = pd.merge(dataUsers,dataUserCount, on = 'User-ID')
dataRatings.rename(columns={'Book-Rating_x': 'Book-Rating'}, inplace=True)
dataRatings.rename(columns={'Book-Rating_y': 'countUserRatings'}, inplace=True)

dataRatings.drop(dataRatings[dataRatings['countUserRatings']<5].index,inplace = True)
dataUsers.drop(dataUsers[dataUsers['Book-Rating']<5].index,inplace = True)

#remove the books who have been rated less than ten times
dataRatings = pd.merge(dataRatings,dataIsbnCount, on='ISBN')
dataRatings.rename(columns={'Book-Rating_x': 'Book-Rating'}, inplace=True)
dataRatings.rename(columns={'Book-Rating_y': 'countIsbnRatings'}, inplace=True)
dataRatings.drop(dataRatings[dataRatings['countIsbnRatings']<10].index,inplace = True)
dataIsbn = pd.merge(dataIsbn,dataIsbnCount, on = 'ISBN')
dataIsbn.drop(dataIsbn[dataIsbn['Book-Rating']<10].index,inplace = True)


#reprossess the book title in order to find key words
ps = PorterStemmer()
lemma = nltk.wordnet.WordNetLemmatizer()
table =str.maketrans(",?!':)(.",8*" ")
i=0
array = []
for index,book in dataIsbn.iterrows():
    x = str(book['Book-Title'])
    x = x.translate(table)            
    tokens = word_tokenize(x)
    stop_words = set(stopwords.words('english')) 
    filtered_sentence = [w for w in tokens if not w in stop_words] 
    tokens=[]
    for w in filtered_sentence: 
        x = ps.stem(w)
        x = lemma.lemmatize(x)
        tokens.append(x)
    array.append(tokens)
dataIsbn['Key-Words'] = array
dataHelp= dataIsbn
dataHelp = dataHelp.drop(dataHelp.iloc[:,1:6], axis=1)
dataRatings = pd.merge(dataRatings,dataHelp, on='ISBN')
    
#locate the three books with the more rates
# create data that has for every user the books and other informmation
dataHelp = dataIsbn.iloc[:,0:5]
dataHelp = pd.merge(dataRatings,dataHelp, on = 'ISBN')
   
for index,rates in dataUsers.iterrows():
    i = dataHelp[dataHelp['User-ID']==rates.iloc[0]]
    array.append(i)

# για καθε χρηστη να βρισκει της τρεις μεγαλυτερες βαθμολογιες του   
for k in array:
    array2.append(k['Book-Rating'].nlargest(3))
  
#πλεον στον array υπαρχει για καθε χ οι μεγλαυτερες βαθμολογιες και ποια ειναι αυτα τα βιβλία
array=[]
w = []
for k in array2:
    for i in range(len(k)):
        w.append(dataHelp[dataHelp.index == k.index[i]])
    array.append(w)
    w = []

# βρισκω τις λέξεις κλειδια τους σκηνοθετες και χρονολογιες για καθε χρηστη  

array3 = []
array2 = []
array1 = []
w = []
x = []
y = []
for k in array:
    for i in k:
        w.append(i.iloc[:,5].values[0])
        x.append(i.iloc[:,7].values[0])
        y.append(i.iloc[:,8].values[0])
    array2.append(w)
    array1.append(x)
    array3.append(y)
    w = []
    x = []
    y = []

w = []
for k in array2:
    if(len(k)==1):
        i = (list(k[0]))
    elif(len(k)==2):
        i = (list(set().union(k[0],k[1])))
    elif(len(k)==3):
        i = (list(set().union(k[0],k[1],k[2])))
    w.append(i)
    
    
dataUsers['General-Key-Words'] = w 
#προσθετω για καθε χρηστη του σχετικούς σκηνοθέτες 
x = []
w = []
for k in array1:
    for i in k:
      x.append(i)
    (dict.fromkeys(x))
    w.append(x)   
    x=[]   
    
dataUsers['General-Director'] = w

#προσθετω για καθε χρηστη της σχετικές ημερομηνιες 
x = []
w = []
for k in array3:
    for i in k:
      x.append(i)
    (dict.fromkeys(x))
    w.append(x)   
    x=[]

dataUsers['General-year'] = w              



#dice,jaccard υπολογισμος και εγγραφη σε αντιστοιχα αρχεια
dataIsbn['Book-Author'].replace(np.nan,'', inplace = True)
Jfile =open('Jaccard.txt', 'w')
Dfile =open('Dice.txt', 'w')


for w in range(1,5):
    i =dataUsers.sample()
    #jaccard simularity
    jaccard = []
    y = []        
    for index,x in dataIsbn.iterrows():
        y.append(i.iloc[:,0].values[0])
        y.append(x[0])
        y.append(jaccard_similarity(i.iloc[:,3].values[0],x[6])*0.4 + jaccard_similarity(i.iloc[:,4].values[0],x[2])*0.4 + years(i.iloc[:,5].values[0],x[3])*0.4)
        jaccard.append(y)
        y = []
    
    jaccard =  Nmaxelements(jaccard,10)
 
    Jfile.write('Jaccard similarity for user: ' + str(int(i.iloc[:,0].values[0])) +'\n')
    for p in jaccard:
        for y,k in dataIsbn.iterrows():
            if(str(p[1])==str(k[0])):
                Jfile.write(str(k))
                Jfile.write('\n-------------------------------------\n') 
          

    rboValue = rbo.RankingSimilarity(jaccardList,DiceList).rbo()
    Jfile.write('Rank-biased Overlap for two lists is : ' + str(rboValue))
    #dice coefficiency
    Dfile.write('Dice similarity for user: ' + str(int(i.iloc[:,0].values[0])) +'\n')
    dice = []
    y = []    
    for index,x in dataIsbn.iterrows():
        y.append(i.iloc[:,0].values[0])
        y.append(x[0])
        y.append(dice_coefficiency(i.iloc[:,3].values[0],x[6])*0.5 + dice_coefficiency(i.iloc[:,4].values[0],x[2])*0.3 + 0.2*years(i.iloc[:,5].values[0],x[3]))
        dice.append(y)
        y = []
    
    dice = Nmaxelements(dice,10)
    for p in dice:
        for y,k in dataIsbn.iterrows():
            if(p[1]==k[0]):
                Dfile.write(str(k))
                Dfile.write('\n-------------------------------------') 
    
    rboValue = rbo.RankingSimilarity(jaccardList,DiceList).rbo()
    JDice.write('Rank-biased Overlap for two lists is : ' + str(rboValue)) 
    
Dfile.close()
Jfile.close()

    #Similarity of years
    def years(UserYears,bookYear):
        minilist = []
        check = False
        for deik in UserYears:            
            y1 = bookYear
            if(deik == np.nan):
                pass
            else:
                check = True
                sim = 1-(abs(float(float(deik)-float(y1)))/2005)
                minilist.append(sim)
        if(check == False):
            minim = 0
        else:
            minim = min(minilist)
        return minim
#JacSimAge.append(minim * 0.4)
#DicSimAge.append(minim * 0.2)







def dice_coefficiency(list1,list2):
    s1 = set(list1)
    s2 = set(list2)
    if(len(s1.union(s2)) == 0):
        return 0
    else:
        return 2*len(s1.intersection(s2)) / len(s1.union(s2))



def Nmaxelements(list1, N): 
    final_list = [] 
    maxrow = []
    for i in range(0, N):  
        max1 = 0 
        for j in list1:      
            if(j[2] > max1): 
                max1 = j[2]
                maxrow = j
                  
        list1.remove(maxrow); 
        final_list.append(maxrow) 
    return(final_list)
     


    


def jaccard_similarity(list1, list2):
    s1 = set(list1)
    s2 = set(list2)
    if(len(s1.union(s2)) == 0):
        return 0
    else:
        return len(s1.intersection(s2)) / len(s1.union(s2))

    
    
               