Guide d'annotation de Verb∋Net
===============================

.. vim: set spelllang=fr:

Ce guide a pour vocation d'expliquer comment est annoté Verb∋Net,
notamment afin de pouvoir l'interpréter en Traitement Automatique des
Langues.

Une partie des notations provient du VerbNet anglais, une autre partie
provient des tables du Lexique-Grammaire, d'autres nous sont propres.
Pour que la cohérence avec ces autres ressources soit maximale, la
notation résultante est un mélange plus ou moins harmonieux entre
l'anglais et le français.

Codage des frames
-----------------

Frames simples
``````````````

La frame la plus simple (et la plus fréquente) est la suivante :

 * Champ primaire : **NP V NP**
 * Champ syntaxe : Agent V Patient

C'est une simple construction transitive ; le sujet est Agent et
l'objet est Patient. Il peut arriver que certains syntagmes du champ
primaire soit associés à un rôle. Par exemple :

 * **NP V NP.destination** - Agent V Destination - Jessica a chargé le
   camion
 * **NP V NP.theme** - Agent V Theme - Jessica a aspergé de l'eau

C'est simplement une notation pour différencier les frames en ne
regardant que le champ primaire. Le rôle est alors indiqué à deux
endroits, ce qui peut potentiellement introduire des irrégularités ;
elles sont normalement vérifiées automatiquement, mais si vous
remarques une erreur, indiquez-la.

Prépositions
````````````

Les prépositions sont marquées à deux endroits : dans le champ
primaire avec un PP (syntagme prépositionnel) et dans le champ syntaxe
entre accolades :

 * **NP V PP** - Agent V {avec} Instrument
 * **NP V NP PP** - Agent V Patient {à/avec/et} Co-Patient
 * **NP V PP** - Theme V {{+loc}} Location

Il n'y a donc jamais d'espace entre les accolades. Quand plusieurs
prépositions sont possibles, elles sont séparées par un *slash*
(``/``). Quand une classe entière est utilisée, telle que *loc* ou
*loc-dest*, deux accolades et un plus sont utilisés : ``{{+classe}}``.
Les classes de prépositions sont définies en annexe.

Adjectifs et adverbes
`````````````````````

Les adjectifs sont marqués par ADJ ; les adverbes sont marqués par
ADV. Dans VerbNet, une distinction semble exister entre ADJ/ADV et
ADJP/ADVP : les premiers sont de simples adjectifs ou adverbes, les
seconds des syntagmes. La distinction ne nous semblant pas pertinente,
nous avons opté pour ADJ/ADV, ce qui ne signifie pas qu'on n'a jamais
de syntagmes.

Verbes
``````

Un verbe peut être prononminal (se V) ou non (V).

Les verbes peuvent être restreints avec la notation
``<+restriction>``. Trois restrictions sémantiques sont ainsi
représentées :

 * **NP se V ADV PP** - Theme se V<+middle> ADV {autour} Location - Ce
   papier s'enroule facilement autour d'un bâton
 * **NP se V** - Agent se V<+reflexive> - Luc s'est coupé
 * **NP se V** - Location se V<+neutre> - Le ciel s'est dégagé

Infinitives
```````````

Vinf éventuellement précédé d'une préposition

Participes présent
``````````````````
Vant

Propositions
````````````
une proposition : Qu Pind ou Qu Psubj éventuellement précédé de "à ce"
ou de "de ce"

Interrogatives indirectes
`````````````````````````

une interrogative indirecte : comment P, si P, combien P

Mots
````

IL, LUI, ensemble

LUI : lui est obligatoire ! (TODO site)




Sous-structures et ordre des syntagmes
``````````````````````````````````````

Les sous-structures sont systématiques supprimées. Ainsi, quand
VerbNet avait ces trois frames :

 * **NP V NP PP**
 * **NP V NP**
 * **NP V**

Verb∋Net n'en a plus qu'une, **NP V NP PP**, qui permettra de générer
ces trois là, plus d'autres, comme **NP V PP**. 

De manière similaire, l'ordre des syntagmes après le verbe n'est pas
significatif : **NP V NP PP** encode aussi **NP V PP NP**. Voir la
thèse de Juliette Thuilier (Contraintes préférentielles et ordre des
mots en français) à ce sujet.

Restrictions sémantiques
````````````````````````

Tous comme les verbes, les syntagmes peuvent être restreints avec la
notation ``<+restriction>``. Une seule restriction
sémantique existe :

 * **NP V** - Agent<+plural> V - Marie et Susanne ont bavardé

Toutes les autres restrictions sont syntaxiques.

Restrictions syntaxiques : infinitifs et propositions
`````````````````````````````````````````````````````


