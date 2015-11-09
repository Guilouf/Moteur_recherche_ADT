#la premiere ligne est pour linux donc bat les couilles
# -*- coding: utf-8 -*-

import os, os.path
import nltk
import email
import pickle #serialisation
import codecs
import re

"""
class main:
    pass  
    
    LISTE DE CHIERS BUGGANT:
    -1 fariza ok
    -2 nazim ok
    -3 dassaul BUUUUUUUUUG
    -4 jerome salse ok
    -5 hello bonjour BUUUUG
    -6 offre demploi ok
    -7 crb anim ok
    =>C'est un problème d'interlignes
    
    muahaha common word fr est en ansi, common word en en utf 8! magnifique C'est vraiment de la grosse merde ses fichiers
    pourquoi les chiffre d'ailleurs ds le common word fr??
    plus les subjects qui ont 3 encodages différents, et en plus en dur dans le fichier original!=>traité avec decode_header() (qq érreurs subsistent mais bon..)
    penser à proposer de download les fichier nltk pour lancer le truc sur une autre machine
    
    
    question: est il vraiment necessaire de garder les accents? je crois que je me fait chier avec en fait...
    et allez un mail en base 64...(le 82)
"""
"""
faire un fichier inversé ac les mots originaux et l'index de liste de leur racine.
faire une correction dans le fichier inversé pour regrouper en un seul mot ceux ayants des fautes, ac la forme retenue etant celle ayant le + grd effectif
"""

"""
bordel de cul, les mails sortent dans un ordre totalement aléatoire...
en cause: os.listdir... qui fait en ordre alphabétique. oui oui.
"""

