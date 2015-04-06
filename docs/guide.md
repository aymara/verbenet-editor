Guide d'annotation de Verb∋Net
===============================

Ce guide a pour vocation d'expliquer comment est annoté Verb∋Net,
notamment afin de pouvoir l'interpréter en Traitement Automatique des
Langues.

Emplois et verbes les plus fréquents


de Vinf -> 'faux de' pronomialise en :

 en -> vrai de
 y -> vrai à
 ceci, cela -> faux à, faux de -> donc dans la restriction




V0 V1


-phrastique pas tout le temps, mais quand il n'y est pas c'est bien
lui


Dans les génitifs, on perd l'attribut, donc on le met dans la
restriction, avec un & si besoin si on a une autre restriction :

Attribute <+genitif(Patient)>
Attribute <+body\_part & genitif(Patient)>


Certains ADV sont présents : ce sont des compléments de manière,
normalement exclus, mais indispensables pour la phrase. Ils n'ont donc
pas de rôle.

ADV-Middle indique que la construction entière est une construction
moyenne.


Formes non codées
 * PPv
 * passif


Codage des prépositions : préposition /, pas d'espace, loc-dest etc.


Quand les complétives sont introduites par une préposition, il y a
forcément un ce. C'est "prep ce que P" (prep = en, à, dans, sur, ...).
Il est possible que prep et ce sautent

Luc a prié Marie de ce que Jean fasse la vaiselle
Luc a prié Marie que Jean fasse la vaiselle

Voir 58.2-2 (TODO site pour le reste : enlever le fait que 'de ce'
peut partir parce qu'on le sait)

Dans le cas direct, Qu Psubj reste en primary


LUI : lui est obligatoire ! (TODO site)


Vinf -> V-inf partout pour plus de cohérence


Documenter les crochets car rôle éclaté


Pas de complétive sujet



NP V (NP et NP) ensemble
TODO Rajouter une frame sans ensemble
TODO choisir si exemple est dans primary ou syntax

TODO V0-inf -> VAgent-inf, VPatient-inf, ...


Potentiel plusieurs langues

On permet des traductions parce que même quand les constructions
changent, les rôles restent.
