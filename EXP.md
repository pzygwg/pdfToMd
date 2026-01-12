Cours Complet : Programmation Avancée Java

  Introduction - C'est quoi tout ça ?

  Ce cours couvre 3 grandes thématiques qui se complètent :

  1. Introspection → Permet à un programme de "se regarder lui-même"
  2. Annotations → Des étiquettes qu'on colle sur le code pour donner des infos supplémentaires
  3. Sérialisation → Sauvegarder des objets sur disque et les recharger

  ---
  PARTIE 1 : INTROSPECTION (Réflexivité)

  1.1 Le concept de base

  Imagine que tu as un objet Java. Normalement, pour l'utiliser, tu dois connaître sa classe à l'avance :

  // Approche classique - tu SAIS que c'est une Personne
  Personne p = new Personne("Alice", 30);
  System.out.println(p.nom);  // Tu connais l'attribut "nom"

  L'introspection, c'est pouvoir explorer un objet sans connaître sa classe à l'avance :

  // Approche introspective - tu ne sais PAS ce que c'est
  Object objetMystere = ...;  // Ça peut être n'importe quoi !
  Class<?> c = objetMystere.getClass();  // On découvre sa classe
  System.out.println(c.getName());  // "Personne"

  1.2 Introspection vs Intercession

  | Introspection                  | Intercession                  |
  |--------------------------------|-------------------------------|
  | Observer le programme          | Modifier le programme         |
  | Lire les infos sur les classes | Ajouter/modifier des méthodes |
  | Java le fait bien ✓            | Java ne le fait PAS ✗         |

  Java = Introspection seulement ! (contrairement à Python ou Ruby qui peuvent modifier des classes à la volée)

  1.3 La classe Class - Le point d'entrée

  Chaque classe/type en Java a un objet Class associé. C'est ta porte d'entrée pour l'introspection.

  3 façons d'obtenir un objet Class :

  // 1. Via une instance (getClass)
  Personne p = new Personne("Alice", 30);
  Class<?> c1 = p.getClass();

  // 2. Via le nom de la classe (.class)
  Class<Personne> c2 = Personne.class;

  // 3. Via une chaîne de caractères (forName) - TRÈS UTILE
  Class<?> c3 = Class.forName("miage.m1.Personne");

  Méthodes utiles de Class :

  Class<?> c = Personne.class;

  c.getName();           // "miage.m1.Personne" (nom complet)
  c.getSimpleName();     // "Personne"
  c.getSuperclass();     // La classe parente
  c.getInterfaces();     // Les interfaces implémentées
  c.isInterface();       // Est-ce une interface ?
  c.isArray();           // Est-ce un tableau ?

  1.4 Explorer les composants d'une classe

  Les CHAMPS (Field)

  Class<?> c = Personne.class;

  // Tous les champs PUBLICS (locaux + hérités)
  Field[] champsPublics = c.getFields();

  // TOUS les champs locaux (même private)
  Field[] tousChamps = c.getDeclaredFields();

  // Un champ spécifique
  Field f = c.getDeclaredField("nom");

  Que peut-on faire avec un Field ?

  Field f = c.getDeclaredField("age");

  f.getName();           // "age"
  f.getType();           // int.class ou Integer.class
  f.getModifiers();      // public, private, static...

  // Lire/écrire la valeur (sur une INSTANCE)
  Personne p = new Personne("Bob", 25);
  f.setAccessible(true);  // Si c'est private !
  int age = f.getInt(p);  // Lire la valeur
  f.setInt(p, 30);        // Modifier la valeur

  Les MÉTHODES (Method)

  // Toutes les méthodes publiques (locales + héritées)
  Method[] methodesPubliques = c.getMethods();

  // Toutes les méthodes locales (même private)
  Method[] toutesMethodes = c.getDeclaredMethods();

  // Une méthode spécifique (nom + types des paramètres)
  Method m = c.getMethod("setAge", int.class);

  Invoquer une méthode dynamiquement :

  Personne p = new Personne("Alice", 30);
  Method m = Personne.class.getMethod("getNom");

  // Équivalent de : p.getNom()
  String nom = (String) m.invoke(p);  // Retourne "Alice"

  // Avec paramètres
  Method setAge = Personne.class.getMethod("setAge", int.class);
  setAge.invoke(p, 35);  // Équivalent de : p.setAge(35)

  Les CONSTRUCTEURS (Constructor)

  Constructor<?>[] constructeurs = c.getConstructors();

  // Créer une instance SANS utiliser "new"
  Constructor<?> cons = c.getConstructor(String.class, int.class);
  Object instance = cons.newInstance("Charlie", 28);

  1.5 Les Modifiers

  Les champs/méthodes ont des modificateurs (public, private, static, final...). On les récupère avec getModifiers() :

  Field f = c.getDeclaredField("nom");
  int mods = f.getModifiers();

  Modifier.isPublic(mods);   // true/false
  Modifier.isPrivate(mods);  // true/false
  Modifier.isStatic(mods);   // true/false
  Modifier.isFinal(mods);    // true/false

  // Ou en chaîne
  String modsString = Modifier.toString(mods);  // "private static final"

  1.6 Accéder aux champs privés

  Par défaut, tu ne peux pas lire un champ private. Solution :

  Field f = c.getDeclaredField("champPrive");
  f.setAccessible(true);  // MAGIE ! On bypasse la protection
  Object valeur = f.get(monObjet);

  1.7 Exemple concret : JUnit

  JUnit utilise l'introspection pour trouver et exécuter les tests :

  // JUnit cherche toutes les méthodes qui commencent par "test"
  // ou qui ont l'annotation @Test
  for (Method m : classeTest.getDeclaredMethods()) {
      if (m.getName().startsWith("test")) {
          m.invoke(instanceTest);  // Exécute le test
      }
  }

  ---
  PARTIE 2 : ANNOTATIONS

  2.1 C'est quoi une annotation ?

  Une annotation = métadonnée attachée au code. C'est une "étiquette" qui donne des infos supplémentaires.

  @Override
  public String toString() { ... }

  ⚠️ Une annotation n'exécute RIEN par elle-même ! C'est juste de l'info. Un outil doit la lire et agir.

  2.2 Les 3 types d'annotations

  // 1. MARQUEUR - pas de paramètre
  @Override

  // 2. PARAMÉTRÉE - un seul paramètre
  @SuppressWarnings("unchecked")

  // 3. MULTI-PARAMÉTRÉE - plusieurs paramètres
  @Author(name = "Alice", date = "2024-01-01")

  2.3 Annotations du compilateur (java.lang)

  @Override

  Indique qu'une méthode redéfinit celle du parent. Le compilateur vérifie !

  public class Enfant extends Parent {
      @Override
      public void maMethode() { }  // Erreur si Parent n'a pas maMethode()
  }

  @Deprecated

  Marque quelque chose comme obsolète :

  @Deprecated
  public void ancienneMethode() { }  // Warning à l'utilisation

  @SuppressWarnings

  Supprime des avertissements du compilateur :

  @SuppressWarnings("deprecation")  // Ignore les warnings d'obsolescence
  public void utiliseVieilleAPI() {
      ancienneMethode();  // Pas de warning
  }

  @SuppressWarnings({"unchecked", "deprecation"})  // Plusieurs

  @FunctionalInterface

  Indique qu'une interface est "fonctionnelle" (une seule méthode abstraite) :

  @FunctionalInterface
  public interface MonAction {
      void execute();  // UNE seule méthode abstraite
  }

  2.4 Créer ses propres annotations

  Syntaxe de base

  public @interface MonAnnotation {
      String nom() default "inconnu";   // Attribut avec valeur par défaut
      int priorite() default 1;
      String[] tags();                   // Attribut obligatoire (pas de default)
  }

  Utilisation

  @MonAnnotation(nom = "test", priorite = 5, tags = {"dev", "urgent"})
  public void maMethode() { }

  @MonAnnotation(tags = {"simple"})  // nom et priorite utilisent les defaults
  public void autreMethode() { }

  2.5 Méta-annotations (annotations sur annotations)

  Ce sont des annotations qui configurent... d'autres annotations !

  @Target - Où peut-on l'utiliser ?

  @Target({ElementType.METHOD, ElementType.FIELD})
  public @interface MonAnnotation { }

  | ElementType     | S'applique à            |
  |-----------------|-------------------------|
  | TYPE            | Classe, interface, enum |
  | FIELD           | Attribut                |
  | METHOD          | Méthode                 |
  | PARAMETER       | Paramètre de méthode    |
  | CONSTRUCTOR     | Constructeur            |
  | LOCAL_VARIABLE  | Variable locale         |
  | ANNOTATION_TYPE | Autre annotation        |
  | PACKAGE         | Package                 |

  @Retention - Quand est-elle disponible ?

  @Retention(RetentionPolicy.RUNTIME)
  public @interface MonAnnotation { }

  | RetentionPolicy | Disponibilité                                       |
  |-----------------|-----------------------------------------------------|
  | SOURCE          | Code source uniquement (disparaît à la compilation) |
  | CLASS           | Fichier .class (mais pas à l'exécution)             |
  | RUNTIME         | À l'exécution (introspection possible) ✓            |

  ⚠️ Pour lire une annotation par introspection, il FAUT RUNTIME !

  @Documented

  L'annotation apparaît dans la Javadoc.

  @Inherited

  Les sous-classes héritent de l'annotation (niveau classe seulement).

  @Repeatable

  Permet de mettre plusieurs fois la même annotation :

  @Repeatable(Auteurs.class)
  public @interface Auteur { String nom(); }

  public @interface Auteurs { Auteur[] value(); }

  // Utilisation
  @Auteur(nom = "Alice")
  @Auteur(nom = "Bob")
  public class MonCode { }

  2.6 Lire les annotations par introspection

  Class<?> c = MaClasse.class;

  // Toutes les annotations de la classe
  Annotation[] annotations = c.getAnnotations();

  // Une annotation spécifique
  if (c.isAnnotationPresent(MonAnnotation.class)) {
      MonAnnotation a = c.getAnnotation(MonAnnotation.class);
      System.out.println(a.nom());  // Lire les valeurs
  }

  // Sur une méthode
  Method m = c.getMethod("maMethode");
  MonAnnotation a = m.getAnnotation(MonAnnotation.class);

  2.7 Exemple complet : Annotation de test

  // 1. Définir l'annotation
  @Retention(RetentionPolicy.RUNTIME)
  @Target(ElementType.METHOD)
  public @interface Test {
      boolean enabled() default true;
  }

  // 2. L'utiliser
  public class MesTests {
      @Test
      public void testAddition() { ... }

      @Test(enabled = false)
      public void testDesactive() { ... }
  }

  // 3. La lire et agir
  for (Method m : MesTests.class.getDeclaredMethods()) {
      Test t = m.getAnnotation(Test.class);
      if (t != null && t.enabled()) {
          m.invoke(new MesTests());  // Exécute le test
      }
  }

  2.8 Spring Framework (aperçu)

  Spring utilise massivement les annotations :

  @Component                    // "Je suis un composant géré par Spring"
  public class MonService {

      @Autowired                // "Injecte-moi une instance automatiquement"
      private AutreService autre;

      @Value("config.properties")  // "Lis cette valeur depuis la config"
      private String config;
  }

  @Configuration
  @ComponentScan("mon.package")  // "Scanne ce package pour trouver les @Component"
  public class MaConfig { }

  ---
  PARTIE 3 : SÉRIALISATION (Persistance)

  3.1 Le problème

  Quand ton programme s'arrête, tous les objets en mémoire disparaissent. Comment les sauvegarder ?

  Sérialisation = Transformer un objet en flux d'octets (pour fichier, réseau...)
  Désérialisation = Recréer l'objet à partir du flux

  Objet Java  →  [Sérialisation]  →  Fichier/Réseau
                                           ↓
  Objet Java  ←  [Désérialisation] ←───────┘

  3.2 Rendre une classe sérialisable

  C'est simple : implémenter l'interface Serializable (qui est vide !) :

  import java.io.Serializable;

  public class Etudiant implements Serializable {
      private String nom;
      private int age;

      // ... constructeurs, getters, setters
  }

  3.3 Sérialiser un objet

  Etudiant e = new Etudiant("Alice", 22);

  // Écrire dans un fichier
  try (ObjectOutputStream oos = new ObjectOutputStream(
          new FileOutputStream("etudiant.ser"))) {
      oos.writeObject(e);
  }

  3.4 Désérialiser un objet

  // Lire depuis le fichier
  try (ObjectInputStream ois = new ObjectInputStream(
          new FileInputStream("etudiant.ser"))) {
      Etudiant e = (Etudiant) ois.readObject();  // Cast nécessaire !
  }

  ⚠️ L'ordre de lecture = ordre d'écriture !

  3.5 Le mot-clé transient

  Certains champs ne doivent pas être sauvegardés (mot de passe, connexion réseau...) :

  public class Utilisateur implements Serializable {
      private String login;
      private transient String motDePasse;  // NE SERA PAS sérialisé
      private transient Connection connexionBD;  // NE SERA PAS sérialisé
  }

  Après désérialisation, les champs transient valent null (ou 0, false...).

  3.6 Les champs static

  Les champs static ne sont JAMAIS sérialisés (ils appartiennent à la classe, pas à l'instance).

  public class Compteur implements Serializable {
      private static int total = 0;  // Jamais sérialisé
      private int valeur;            // Sérialisé
  }

  3.7 serialVersionUID - Contrôle de version

  Problème : Tu sérialises un objet, puis tu modifies la classe, puis tu désérialises → ERREUR !

  Solution : Déclarer un numéro de version explicite :

  public class Etudiant implements Serializable {
      private static final long serialVersionUID = 1L;  // ← IMPORTANT !

      private String nom;
      private int age;
  }

  - Si tu ne le déclares pas, Java en génère un automatiquement basé sur la structure de la classe
  - Toute modification → nouveau numéro → InvalidClassException à la désérialisation
  - En le déclarant toi-même, tu contrôles quand incrémenter

  3.8 Gestion des cycles

  Java gère automatiquement les références circulaires :

  class A { B refB; }
  class B { A refA; }

  A a = new A();
  B b = new B();
  a.refB = b;
  b.refA = a;  // Cycle !

  // Java ne boucle pas à l'infini, il met des références internes

  3.9 Personnaliser la sérialisation

  Méthode 1 : writeObject / readObject

  public class Etudiant implements Serializable {
      private String nom;
      private transient String secret;  // On veut quand même le sauvegarder (chiffré)

      private void writeObject(ObjectOutputStream out) throws IOException {
          out.defaultWriteObject();  // Sérialise les champs normaux
          out.writeObject(encrypt(secret));  // Ajoute le secret chiffré
      }

      private void readObject(ObjectInputStream in)
              throws IOException, ClassNotFoundException {
          in.defaultReadObject();  // Désérialise les champs normaux
          secret = decrypt((String) in.readObject());  // Déchiffre le secret
      }
  }

  Méthode 2 : Interface Externalizable

  Contrôle TOTAL sur ce qui est sérialisé :

  public class Etudiant implements Externalizable {
      private String nom;
      private int age;

      public Etudiant() { }  // Constructeur par défaut OBLIGATOIRE !

      @Override
      public void writeExternal(ObjectOutput out) throws IOException {
          out.writeObject(nom);
          out.writeInt(age);
      }

      @Override
      public void readExternal(ObjectInput in)
              throws IOException, ClassNotFoundException {
          nom = (String) in.readObject();
          age = in.readInt();
      }
  }

  Méthode 3 : serialPersistentFields

  Lister explicitement les champs à sérialiser :

  public class Etudiant implements Serializable {
      private static final ObjectStreamField[] serialPersistentFields = {
          new ObjectStreamField("nom", String.class),
          new ObjectStreamField("age", int.class)
          // prenom n'est PAS listé → pas sérialisé
      };

      private String nom;
      private String prenom;
      private int age;
  }

  3.10 Héritage et sérialisation

  Cas 1 : Parent sérialisable
  class Parent implements Serializable { int x; }
  class Enfant extends Parent { int y; }
  // → x ET y sont sérialisés

  Cas 2 : Parent NON sérialisable
  class Parent { int x; }  // Pas Serializable
  class Enfant extends Parent implements Serializable { int y; }
  // → SEULEMENT y est sérialisé
  // → Parent DOIT avoir un constructeur par défaut !

  3.11 Exceptions principales

  | Exception                | Cause                                               |
  |--------------------------|-----------------------------------------------------|
  | NotSerializableException | Classe non sérialisable                             |
  | InvalidClassException    | serialVersionUID différent ou problème de structure |
  | StreamCorruptedException | Fichier corrompu                                    |
  | ClassNotFoundException   | Classe non trouvée à la désérialisation             |

  ---
  RÉSUMÉ EXPRESS (À RETENIR !)

  Introspection

  // Obtenir Class
  Class<?> c = objet.getClass();
  Class<?> c = MaClasse.class;
  Class<?> c = Class.forName("nom.complet.Classe");

  // Explorer
  Field[] champs = c.getDeclaredFields();
  Method[] methodes = c.getDeclaredMethods();
  Constructor[] constructeurs = c.getConstructors();

  // Utiliser
  field.setAccessible(true);  // Pour accéder au private
  Object val = field.get(instance);
  method.invoke(instance, args);
  Object o = constructor.newInstance(args);

  Annotations

  // Créer
  @Retention(RetentionPolicy.RUNTIME)
  @Target(ElementType.METHOD)
  public @interface MonAnnotation {
      String value() default "";
  }

  // Utiliser
  @MonAnnotation("test")
  public void maMethode() { }

  // Lire
  MonAnnotation a = method.getAnnotation(MonAnnotation.class);

  Sérialisation

  // Rendre sérialisable
  public class X implements Serializable {
      private static final long serialVersionUID = 1L;
      private transient String secret;  // Non sauvegardé
  }

  // Écrire
  ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream("f"));
  oos.writeObject(monObjet);

  // Lire
  ObjectInputStream ois = new ObjectInputStream(new FileInputStream("f"));
  MonType obj = (MonType) ois.readObject();

  ---
  Questions types d'examen

  1. Quelle est la différence entre getFields() et getDeclaredFields() ?
    - getFields() : champs publics (locaux + hérités)
    - getDeclaredFields() : tous les champs locaux (même private)
  2. Pourquoi utiliser setAccessible(true) ?
    - Pour accéder aux membres private par introspection
  3. Quelle RetentionPolicy pour lire une annotation à l'exécution ?
    - RUNTIME
  4. Que fait transient ?
    - Le champ n'est pas sérialisé
  5. Pourquoi déclarer serialVersionUID ?
    - Contrôler la compatibilité entre versions de la classe
  6. Différence Serializable vs Externalizable ?
    - Serializable : automatique, peu de contrôle
    - Externalizable : contrôle total, constructeur par défaut obligatoire

  ---