class Parsemail:

    def __init__(self):
        
        print("start __init__ parsemail" )        
        
            
        self.filepath = "C:/Users/Guigui/Desktop/M2/ADT/Moteur_Recherche/archives_SFBI/2015_06_10-bioinfo_archives_annee_2014/Traitement_Interlignes/"
        
        self.pathFR = "C:/Users/Guigui/Desktop/M2/ADT/Moteur_Recherche/Outils/common_words.total_fr.txt"
        
        self.pathENG = "C:/Users/Guigui/Desktop/M2/ADT/Moteur_Recherche/Outils/common_words.total_en.txt"
        
        listdefichenbordel = os.listdir(self.filepath)
        self.listdefich = sorted(listdefichenbordel, key = lambda num: int(num[:-8]) ) #◘"""attention, faut que les fichiers aient bien .recoded à la fin..."""
        
        self.feuille = open("feuille.txt", "w+", encoding='utf-8')
        
        self.stoplist = self.stopwords() 
    
    """
    ############################
    FONCTION qui crée une liste à partir des fichiers de stop words anglais et et francais, et plus quelques ajouts personnels
    APPELEE dans: le main
    PB: c'est-à-dire: stopword, mais la reg ex enlève le c'..=====>appliquer une regex aux stop words
    ############################
    """
    def stopwords(self):
        stopEN = open(self.pathENG, "r", encoding='utf-8')
        stopFR = open(self.pathFR , "r", encoding='utf-8')
        stoplist = []
        for i in stopEN:
            stoplist.append(i.strip().replace("_"," ")) #peut être les ', la tokenisation peut aussi poser problème. encodage correspond, c'est bon de ce coté
            #print i.strip().replace("_"," ").encode('utf-8')
        for j in stopFR:
            stoplist.append(j.strip().replace("_"," ")) #problème, c'est en ansi... mais je pense que je vais y remédier à la source... voila c'est fait.
        stoplist.extend(["al.","al","-","--",":"]) #ajoute les trucs chiants, peut etre à mettre au début de la liste pr opti. voir mm faire un système de fréquence pour mettre les truc a enlever les plus fréquents en avant.. mais ca sert mois grace à la reg ex.
    
        return stoplist
    
                               
    """
    ############################
    FONCTION 
    APPELEE dans: parsemail
    ############################
    """
    def tokenostop(self,corpsmail, stoplist): #mettre les mots 
        #print corpsmail
        
        mailtokenibad = nltk.word_tokenize(corpsmail) #marche, mais encodage un peu chelou... puis marche assez mal en fait... (point esseulé, ou à la fin d'un mot. , (L')Utilisation.. /http séparé => PROBLEME DES "d'"
       
        mailtokeni =  []
        for i in mailtokenibad:
            fix = re.sub("((.)?'|)((?P<mot>[ôûùéêèñïçàâ0-9A-Za-z_ @:-]*).?)", "\g<mot>", i) #mots a problème:  THÉMATIQUE(et ouais putain les majuscules..(corrigé normalement).(\x89)), et le petit nouveau: le en dash...:\xe2\x80\x93(?),aujourd'hui
            #fix = i #décommenter pour desactiver la regex                                    refaire la regex en mode compilé
            #print fix
            if fix == '': 
                #print i #regarder les caractères supprimé par la regex.. et ca marche super!!!
                pass
            else : mailtokeni.append(fix) #regarder quand meme si ca n'a pas bouffer certains mots
        
        for i in stoplist: #parcourt la stoplist
            if i in mailtokeni:#regarde si un stop word est dans le mail
                #print(i) #print le stopword en commun
                #ici mettre un regex pour enlever les d' et les points à la fin du mot. ou adapter nltk
                mailtokeni = [x for x in mailtokeni if x != i] #comprehension list, faible complexité nrmlt: ne retourne que les éléments du mail qui sont différents du stopword
                #mettre en lowercase, faire correspondre l'encodage=>fait
            
        return mailtokeni
    
    
    """
    ############################
    FONCTION pour extraire le contenu des mails, et le separé en une liste de 3 éléments
    APPELEE dans: le main
    ############################
    """
    
    def parsemail(self): #listdefich,filepath,stoplist
        
        #j = listdefich[1] #a remplacer par un for...
        
        totalmail = []
        
        for j in self.listdefich:
            mailform = []
            
            fichmail = open(self.filepath+j,"r", encoding='utf-8') #bon je pense que c deja decodé peut etre
            mail = fichmail.read() 
            contenumail = email.message_from_string(mail)
            
            
            mailform.append(contenumail['subject'].lower()) #faudra extraire le tag, pour lui donner un grand poids Il y a de iso8859-1 (latin1) et du utf8, même du windows 1252 selon le mail de provenance... donc à rencoder si on veut en faire qqchose.
            mailform.append(contenumail['date'].lower())
            mailform.append(contenumail['from'])
            mailtokeni = self.tokenostop(contenumail.get_payload().lower(),self.stoplist) #choppe le contenu du mail en lowercase, le problème c'est que Equipe se transforme en equipe au lieu de équipe...
            #faire un fichier regroupant tous les mots trouvés
            self.imprimante(mailtokeni)
            mailform.append(mailtokeni) #ici, tokeniser, lemmatiser...
    
            #print("//////////////////////////////////////////////////////////////////")
            
            """
            print contenumail['subject'].lower()
            print contenumail['subject'].lower().encode()
            """
            
            
            #print (mailform[0])
            totalmail.append(mailform) 
        #print (totalmail)  
        #print(self.listdefich)
        return totalmail
    
    def imprimante(self,mailtokeni): #en faire un fichier inversé avec le nombre total d'occurences du mot, puis les textes dans lequel apparait le mot avec le nombre d'occurence dans le texte
        #pour l'instant je vais faire un retraitement du fichier
        for mot in mailtokeni:
            self.feuille.write(mot)
            self.feuille.write('\n')
    
    
if __name__ == "__main__": #permet de ne pas executer à l'import du fichier mais seulement qd on ne run que ce fichier
    ft = Parsemail()
          
    ft.parsemail() 

    print("arrete d'imprimer ca c'est pas dans la classe bordel t con ou quoi??")



    