de Vinf -> 'faux de' se pronominalise en :

 en -> vrai de
 y -> vrai à
 ceci, cela -> faux à, faux de -> donc dans la restriction

  - des restrictions syntaxiques :  lorsque le rôle thématique ne se
    réalise pas comme un groupe nominal mais comme une infinitive, une
    proposition ou une interrogative indirecte (et aussi en 30-1-1-1
    NP Vinf ou NP Vant).  Je peux détailler.

Correspondances
```````````````

Les correspondances entre champ primaire et champ syntaxique se font
avec les règles suivantes :

les restrictions sémantiques qui sont présentes dans un champ
syntaxique disparaissent dans le champ primaire correspondant

les rôles thématiques non suivies d'une restriction syntaxique dans
le champ syntaxique correspondent dans le champ primaire à un  NP
ou à  un PP si   précédé dans le champ syntaxique d'une préposition
entre accolades  (voir Agent V Patient <-> NP V NP.patient   ou
Agent V {à} Patient <-> NP V PP.patient)

les restrictions syntaxiques apparaissent dans le champ primaire
sous forme d'infinitive, de proposition ou d'interrogative indirecte
:  je peux écrire un certain nombre de règles (qui expliquent aussi
le coup du faux de ou faux à), si tu veux.



À traiter
`````

VAgent VTheme


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



Complétives introduites par une préposition
```````````````````````````````````````````

Quand les complétives sont introduites par une préposition, il y a
forcément un ce. C'est "prep ce que P" (prep = en, à, dans, sur, ...).
Il est possible que prep et ce sautent

Luc a prié Marie de ce que Jean fasse la vaiselle
Luc a prié Marie que Jean fasse la vaiselle

Voir 58.2-2 (TODO site pour le reste : enlever le fait que 'de ce'
peut partir parce qu'on le sait)

Dans le cas direct, Qu Psubj reste en primary


Liste des rôles syntagmes, rôles et restrictions
------------------------------------------------

Syntagmes
`````````

 * NP : *noun phrase*, syntagme nominal
 * PP : *prepositional phrase*, syntagme prépositionnel
 * Vinf : verbe à l'infinitif
 * P : proposition

Rôles
`````
Les noms anglais des rôles VerbNet ont étés retenus.

 * Agent
 * Theme
 * Patient
 * Topic
 * Location
 * Recipient
 * Experiencer
 * Stimulus
 * Destination
 * Instrument
 * Source
 * Attribute
 * Beneficiary
 * Co-Patient
 * Co-Agent
 * Initial
 * Pivot
 * Goal
 * Result
 * Cause
 * Predicate
 * Asset
 * Co-Theme
 * Value
 * Product
 * Material
 * Extent
 * Trajectory

Classes de prépositions
```````````````````````

Avril 2015 : La liste n'est pas fixée précisément.



Considérations générales
------------------------

Les emplois et verbes les plus fréquents sont considérés : pas
d'emplois métaphoriques, pas d'emplois techniques, pas de verbes
désuets, etc.


Formes non codées
`````````````````
Nous n'avons pas noté des alternances qui sont considérées comme assez
générales (donc déductibles des règles de la grammaire), telles que
changements de diathèse (passivation, certaines emplois pronominales
du verbe, etc.), pronominalisation de compléments, omissions de
compléments, etc. 


Le rôle Attribute
`````````````````

Le rôle "Attribute" apparaît dans deux types de cas de figure:

1. On attribue ce rôle à un nom de procès ou propriété (nom dont le
sens est relationnel/prédicatif, que nous appelons Na) dont le sujet
ou porteur (que nous appelons Nb) peut assumer un rôle distinct dans
une phrase. Syntaxiquement, ces deux types de noms peuvent constituer
soit un syntagme nominal unique (de la forme Na de Nb, que nous
appelons SN complexe) soit deux compléments indépendants (souvent, Na
est prépositionnel, tandis que Nb est un dépendant direct du verbe
(sujet ou objet direct)). Deux types de phrases ainsi constituées sont
en relation d'alternance (du type ???voir Levin). Voici quelques
exemples :

    calibrate_cos-45.6

    * L'huile a chuté en prix de 10 pourcent = Patient V {en} Attribute {de} Extent = Nb V en Na de N
    * Le prix de l'huile a chuté de 10 pourcent = Attribute<+genitive(Patient)> V {de} Extent = (Na de Nb) V de N

    Dans le cas du SN complexe, c'est le nom tête (Na) qui assume le rôle
    d'Attribut par rapport au verbe, le nom qui lui est corrélé (Nb) se
    trouvant dépendant de celui-là. Cette configuration est décrite sous
    forme d'une restriction <+genitive(Patient)>.

2. On attribue ce rôle à un nom qui a la fonction grammaticale
d'attribut (du sujet ou de l'objet) de la grammaire traditionnelle.
Exemple :

    hire-13.5.3

    Max a recruté Luc comme lecteur = Agent V Theme {comme} Attribute
    <-phrastique>


