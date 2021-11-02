import string
import random
liste=string.ascii_lowercase+" 0123456789"+string.ascii_uppercase
cle="Cle1Cryptage9Et2Decryptage8Application3Yakoii"

def cryptage(texte_claire):
    tr1=cesar(texte_claire)
    tr2=beaufort(tr1)
    tr3=xor(tr2)
    return tr3
def decryptage(texte_crypter):
    dc1=xor(texte_crypter)
    dc2=decryptage_beaufort(dc1)
    dc3=decryptage_cesar(dc2)
    return dc3


def cryptage_url(id):
    transformation1=crypt_url(id)
    transformation2=crypt_url(transformation1)
    transformation3=crypt_url(transformation2)

    return transformation3

def decryptage_url(id):
    
    decrypt1=decrypt_url(id)
    decrypt2=decrypt_url(decrypt1)
    decrypt3=decrypt_url(decrypt2)

    return decrypt3




def transformation_cle(cle,texte):
    list(cle)
    clef=""
    i=0
    j=0
    while i< len(texte):
        clef+=cle[j]
        if j > len(cle)-2:
            j=0
        else:
            j+=1  
        i+=1
    return clef
def cesar(texte):
    texte=str(texte)
    new=""
    for i in texte:
        j=0
        is_alpha=False
        while j< len(liste):
            k = j+13
            if k >= 63:
                k = k-63
            if i == liste[j]:
                new =new+ liste[k]    
                is_alpha=True      
            j=j+1 
            

        if is_alpha is False:
            new =new+i
            j=j+1 

    return str(new)   
def decryptage_cesar(texte):
    new=""
    for i in texte:
        j=0
        is_alpha=False
        while j< len(liste):
            k=j-13
            if k < 0:
                k = k+63           
            if i == liste[j]:
                new = new+ liste[k]     
                is_alpha = True             
            j = j+1 
        if is_alpha is False:
            new =new+i
    return str(new) 

def beaufort(texte):
    list(texte)
    clef=list(transformation_cle(cle,texte)) 
    new=""
    i=0
    while i< len(texte):
            new= new + c_beaufort(texte[i],clef[i])  
            i+=1   
    return new
def decryptage_beaufort(texte):
    list(texte)
    clef=list(transformation_cle(cle,texte)) 
    new=""
    i=0  
    while i< len(texte):
        new+=d_beaufort(clef[i],texte[i])
        i+=1  
    return new
def c_beaufort(a,b):
    if a == ' ':
        return a
    else:
        z=ord(a)-ord(b)
        if z < 0:
            z=z+75
        z+=48
        return chr(z)
def d_beaufort(c,b):
    if b == " ":
        return b
    else:
        z=ord(c)+ord(b)-96
        if z >= 75:
            z=z-75
        z=z+48
        if z > 122:
            z=z-122
        return chr(z)
def xor(texte):
    list(texte)
    clef=list(transformation_cle(cle,texte)) 
    new=""
    i=0
    while i< len(texte):
        z= ord(clef[i]) ^ ord(texte[i])
        new+=chr(z)
        i+=1  
    return new

liste1=["1","2","3","4","5","6","7","8","9","0","&","$","é","è","ç","?","!","§"]+list(string.ascii_lowercase)

def crypt_url(mot):
    mot=str(mot)
    new=""
    for i in mot:
        j=0
        c=random.randint(0,43)
        while j< len(liste1):
            k=j+5
            if k>=44:
                k=k-44            
            if i==liste1[j]:
                new =new+ liste1[k]+liste1[c]           
            j=j+1 
    return str(new) 

def decrypt_url(mot):
    mot=str(mot)
    new=""
    l=0
    for i in mot:
        j=0
        if l%2 == 0:     
            while j< len(liste1):
                k=j-5
                if k< 0:
                    k=k+44      
                if i == liste1[j]:
                    new = new+ liste1[k]        
                j=j+1 
        l+=1     
    return str(new)   

