
//////////////////////////////
// The Inspector            //
// Mock Application         //
// University of Colorado   //
// Fall 2006                //
//////////////////////////////

package vn;

import java.util.*;
import org.w3c.dom.*;

/**
 * This class defines the action to take upon encountering each element
 * in a VerbNet XML file.  The name Sweeper has no particular significance
 * other than to be memorable enough to be associated with this important task.
 * <BR><BR>
 * The {@link vn.Inspector} class, after it has processed all command-line
 * arguments, will begin reading in the requested XML files one-by-one.  After
 * loading and parsing each one, a recursive process is begun that executes
 * the methods in this class.  The appropriate method is called based solely
 * upon the tag name of the element being processed by use of reflection.  The
 * methods {@link vn.Inspector#processNode(Node)} or
 * {@link vn.Inspector#processNodeByPairs(Node, ArrayList)} recursively
 * traverse the XML nodes and call upon {@link vn.Inspector#executeHTMLMethod(String, Node)}
 * to execute the appropriate method in this class.
 * <BR><BR>
 * This class has multiple responsibilities.  They include:
 * <UL>
 *    <LI>Send to standard out simple text representations of VerbNet XML nodes, depending on view options</LI>
 *    <LI>Alphabetically sort the members of each class or subclass, if corresponding flag provided</LI>
 *    <LI>Output a class hierarchy of all VerbNet classes, if corresponding flag provided
 *    <LI>Fire events as elements are encountered</LI>
 *    <LI>Increment tag counters for class counts and final counts</LI>
 * </UL>
 * The implementation of this class is fairly intricate so that the
 * {@link vn.EventManager} class is as easy to use as possible for
 * researchers.  A researcher should never have to modify this code, but it
 * is provided openly so that doing so is available if necessary.
 * <BR><BR>
 * This file has also been as convenient as possible for future developers.
 * Since VerbNet is not a fixed entity (its structure and content can change
 * as work progresses on it), elements and attributes may be added to or removed from
 * the XML format.
 * <BR><BR>
 * If a new element is added to the XML files, one can simply
 * insert new methods named <CODE>startNODE</CODE> and <CODE>endNODE</CODE>
 * where <CODE>NODE</CODE> is the tag name of the new element.  They will be invoked when
 * the driver class ({@link vn.Inspector}) begins and ends processing the node,
 * respectively.  Just the act of inserting these methods, in the same manner as
 * the already-existing methods, makes them active since reflection is used.
 * <BR><BR>
 * If an attribute is added to or removed from an element, one can find the appropriate
 * <CODE>startNODE</CODE> or <CODE>endNODE</CODE> method and modfiy how the attributes
 * are used to construct the simple-text representation of the element.  All attributes
 * are stored into local String objects at the very beginning of each of the methods
 * (using the {@link org.w3c.dom.Element#getAttribute(String)} method).  Read the
 * specific documentation of each method below carefully to avoid invalid modifications.
 * <BR><BR>
 * Finally, a <I>sweeper method</I> has the general form:
 * <PRE> static void startNODE( Node n )
 * {
 *    // 1. Grab all attributes from the element (Node n).
 *    // 2. Construct local output string (simple-text representation) for this element.
 *    // 3. Initialize global event string to local output string or append local output
 *    //    string to global event string.
 *    // 4. If the proper view options are supplied for this element, display the
 *    //    local output string.
 *    // 5. If applicable, fire appropriate event(s)
 * }</PRE>
 *
 * The Inspector is ready for use <I>right out of the box</I>.  There is very
 * little to configure.  However, these notes (all of which shown on {@link vn.Inspector},
 * {@link vn.Sweeper}, and {@link vn.EventManager} classes) provide some more
 * logistical details about the software.
 *
 * <BR><BR><I>NOTE 1: The Inspector is implemented almost entirely with static methods.
 * Text parsing and scanning is a very serial process and the Inspector would
 * only have been made more complicated with a more object-oriented scheme.</I>
 *
 * <BR><BR><I>NOTE 2: The Inspector produces simple-text representations for <B>frame syntax</B>
 * which are congruent with the representations for frame syntax presented in the
 * <A href='http://verbs.colorado.edu/verb-index' target='_blank'>Unified Verb Index</A>.  The only difference
 * is that the UVI represents noun phrase thematic roles with underline
 * (<FONT style='text-decoration:underline;font-style:normal;font-variant:small-caps;'>Agent</FONT>) and
 * the Inspector represents them with a preceding % sign
 * (<CODE><FONT style='font-style:normal;'>%Agent</FONT></CODE>).  Look at the UVI's key or
 * the Inspector's key (-k option on command line) for more information.</I>
 *
 * <BR><BR><I>NOTE 3: Use of the Inspector, either by extension or by insertion into
 * an existing application, requires the entirety of the VerbNet XML files.  They may be
 * placed anywhere in relation to the Inspector source code, as the only required argument
 * to the Inspector is this XML input directory path.  They can be downloaded
 * <A href='http://verbs.colorado.edu/~mpalmer/projects/verbnet/downloads.html' target='_blank'>here</A>.
 * Finally, the DTD file contained in this download is required to be in the same
 * directory as the XML files (it's already there, just don't remove it).</I>
 *
 * <BR><BR><I>NOTE 4: This software assumes that the XML files it is processing match the VerbNet DTD.
 * This means that elements appear in the proper order (MEMBERS, THEMROLES, FRAMES, SUBCLASSES) and
 * all tag names are in upper case (i.e. &lt;FRAME>).  The files available for download should match
 * the DTD almost 100%.</I>
 *
 * <BR><BR><I>NOTE 5: This documentation utilizes the terms 'researcher' and
 * 'future developer' so as to reduce confusion as much as possible.  A researcher is
 * one who downloads the Inspector source code from the website with the intention
 * of extending it for his or her own purposes, or integrating it into an existing
 * NLP application.  A future developer is a member of the University of Colorado
 * team responsible for the Inspector who might modify or enhance it over time.
 * This documentation is written for both parties.</I>
 *
 * <BR><BR><I>NOTE 6: This Javadoc documentation is not written like a standard public API
 * might be written.  First, all private members are displayed here because this is also
 * made to be convenient documentation for future developers.  Second, all "See Also"
 * links below actually reference other places in the code that reference or are referenced
 * by the given member.  This is in contrast to public API documentation, in which the
 * "See Also" links commonly refer the reader to class members of related or contrasted
 * functionality.</I>
 *
 * <BR><BR><I>NOTE 7: Although originally written with a few Java 1.5 features, the Inspector
 * was downgraded so as to be compilable with <CODE>javac</CODE> 1.4.2.  The reason for this was so
 * researchers did not need to download and run Java 1.5 for this software.  This software
 * will however work with Java 1.5.  If you do not have Java installed on your system,
 * download the most recent release
 * <A href='http://java.sun.com/javase/downloads/index.jsp' target='_blank'>right here</A>.
 * Also, here are links to the <A href='http://java.sun.com/j2se/1.4.2/docs/api/' target='_blank'>1.4.2 documentation</A>
 * and the <A href='http://java.sun.com/j2se/1.5.0/docs/api/' target='_blank'>1.5.0 documentation</A>.</I>
 *
 * @author Derek Trumbo
 * @version 1.0, 2006.10.18
 */
public class Sweeper
{

   ////////////
   // Fields //
   ////////////

   // ---------------------------- //
   // -- Current File and Class -- //
   // ---------------------------- //

   /**
    * The name of the current XML file being processed.  This is set in the
    * {@link vn.Inspector#performInspection()} method, which calls
    * {@link vn.Sweeper#setCurFile(String)}.  This is used so that at
    * any point during the execution of the <I>sweeper methods</I>, the
    * currently-active file name is available for use.  It is
    * given to {@link vn.EventManager#fireEvent(int, int, String, String, String, Element, Element)}
    * upon firing of each event.
    *
    * @see vn.Inspector#performInspection()
    * @see vn.Sweeper#startVNCLASS(Node)
    */
   private static String curFile;

   /**
    * The name of the current class or subclass being processed.  This is
    * set when each new class or subclass is begun.  This is used so that at
    * any point during the execution of the <I>sweeper methods</I>, the
    * currently-active class or subclass name is available for use.   It is
    * given to
    * {@link vn.EventManager#fireEvent(int, int, String, String, String, Element, Element)}
    * upon firing of each event.
    *
    * @see vn.Sweeper#startVNCLASS(Node)
    * @see vn.Sweeper#startVNSUBCLASS(Node)
    */
   private static String curClass;

   // ---------------------------------------- //
   // -- General Inter-Method Communication -- //
   // ---------------------------------------- //

   /**
    * Used by various types of nodes for which there might be a list to
    * display to know if another of their same kind has already been
    * shown, so as to print the appropriate separator.
    *
    * @see vn.Sweeper#startSELRESTRS(Node)
    * @see vn.Sweeper#startSELRESTR(Node)
    * @see vn.Sweeper#startARGS(Node)
    * @see vn.Sweeper#startARG(Node)
    * @see vn.Sweeper#startSYNRESTRS(Node)
    * @see vn.Sweeper#startSYNRESTR(Node)
    */
   private static boolean hasBeenOther;

   /**
    * Whether or not nodes which specify logical operators for their
    * children are using 'or'.  This only happens with SELRESTRS
    * and SYNRESTRS.  When their children execute, they know whether to
    * print a | or an & before printing themselves.
    *
    * @see vn.Sweeper#startSELRESTRS(Node)
    * @see vn.Sweeper#startSELRESTR(Node)
    * @see vn.Sweeper#startSYNRESTRS(Node)
    * @see vn.Sweeper#startSYNRESTR(Node)
    */
   private static boolean usingOr;

   // ------------------------------ //
   // -- Selectional Restrictions -- //
   // ------------------------------ //

   /**
    * The level of nested SELRESTRS being processed.  The definition of SELRESTRS
    * is recursive in the DTD (&lt;!ELEMENT SELRESTRS (SELRESTR|SELRESTRS)*&gt;)
    * and a | or an & should be printed if it's not the top-level element.
    * Currently, this only happens in a few files:  bring-11.3.html, carry-11.4.html,
    * cheat-10.6.html, drive-11.5.html, pour-9.5.html, send-11.1.html, slide-11.2.html,
    * spray-9.7.html, steal-10.5.html, throw-17.1.html.
    *
    * @see vn.Sweeper#startSELRESTRS(Node)
    * @see vn.Sweeper#endSELRESTRS(Node)
    */
   private static int restrsLevel;

   /**
    * Whether or not the SELRESTRS about to be entered is under a PREP node
    * (as compared to a THEMROLE or NP node).  This is modified upon entering and
    * leaving a PREP element.  SELRESTRS for a preposition are displayed differently
    * than other uses of SELRESTRS.
    *
    * @see vn.Sweeper#startPREP(Node)
    * @see vn.Sweeper#endPREP(Node)
    * @see vn.Sweeper#startSELRESTRS(Node)
    * @see vn.Sweeper#endSELRESTRS(Node)
    * @see vn.Sweeper#startSELRESTR(Node)
    * @see vn.Sweeper#endSELRESTR(Node)
    */
   private static boolean prepSelRestrs;

   /**
    * Whether or not the SELRESTRS about to be entered is under a THEMROLE node
    * (as compared to a PREP or NP node).  This is modified upon entering and
    * leaving a THEMROLE element.  SELRESTRS for thematic roles are displayed
    * much like those for noun phrases (NP).
    *
    * @see vn.Sweeper#startTHEMROLE(Node)
    * @see vn.Sweeper#endTHEMROLE(Node)
    * @see vn.Sweeper#startSELRESTRS(Node)
    * @see vn.Sweeper#endSELRESTRS(Node)
    * @see vn.Sweeper#startSELRESTR(Node)
    * @see vn.Sweeper#endSELRESTR(Node)
    */
   private static boolean trSelRestrs;

   /**
    * Whether or not the SELRESTRS about to be entered is under an NP node
    * (as compared to a PREP or THEMROLE node).  This is modified upon entering and
    * leaving a NP element.  SELRESTRS for noun phrases are displayed
    * much like those for thematic roles.
    *
    * @see vn.Sweeper#startNP(Node)
    * @see vn.Sweeper#endNP(Node)
    * @see vn.Sweeper#startSELRESTRS(Node)
    * @see vn.Sweeper#endSELRESTRS(Node)
    * @see vn.Sweeper#startSELRESTR(Node)
    * @see vn.Sweeper#endSELRESTR(Node)
    */
   private static boolean npSelRestrs;

   // ------------------ //
   // -- Members List -- //
   // ------------------ //

   /**
    * Holds all the member information for a given class or subclass.  Information
    * for a single member consists of the verb, its list of WordNet senses and
    * the XML MEMBER node from which that information was extracted.
    * It is cleared at the start of each class or subclass, loaded up during the
    * &lt;MEMBER> tag scanning, and sorted and dumped upon reaching the &lt;/MEMBERS>
    * tag.  This was only added to facilitate sorted member sections.  If sorting
    * was not a priority, then members would just be printed as they were
    * reached.  If verb-frame pairs are enabled, then the members are not printed
    * in &lt;/MEMBERS> but rather printed in a pair with each frame in
    * {@link vn.Sweeper#printVerbFramePairs()}.
    *
    * @see vn.Sweeper#startMEMBERS(Node)
    * @see vn.Sweeper#startMEMBER(Node)
    * @see vn.Sweeper#printMembers()
    * @see vn.Sweeper#printVerbFramePairs()
    */
   private static ArrayList members = new ArrayList();

   /**
    * Holds all crucial information about a member when it is encountered
    * so it can be properly displayed in later processing.  This is
    * a simple information holder class.
    *
    * @see vn.Sweeper#startMEMBER(Node)
    * @see vn.Sweeper#printVerbFramePairs()
    */
   private static class MemberNode
   {

      /**
       * The verb.  This is extracted from the 'name' attribute of the
       * MEMBER element.
       */
      public String verb;

      /**
       * The WordNet sense.  This is extracted from the 'wn' attribute of the
       * MEMBER element.
       */
      public String wn;

      /**
       * The XML node.  This is the MEMBER element.
       */
      public Node node;

      /**
       * Constructs a {@link vn.Sweeper.MemberNode} object.
       *
       * @param v the verb
       * @param w the WordNet sense
       * @param n the XML node
       * @see vn.Sweeper#startMEMBER(Node)
       */
      public MemberNode( String v, String w, Node n )
      {
         verb = v;
         wn   = w;
         node = n;
      }
   }

   // ----------------- //
   // -- Indentation -- //
   // ----------------- //

   /**
    * The number of spaces for a single indentation width.
    */
   private static final int INDENT_WIDTH = 3;

   /**
    * A string consisting of {@link vn.Sweeper#INDENT_WIDTH} spaces.  This
    * is set in the static initializer for this class and used when
    * the indentation flag (-i) is specified.
    *
    * @see vn.Sweeper#iprint(String)
    * @see vn.Sweeper#iprintln(String)
    * @see vn.Sweeper#classHierarchyPrint(Element, int)
    */
   private static String indentSpaces;

   /**
    * Represents how many levels of indentation should be printed
    * when output is printed to stdout.  This variable is modified
    * regardless of whether the indentation flag (-i) is specified.
    * The {@link vn.Sweeper#iprint(String)} and {@link vn.Sweeper#iprintln(String)}
    * methods control whether the actual indentation is performed.
    * Indentation level is changed only by FILE, CLASS, SUBCLASS, and FRAME.
    *
    * @see vn.Sweeper#iprint(String)
    * @see vn.Sweeper#iprintln(String)
    * @see vn.Sweeper#startVNCLASS(Node)
    * @see vn.Sweeper#endVNCLASS(Node)
    * @see vn.Sweeper#startVNSUBCLASS(Node)
    * @see vn.Sweeper#endVNSUBCLASS(Node)
    * @see vn.Sweeper#startFRAME(Node)
    * @see vn.Sweeper#endFRAME(Node)
    */
   private static int curIndentLevel;

   // ---------------------------------- //
   // -- Verb-Frame Pair Coordination -- //
   // ---------------------------------- //

   /**
    * The verb corresponding to the current verb-frame pair (used
    * only when the Inspector is running in verb-frame pair mode).
    * This needs to be class-level so the {@link vn.Sweeper#printVerbFramePairs()}
    * method can communicate information to {@link vn.Sweeper#startDESCRIPTION(Node)}
    * This string is used in constructing the header line for
    * the verb-frame pair.
    *
    * @see vn.Sweeper#startDESCRIPTION(Node)
    * @see vn.Sweeper#printVerbFramePairs()
    */
   private static String curVFVerbName;

   /**
    * The WordNet sense corresponding to the current verb-frame pair (used
    * only when the Inspector is running in verb-frame pair mode).
    * This needs to be class-level so the {@link vn.Sweeper#printVerbFramePairs()}
    * method can communicate information to {@link vn.Sweeper#startDESCRIPTION(Node)}.
    * This string is used in constructing the header line for
    * the verb-frame pair.
    *
    * @see vn.Sweeper#startDESCRIPTION(Node)
    * @see vn.Sweeper#printVerbFramePairs()
    */
   private static String curVFVerbWN;

   /**
    * The XML MEMBER node corresponding to the current verb-frame pair (used
    * only when the Inspector is running in verb-frame pair mode).
    * This needs to be class-level so the {@link vn.Sweeper#printVerbFramePairs()}
    * method can communicate information to {@link vn.Sweeper#startDESCRIPTION(Node)}.
    * This node is used when firing the 'start' and 'end' events
    * for the verb-frame pair.
    *
    * @see vn.Sweeper#startDESCRIPTION(Node)
    * @see vn.Sweeper#endFRAME(Node)
    * @see vn.Sweeper#printVerbFramePairs()
    * @see vn.EventManager#fireEvent(int, int, String, String, String, Element, Element)
    */
   private static Node curVFMemberNode;

   /**
    * The XML FRAME node corresponding to the current verb-frame pair (used
    * only when the Inspector is running in verb-frame pair mode).
    * This needs to be class-level so the {@link vn.Sweeper#printVerbFramePairs()}
    * method can communicate information to {@link vn.Sweeper#startDESCRIPTION(Node)}.
    * This node is used when firing the 'start' and 'end' events
    * for the verb-frame pair.
    *
    * @see vn.Sweeper#startDESCRIPTION(Node)
    * @see vn.Sweeper#endFRAME(Node)
    * @see vn.Sweeper#printVerbFramePairs()
    * @see vn.EventManager#fireEvent(int, int, String, String, String, Element, Element)
    */
   private static Node curVFFrameNode;

   /**
    * All the frames visited so far since the main (root) class.  Or at least
    * that's the description used throughout this documentation.  What does this mean though?
    * A verb in VerbNet is involved in not only the frames in its class or subclass,
    * but also all those frames in the ancestor classes or subclasses (using tree terminology).
    * Therefore, if we take the separate-23.1 class:
    * <PRE> separate-23.1 [Members: 4, Frames: 5]
    *     separate-23.1-1 [Members: 7, Frames: 1]
    *     separate-23.1-2 [Members: 4, Frames: 1]</PRE>
    * When the Sweeper is scanning the main class's verb-frame pairs there are <U>4 members x 5 frames
    * = 20 verb-frame pairs</U> in <CODE>curVFFrameNode</CODE>.  When the Sweeper is scanning the first subclass's verb-frame pairs
    * there are <U>7 members x (5+1) frames = 42 verb-frame pairs</U> in <CODE>curVFFrameNode</CODE>.  When the Sweeper is scanning
    * the second subclass's verb-frame pairs there are <U>4 members x (5+1) frames = 24 verb-frame
    * pairs</U> in <CODE>curVFFrameNode</CODE>.  A subclass does not inherit frames from a sibling
    * class, only ancestor classes.  This array is loaded up in {@link vn.Inspector#processNodeByPairs(Node, ArrayList)}.
    * Remember that this member and all verb-frame-pair-related members are only used by the code if
    * the -q or -Vq options are specified.
    *
    * @see vn.Sweeper#printVerbFramePairs()
    * @see vn.Sweeper#setFrameList(ArrayList)
    * @see vn.Inspector#processNodeByPairs(Node, ArrayList)
    */
   private static ArrayList curVFFrameList;

   // ----------------------- //
   // -- Event Information -- //
   // ----------------------- //

   /**
    * The string which is given to
    * {@link vn.EventManager#fireEvent(int, int, String, String, String, Element, Element)}
    * when events are fired.  This string does not necessarily equal
    * the line of text that is sent to stdout for the given element.
    * What is displayed on stdout is controlled by view options (-V operator)
    * but this string contains as much text for the line as is
    * available in the XML files for that element.  In other words
    * this string is the same as the lines of text send to stdout for ALL
    * elements if and only if the option <CODE>-Vab</CODE> were supplied (which prints
    * all information from the XML files to stdout).
    *
    *
    * @see vn.Sweeper#pushText()
    * @see vn.Sweeper#popText()
    * @see vn.EventManager
    * @see vn.EventManager#fireEvent(int, int, String, String, String, Element, Element)
    */
   private static String evText;

   /**
    * The string which contains the characters that each sweeper
    * method will output locally.  This was promoted to a class-level
    * variable only for convenience so it wouldn't have to be
    * declared in every sweeper method.  Sometimes there are other
    * intermediate strings that are used until the final value
    * for this variable is known.  Then, usually it is appended
    * to {@link vn.Sweeper#evText} or {@link vn.Sweeper#evText}
    * is initialized to it (in cases where the method in question
    * prints the first characters for a line of text).
    *
    * @see vn.Sweeper#evText
    */
   private static String evTextLocal;

   /**
    * A stack of strings which holds the global event string
    * for various elements which was created for their 'start' events
    * until their 'end' events come around.
    *
    * @see vn.Sweeper#pushText()
    * @see vn.Sweeper#popText()
    */
   private static Stack evTexts = new Stack();

   // ---------------------- //
   // -- Replicate Option -- //
   // ---------------------- //

   /**
    * A stack of strings which holds the labels for all printed
    * elements that have caused additional nesting (file,
    * class, subclass, and frame).  So at any given time
    * this stack contains at most one file label, one class label,
    * a handful of subclass labels, and one frame label (that
    * scenario would be for when an example, syntax, or semantic
    * predicate was being printed in a class with multiple
    * subclasses and most view options enabled with the replicate
    * flag supplied).  Applies to replicate flag only.
    *
    * @see vn.Sweeper#pushTextForReplicate(String)
    * @see vn.Sweeper#popTextForReplicate()
    * @see vn.Sweeper#replicateLabels()
    */
   private static Stack replicateLabels = new Stack();

   ////////////////////////
   // Static Initializer //
   ////////////////////////

   /**
    * This static initializer is used only to set up the string which
    * a single indentation level's worth of spaces.  This code is
    * executed when this class is loaded by the JVM, or at the very
    * beginning of the program essentially.
    */
   static
   {
      indentSpaces = "";

      for( int i = 0; i < INDENT_WIDTH; i++ )
         indentSpaces += " ";
   }

   /////////////////
   // Constructor //
   /////////////////

   /**
    * This constructor is private because the class is not intended to ever
    * be instantiated.  The Inspector is a very procedural process and
    * thus all the members are static.
    */
   private Sweeper() {}

   ////////////////////
   // Helper Methods //
   ////////////////////

   /**
    * Used as shorthand for <CODE>System.out.println</CODE>.
    *
    * @param s the string to print to stdout, followed by a carriage return
    * @see     java.io.PrintStream#println(String)
    */
   private static void println( String s ) { System.out.println( s ); }

   /**
    * Used as shorthand for <CODE>System.out.print</CODE>.
    *
    * @param s the string to print to stdout
    * @see     java.io.PrintStream#print(String)
    */
   private static void print( String s ) { System.out.print( s ); }

   /**
    * Does the exact same thing as {@link vn.Sweeper#println(String)} if the indentation
    * flag (-i) was not supplied on the command line (and thus
    * {@link vn.Inspector#flIndent} is <CODE>false</CODE>).  However,
    * if indentation was requested, then this method first prints
    * the appropriate number of spaces based on the current indentation level.
    * Indentation level is changed only by FILE, CLASS, SUBCLASS, and FRAME.
    *
    * @param s the string to print to stdout, with possible indenting, followed
    *          by a carriage return
    * @see vn.Sweeper#println(String)
    * @see vn.Sweeper#curIndentLevel
    * @see vn.Inspector#flIndent
    */
   private static void iprintln( String s )
   {
      if( Inspector.flIndent )
         for( int c = 0; c < curIndentLevel; c++ )
            print( indentSpaces );

      println( s );
   }

   /**
    * Does the exact same thing as {@link vn.Sweeper#print(String)} if the indentation
    * flag (-i) was not supplied on the command line (and thus
    * {@link vn.Inspector#flIndent} is <CODE>false</CODE>).  However,
    * if indentation was requested, then this method first prints
    * the appropriate number of spaces based on the current indentation level.
    * Indentation level is changed only by FILE, CLASS, SUBCLASS, and FRAME.
    *
    * @param s the string to print to stdout, with possible indenting
    * @see vn.Sweeper#print(String)
    * @see vn.Sweeper#curIndentLevel
    * @see vn.Inspector#flIndent
    */
   private static void iprint( String s )
   {
      if( Inspector.flIndent )
         for( int c = 0; c < curIndentLevel; c++ )
            print( indentSpaces );

      print( s );
   }

   /**
    * Sets the current file being processed.  It is primarily used
    * when firing events.
    *
    * @param newFileName the current file being processed in
    *        {@link vn.Inspector#performInspection()}
    * @see vn.Inspector#performInspection()
    * @see vn.Sweeper#curFile
    */
   static void setCurFile( String newFileName )
   {
      curFile = newFileName;
   }

   /**
    * Sets a class-level reference to a list containing all the frames
    * visited so far since the main (root) class.  This is set each
    * time a new class or subclass is reached in the driver class's
    * recursive XML traversal method ({@link vn.Inspector#processNodeByPairs(Node, ArrayList)}).
    * This is only used when the Inspector is running in verb-frame
    * pair mode.
    *
    * @param newFrameList the list containing all of the frames
    *        visited so far since the main (root) class
    * @see vn.Inspector#processNodeByPairs(Node, ArrayList)
    * @see vn.Sweeper#printVerbFramePairs()
    * @see vn.Sweeper#curVFFrameList
    */
   static void setFrameList( ArrayList newFrameList )
   {
      curVFFrameList = newFrameList;
   }

   /**
    * Whether or not the given XML element has children with a given
    * tag name.
    *
    * @param n the node whose children should be checked
    * @param which the tag name to look for among the children
    * @return whether or not the node contains one or more children of
    *         the given type
    */
   private static boolean hasKids( Node n, String which )
   {
      return numKids( n, which ) != 0;
   }

   /**
    * Counts the number of children of a given XML element who have
    * the given tag name.
    *
    * @param n the node whose children should be checked
    * @param which the tag name to look for among the children
    * @return the number of children of the given type that
    *         the node contains
    */
   private static int numKids( Node n, String which )
   {
      NodeList kids = n.getChildNodes();

      int whichKid = 0;

      for( int k = 0; k < kids.getLength(); k++ )
      {
         Node kid = ( Node ) kids.item( k );

         if( kid.getNodeName().equals( which ) )
            whichKid++;
      }

      return whichKid;
   }

   /**
    * Saves the class-level global event string to a stack of event strings.
    * This is required because the 'end' event for all elements contains
    * the same event text as the 'start' events.  Since all the elements
    * use the same class-level global event string, this text needs to be
    * saved for the 'end' events of certain elements.  These elements are:
    * FILE, CLASS, SUBCLASS, and FRAME.
    *
    * @see vn.Sweeper#classHierarchyPrint(Element, int)
    * @see vn.Sweeper#startVNCLASS(Node)
    * @see vn.Sweeper#startVNSUBCLASS(Node)
    * @see vn.Sweeper#startDESCRIPTION(Node)
    * @see vn.Sweeper#popText()
    * @see vn.Sweeper#evTexts
    */
   private static void pushText()
   {
      evTexts.push( evText );
   }

   /**
    * Removes a string from the global event string stack and places
    * it into the class-level global event string.  This is so
    * an element which had previously saved this string from
    * its 'start' event, could use it again for its end event.
    *
    * @see vn.Sweeper#classHierarchyPrint(Element, int)
    * @see vn.Sweeper#endVNCLASS(Node)
    * @see vn.Sweeper#endVNSUBCLASS(Node)
    * @see vn.Sweeper#endFRAME(Node)
    * @see vn.Sweeper#pushText()
    * @see vn.Sweeper#evTexts
    */
   private static void popText()
   {
      evText = ( String ) evTexts.pop();
   }

   /**
    * Saves the text for a label to be replicated for
    * all elements contained within it.
    * Applies to replicate flag only.
    *
    * @see vn.Sweeper#startVNCLASS(Node)
    * @see vn.Sweeper#startVNSUBCLASS(Node)
    * @see vn.Sweeper#startDESCRIPTION(Node)
    * @see vn.Sweeper#popTextForReplicate()
    * @see vn.Sweeper#replicateLabels
    */
   private static void pushTextForReplicate( String text )
   {
      replicateLabels.push( text );
   }

   /**
    * Removes the most recently stored label text for
    * replication.  This method is called whenever a
    * an element which causes nesting closes (i.e.&nbsp;when
    * a file, class, subclass, or frame ends).
    * Applies to replicate flag only.
    *
    * @see vn.Sweeper#endVNCLASS(Node)
    * @see vn.Sweeper#endVNSUBCLASS(Node)
    * @see vn.Sweeper#endFRAME(Node)
    * @see vn.Sweeper#pushTextForReplicate(String)
    * @see vn.Sweeper#replicateLabels
    */
   private static void popTextForReplicate()
   {
      replicateLabels.pop();
   }

   /**
    * Prints all the labels currently stored for replication.
    * The labels printed will be any file, class, subclass,
    * and frame elements that have already been printed
    * due to the appropriate view options being set.  This
    * method is called for all printable elements besides
    * file (because nothing would be in this stack).  For example,
    * the -r flag will not produce any additional output for
    * the view options -Vm.  However, when the -r flag is applied
    * to -Vcm, each member is preceded by all classes and subclasses
    * in which it is contained.
    * Applies to replicate flag only.
    *
    * @see vn.Inspector#flReplicate
    */
   private static void replicateLabels()
   {
      curIndentLevel = 0;     // Start the indentation level back at the left side.
                              // It will be incremented back to the right value.

      for( int s = 0; s < replicateLabels.size(); s++, curIndentLevel++ )
         iprintln( ( String ) replicateLabels.get( s ) );
   }

   /////////////////////
   // Class Hierarchy //
   /////////////////////

   /**
    * Prints name of the class element provided and the names of all subclass
    * elements contained within, joint with the number of members and frames for each.
    * This method is recursive and it is first called by {@link vn.Sweeper#startVNCLASS(Node)}
    * which is provided the document root Element object by {@link vn.Inspector#processNode(Node)}.
    * This method is only called when the class hierarchy option (-c) is provided.
    * The view operator (-V) is ignored and class counts (-m) are not honored.
    *
    * @param cls the XML {@link org.w3c.dom.Element} object representing a class or subclass
    * @param level the depth of the class or subclass (0 represents the main class in file)
    * @see vn.Sweeper#startVNCLASS(Node)
    * @see vn.Inspector#incrementTagCounter(String)
    * @see vn.Inspector#incrementTagCounter(String, int)
    */
   private static void classHierarchyPrint( Element cls, int level )
   {
      String indent = "";
      boolean hasSubclasses = false;

      // Save the current class or subclass name.
      curClass = cls.getAttribute( "ID" );

      // If the indentation flag was provided, add the proper number of
      // spaces to the total indent, depending on the depth of this subclass.
      // See the static initializer above for more information on 'indentSpaces'.
      if( Inspector.flIndent )
         for( int l = 0; l < level; l++ )
            indent += indentSpaces;

      // Increment the counter for this class or subclass.
      if( level == 0 )
         Inspector.incrementTagCounter( "CLASS" );

      else
         Inspector.incrementTagCounter( "SUBCLASS" );

      // Count the number of members and frames for this class or subclass only
      // (don't include members and frames of subclasses).
      int m = numKids( cls.getElementsByTagName( "MEMBERS" ).item( 0 ), "MEMBER" );
      int f = numKids( cls.getElementsByTagName( "FRAMES" ).item( 0 ),  "FRAME" );

      // Increment the counters for the members and frames of this class or subclass.
      Inspector.incrementTagCounter( "MEMBER", m );
      Inspector.incrementTagCounter( "FRAME",  f );

      // Construct count string.
      String counts = " [mem " + m + ", fr " + f + "]";

      // Construct local output string (simple-text representation) for this class or subclass.
      evTextLocal = curClass + counts;

      // Print the local output string for this class or subclass with
      // indentation, if appropriate flag provided.
      println( indent + evTextLocal );

      evText = evTextLocal;

      // Fire either the class start event or the subclass start event.
      if( level == 0 )
         EventManager.fireEventMaybe( EventManager.EVENT_CLASS, EventManager.EVENT_START, curFile, curClass, evText, cls, null );
      else
         EventManager.fireEventMaybe( EventManager.EVENT_SUBCLASS, EventManager.EVENT_START, curFile, curClass, evText, cls, null );

      // Add this global event string to a stack for retrieval when the 'end'
      // event fires for this element (the 'end' event has the same event text
      // as the 'start' event for every element).
      pushText();

      // Get all the child nodes for this class or subclass.
      NodeList kids = cls.getChildNodes();

      // Recursively print the links for this class's subclasses.
      for( int k = 0; k < kids.getLength(); k++ )
      {
         Node kid = ( Node ) kids.item( k );
         String nodeName = kid.getNodeName();

         // If this node is the subclasses section of the class...
         if( nodeName.equalsIgnoreCase( "SUBCLASSES" ) )
         {
            Element scls = ( Element ) kid;
            NodeList skids = scls.getChildNodes();

            // Look for some subclasses in the subclass section.
            for( int j = 0; j < skids.getLength(); j++ )
            {
               Node skid = ( Node ) skids.item( j );
               String sNodeName = skid.getNodeName();

               // If this node is a subclass, recursively print its label.
               if( sNodeName.equalsIgnoreCase( "VNSUBCLASS" ) )
               {
                  Element newCls = ( Element ) skid;

                  classHierarchyPrint( newCls, level + 1 );

                  hasSubclasses = true;         // There exists at least one subclass for this class.
               }
            }
         }
      }

      // Show if there are no subclasses for the main class.
      if( !Inspector.flNoAbsence && level == 0 && !hasSubclasses )
         if( Inspector.flIndent )
            println( indentSpaces + "<NO SUBCLASSES>" );

         else
            println( "<NO SUBCLASSES>" );

      // Retrieve the global event string for this element that was previously
      // saved to a stack.  This method sets the class-level variable evText.
      popText();

      // Fire either the class end event or the subclass end event.
      if( level == 0 )
         EventManager.fireEventMaybe( EventManager.EVENT_CLASS, EventManager.EVENT_END, curFile, curClass, evText, cls, null );
      else
         EventManager.fireEventMaybe( EventManager.EVENT_SUBCLASS, EventManager.EVENT_END, curFile, curClass, evText, cls, null );
   }

   /////////////////////
   // Sweeper Methods //
   /////////////////////

   // ------------------------------ //
   // -- Class/Subclass Elements  -- //
   // ------------------------------ //

   /**
    * Prints the text that corresponds to the beginning of the VNCLASS
    * element in the VerbNet XML files.  The global event string will
    * be initialized to this text in preparation for the events that
    * fire for the VNCLASS element.  As there is exactly one main class
    * (VNCLASS) per file, this method also handles FILE actions.
    * Starting events for both FILE and the VNCLASS element are handled here.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active VNCLASS element
    * @see vn.Sweeper#iprintln(String)
    * @see vn.Inspector#incrementTagCounter(String)
    */
   static void startVNCLASS( Node n )
   {
      curClass = ( ( Element ) n ).getAttribute( "ID" );

      // One counter per CLASS AND SUBCLASS.  Clear previous counts.
      Inspector.clearClassTagCounter();

      if( Inspector.flClassH )
      {
         classHierarchyPrint( ( Element ) n, 0 );
         return;
      }

      curIndentLevel = 0;

      // Construct local output string (simple-text representation) for this file
      evTextLocal = "FILE: " + curFile;

      // Initialize the global event string to the local output string since this
      // is the first text to display on the line.
      evText = evTextLocal;

      if( Inspector.voFileName )
      {

         // Save the text that will be printed for this element
         // for possible replication.
         pushTextForReplicate( evTextLocal );

         // Print the local output string with proper indentation.
         iprintln( evTextLocal );

         // Since the FILE label is one which indents all elements under it,
         // increase the indentation level so that if indentation is enabled
         // (via appropriate flag), iprint & iprintln will indent text given to them.
         curIndentLevel++;

         // Increment the counter for this file.
         Inspector.incrementTagCounter( "FILE" );
      }

      EventManager.fireEventMaybe( EventManager.EVENT_FILE, EventManager.EVENT_START, curFile, null, evText, null, null );

      // Add this global event string to a stack for retrieval when the 'end'
      // event fires for this element (the 'end' event has the same event text
      // as the 'start' event for every element).
      pushText();

      // Count the number of members and frames for this class or subclass only
      // (don't include members and frames of subclasses).
      int m = numKids( ( ( Element ) n ).getElementsByTagName( "MEMBERS" ).item( 0 ), "MEMBER" );
      int f = numKids( ( ( Element ) n ).getElementsByTagName( "FRAMES" ).item( 0 ),  "FRAME" );

      // Construct the counts string.
      String counts = " [Members: " + m + ", Frames: " + f + "]";

      // Construct the full text to be used for the VNCLASS events.
      String fullText = "CLASS: " + curClass + counts;

      // Construct local output string (simple-text representation) for this element.
      if( Inspector.voCount )
         evTextLocal = fullText;
      else
         evTextLocal = "CLASS: " + curClass;

      // Initialize the global event string to the local output string since this
      // is the first text to display on the line.
      evText = fullText;

      if( Inspector.voClassName )
      {

         // Reprint labels for all files, classes, subclasses, and frames in which
         // this class is contained.
         if( Inspector.flReplicate )
            replicateLabels();

         // Save the text that will be printed for this element
         // for possible replication.
         pushTextForReplicate( evTextLocal );

         // Print the local output string with proper indentation.
         iprintln( evTextLocal );

         // Since the CLASS element is one which indents all elements under it,
         // increase the indentation level so that if indentation is enabled
         // (via appropriate flag), iprint & iprintln will indent text given to them.
         curIndentLevel++;

         // Increment the counter for this element.
         Inspector.incrementTagCounter( "CLASS" );
      }

      EventManager.fireEventMaybe( EventManager.EVENT_CLASS, EventManager.EVENT_START, curFile, curClass, evText, n, null );

      // Add this global event string to a stack for retrieval when the 'end'
      // event fires for this element (the 'end' event has the same event text
      // as the 'start' event for every element).
      pushText();
   }

   /**
    * Prints the text that corresponds to the closing of the VNCLASS
    * element in the VerbNet XML files.  No additional text needs to be
    * printed here.  However, as there is exactly one main class
    * (VNCLASS) per file, this method also handles FILE actions.
    * Ending events for both FILE and the VNCLASS element are handled here.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active VNCLASS element
    */
   static void endVNCLASS( Node n )
   {

      // If the proper view options were supplied, display the text
      // for the closing of this element.  Although there is no text
      // to display in this method, the indentation level must now be
      // decreased.
      if( Inspector.voClassName )
      {

         // Remove this element's text from the replication stack
         // now that it's ending.
         popTextForReplicate();

         curIndentLevel--;
      }

      // Retrieve the global event string for this element that was previously
      // saved to a stack.  This method sets the class-level variable evText.
      popText();

      EventManager.fireEventMaybe( EventManager.EVENT_CLASS, EventManager.EVENT_END, curFile, curClass, evText, n, null );

      // If the proper view options were supplied, display the text
      // for the closing of a file.  Although there is no text
      // to display in this method, the indentation level must now be
      // decreased.
      if( Inspector.voFileName )
      {

         // Remove this element's text from the replication stack
         // now that it's ending.
         popTextForReplicate();

         curIndentLevel--;
      }

      // Retrieve the global event string for this element that was previously
      // saved to a stack.  This method sets the class-level variable evText.
      popText();

      EventManager.fireEventMaybe( EventManager.EVENT_FILE, EventManager.EVENT_END, curFile, null, evText, null, null );
   }

   /**
    * Prints the text that corresponds to the beginning of the VNSUBCLASS
    * element in the VerbNet XML files.  The global event string will
    * be initialized to this text in preparation for the events that
    * fire for the VNSUBCLASS element.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active VNSUBCLASS element
    * @see vn.Sweeper#iprintln(String)
    * @see vn.Inspector#incrementTagCounter(String)
    */
   static void startVNSUBCLASS( Node n )
   {
      curClass = ( ( Element ) n ).getAttribute( "ID" );

      // One counter per CLASS AND SUBCLASS.  Clear previous counts.
      Inspector.clearClassTagCounter();

      // Count the number of members and frames for this class or subclass only
      // (don't include members and frames of subclasses).
      int m = numKids( ( ( Element ) n ).getElementsByTagName( "MEMBERS" ).item( 0 ), "MEMBER" );
      int f = numKids( ( ( Element ) n ).getElementsByTagName( "FRAMES" ).item( 0 ),  "FRAME" );

      // Construct the counts string.
      String counts = " [Members: " + m + ", Frames: " + f + "]";

      // Construct the full text to be used for the VNCLASS events.
      String fullText = "SUBCLASS: " + curClass + counts;

      // Construct local output string (simple-text representation) for this element.
      if( Inspector.voCount )
         evTextLocal = fullText;
      else
         evTextLocal = "SUBCLASS: " + curClass;

      // Initialize the global event string to the local output string since this
      // is the first text to display on the line.
      evText = fullText;

      // If the proper view options were supplied, display the text
      // for the beginning of this element (the local output string).
      if( Inspector.voClassName )
      {

         // Reprint labels for all files, classes, subclasses, and frames in which
         // this subclass is contained.
         if( Inspector.flReplicate )
            replicateLabels();

         // Save the text that will be printed for this element
         // for possible replication.
         pushTextForReplicate( evTextLocal );

         // Print the local output string with proper indentation.
         iprintln( evTextLocal );

         // Since the SUBCLASS element is one which indents all elements under it,
         // increase the indentation level so that if indentation is enabled
         // (via appropriate flag), iprint & iprintln will indent text given to them.
         curIndentLevel++;

         // Increment the counter for this element.
         Inspector.incrementTagCounter( "SUBCLASS" );
      }

      EventManager.fireEventMaybe( EventManager.EVENT_SUBCLASS, EventManager.EVENT_START, curFile, curClass, evText, n, null );

      // Add this global event string to a stack for retrieval when the 'end'
      // event fires for this element (the 'end' event has the same event text
      // as the 'start' event for every element).
      pushText();
   }

   /**
    * Prints the text that corresponds to the closing of the VNSUBCLASS
    * element in the VerbNet XML files.  No additional text needs to be
    * printed here.  Only the 'end' event for the subclass is fired.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active VNSUBCLASS element
    */
   static void endVNSUBCLASS( Node n )
   {

      // If the proper view options were supplied, display the text
      // for the closing of this element.  Although there is no text
      // to display in this method, the indentation level must now be
      // decreased.
      if( Inspector.voClassName )
      {

         // Remove this element's text from the replication stack
         // now that it's ending.
         popTextForReplicate();

         curIndentLevel--;
      }

      // Retrieve the global event string for this element that was previously
      // saved to a stack.  This method sets the class-level variable evText.
      popText();

      EventManager.fireEventMaybe( EventManager.EVENT_SUBCLASS, EventManager.EVENT_END, curFile, curClass, evText, n, null );
   }

   // ---------------------- //
   // -- Member Elements  -- //
   // ---------------------- //

   /**
    * Prints the text that corresponds to the beginning of the MEMBERS
    * element in the VerbNet XML files.  There is no text actually
    * printed here other than the <CODE>&lt;NO MEMBERS></CODE> label
    * if there are no members for this class or subclass and
    * the "no-absence" flag (-z) was <I>not</I> supplied on the
    * command line.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active MEMBERS element
    * @see vn.Sweeper#iprintln(String)
    */
   static void startMEMBERS( Node n )
   {

      // Clear out the members list from the previous class or subclass.
      // This is a good place to clear this list because new members will
      // be added to it as the MEMBER elements are encountered shortly.
      members.clear();

      // If the proper view options were supplied, display the text
      // for the beginning of this element.  Currently the only
      // thing that needs to be printed here, is the NO MEMBERS
      // label if there are no thematic roles for this class or subclass.
      if( !Inspector.flNoAbsence && Inspector.voMember && !Inspector.flVFPairs )
         if( !hasKids( n, "MEMBER" ) )
         {

            // Reprint labels for all files, classes, subclasses, and frames in which
            // this member absence label is contained.
            if( Inspector.flReplicate )
               replicateLabels();

            iprintln( "<NO MEMBERS>" );
         }
   }

   /**
    * Prints the text that corresponds to the closing of the MEMBERS
    * element in the VerbNet XML files.  No specific closing text is
    * needed to be printed, but here is where all the members of
    * the current class or subclass are printed, now that they
    * were all loaded up (and possibly sorted) by {@link vn.Sweeper#startMEMBER(Node)}.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active MEMBERS element
    * @see vn.Sweeper#printMembers()
    * @see vn.Sweeper#startMEMBER(Node)
    */
   static void endMEMBERS( Node n )
   {

      // If the Inspector is running normal mode, not verb-frame pair mode,
      // then print all the members.
      if( !Inspector.flVFPairs )
         printMembers();
   }

   /**
    * Prints the text that corresponds to the beginning of the MEMBER
    * element in the VerbNet XML files.  Instead of printing the member
    * at this moment, all the members are stored into a list to
    * be printed later upon executing the {@link vn.Sweeper#endMEMBERS(Node)}
    * method.  This method adds the members to the list in sorted order
    * if the sort members (-s) flag is provded ({@link vn.Inspector#flSortMembers}).
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active MEMBER element
    * @see vn.Sweeper#printMembers()
    * @see vn.Sweeper#endMEMBERS(Node)
    */
   static void startMEMBER( Node n )
   {

      // Grab all attributes from the element.
      String vbName = ( ( Element ) n ).getAttribute( "name" );
      String wn     = ( ( Element ) n ).getAttribute( "wn" );

      // Don't attempt to sort the member if it's the first member
      // of if sorting is not enabled.
      if( !Inspector.flSortMembers || members.size() == 0 )
         members.add( new MemberNode( vbName, wn, n ) );

      else
      {
         int m;

         // Locate the insertion point.
         for( m = members.size(); m > 0; m-- )
         {

            // Isolate current member.
            String mm = ( ( MemberNode ) members.get( m - 1 ) ).verb;

            // If the array list entry is lexicographically less than
            // the new verb name, then it's in sorted order.
            if( mm.compareTo( vbName ) < 0 )
               break;
         }

         // Add the verb at the located position.
         members.add( m, new MemberNode( vbName, wn, n ) );
      }
   }

   /**
    * Prints the text that corresponds to the closing of the MEMBER
    * element in the VerbNet XML files.
    * Although it is specified for completeness, this method does
    * not do anything useful.  This is because <CODE>&lt;!ELEMENT MEMBER EMPTY></CODE>
    * in the DTD, so any "closing text" could just be placed at the
    * end of the {@link vn.Sweeper#startMEMBER(Node)} method.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active MEMBER element
    */
   static void endMEMBER( Node n )
   {

      // If the proper view options were supplied, display the text
      // for the closing of this element (nothing as of yet).
      if( Inspector.voMember )
      {
         // Text to display for end of MEMBER element.
      }
   }

   // ----------------------------- //
   // -- Thematic Role Elements  -- //
   // ----------------------------- //

   /**
    * Prints the text that corresponds to the beginning of the THEMROLES
    * element in the VerbNet XML files.  There is no text actually
    * printed here other than the <CODE>&lt;NO THEMROLES></CODE> label
    * if there are no thematic roles for this class or subclass and
    * the "no-absence" flag (-z) was <I>not</I> supplied on the
    * command line.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active THEMROLES element
    * @see vn.Sweeper#iprintln(String)
    */
   static void startTHEMROLES( Node n )
   {

      // If the proper view options were supplied, display the text
      // for the beginning of this element.  Currently the only
      // thing that needs to be printed here, is the NO THEMROLES
      // label if there are no thematic roles for this class or subclass.
      if( !Inspector.flNoAbsence && Inspector.voThemRole )
         if( !hasKids( n, "THEMROLE" ) )
         {

            // Reprint labels for all files, classes, subclasses, and frames in which
            // this thematic role absence label is contained.
            if( Inspector.flReplicate )
               replicateLabels();

            iprintln( "<NO THEMROLES>" );
         }
   }

   /**
    * Prints the text that corresponds to the closing of the THEMROLES
    * element in the VerbNet XML files.  No text is needed to
    * be printed here, as THEMROLE elements are printed independently on
    * their own line.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active THEMROLES element
    */
   static void endTHEMROLES( Node n )
   {

      // If the proper view options were supplied, display the text
      // for the closing of this element (nothing as of yet).
      if( Inspector.voThemRole )
      {
         // Text to display for end of THEMROLES element.
      }
   }

   /**
    * Prints the text that corresponds to the beginning of the THEMROLE
    * element in the VerbNet XML files.  The global event string will
    * be initialized to this text in preparation for the events that
    * fire for the THEMROLE element in {@link vn.Sweeper#endTHEMROLE}.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active THEMROLE element
    * @see vn.Sweeper#iprint(String)
    * @see vn.Inspector#incrementTagCounter(String)
    */
   static void startTHEMROLE( Node n )
   {

      // Grab all attributes from the element.
      String type = ( ( Element ) n ).getAttribute( "type" );

      // Signal that any SELRESTRS or SELRESTR elements that are visited
      // immediately after this method are children of this THEMROLE element,
      // and should be displayed as such.
      trSelRestrs = true;

      // Construct local output string (simple-text representation) for this element.
      evTextLocal = "THEMROLE: " + type + " ";

      // Initialize the global event string to the local output string since this
      // is the first text to display on the line.
      evText = evTextLocal;

      // If the proper view options were supplied, display the text
      // for the beginning of this element (the local output string).
      if( Inspector.voThemRole )
      {

         // Reprint labels for all files, classes, subclasses, and frames in which
         // this thematic role is contained.
         if( Inspector.flReplicate )
            replicateLabels();

         // Print the local output string with proper indentation.
         iprint( evTextLocal );

         // Increment the counter for this element.
         Inspector.incrementTagCounter( "THEMROLE" );
      }
   }

   /**
    * Prints the text that corresponds to the closing of the THEMROLE
    * element in the VerbNet XML files.  Right now the primary
    * responsibility of this method is to fire both the 'start THEMROLE'
    * and 'end THEMROLE' events.  The gloabl event string will have been
    * initialized to the proper THEMROLE label and the events
    * are ready to be fired.  Since the THEMROLE element takes up only
    * one line in the console, the 'start' and 'end' events are
    * fired one right after the other.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active THEMROLE element
    */
   static void endTHEMROLE( Node n )
   {

      // Signal that any SELRESTRS or SELRESTR elements that are visited
      // immediately after this method are no longer necessarily
      // children of this THEMROLE element.
      trSelRestrs = false;

      // If the proper view options were supplied, display the text
      // for the closing of this element.
      if( Inspector.voThemRole )
         println( "" );                   // Carriage return does not affect event text.

      // Fire both the start and end events for the THEMROLE element.  See note
      // in EventManager class for more information on why these fire back-to-back.
      EventManager.fireEventMaybe( EventManager.EVENT_THEMROLE, EventManager.EVENT_START, curFile, curClass, evText.trim(), n, null );
      EventManager.fireEventMaybe( EventManager.EVENT_THEMROLE, EventManager.EVENT_END,   curFile, curClass, evText.trim(), n, null );
   }

   // --------------------------------------- //
   // -- Selectional Restriction Elements  -- //
   // --------------------------------------- //

   /**
    * Prints the text that corresponds to the beginning of the SELRESTRS
    * element in the VerbNet XML files.  The text is also appended
    * to the global event string that will be used in the events that
    * fire for the THEMROLE or SYNTAX (NP or PREP) elements.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active SELRESTRS element
    */
   static void startSELRESTRS( Node n )
   {

      // Grab all attributes from the element.
      String logic = ( ( Element ) n ).getAttribute( "logic" );

      String type;
      String op = "";         // Default is no preceding operator.

      // If this is not the top-level SELRESTRS, then print the appropriate
      // operator, which was set when the parent SELRESTRS was visited.
      // Note this value is not pushed or popped on or off of any stack,
      // so multiple levels of SELRESTRS could see invalid operators chosen.
      if( restrsLevel != 0 )
         op = usingOr ? " | " : " & ";

      // Decide whether or not the operator to be applied between multiple
      // SELRESTR/SELRESTRS children elements is the 'Or' operator.  If the 'logic'
      // attribute of this element is not "or" then the operator is
      // assumed to be the 'And' operator.
      usingOr = logic.equals( "or" );

      // Decide which type of brackets to use.  Prepositions get curly braces.
      if( prepSelRestrs )
         type = "{";

      else
         type = "[";

      // Construct local output string (simple-text representation) for this element.
      evTextLocal = "";

      // If this SELRESTRS element has any children (SELRESTR elements), then
      // add the operator and opening bracket to the local output string.
      if( hasKids( n, "SELRESTR" ) )
         evTextLocal = op + type;

      // Add local output string to global event string for THEMROLE or SYNTAX element.
      // The global event string is initialized in startTHEMROLE or startSYNTAX and added to
      // by each of that element's children elements.  Events are fired with
      // the final event text in endTHEMROLE or endSYNTAX.
      evText += evTextLocal;

      // Increase the depth of the SELRESTRS nodes.  Only needed since
      // SELRESTRS is a recursive node and to know if an operator must be
      // printed before one.
      restrsLevel++;

      // Signal that there have not been any SELRESTR elements encountered as of yet.
      hasBeenOther = false;

      // If the proper view options were supplied, display the text
      // for the beginning of this element (the local output string).
      if( ( !trSelRestrs   || ( Inspector.voThemRole && Inspector.voTRSelRestr ) ) &&
          ( !prepSelRestrs || ( Inspector.voSyntax ) ) &&
          ( !npSelRestrs   || ( Inspector.voSyntax && Inspector.voXSelRestr ) ) )
      {
         print( evTextLocal );
      }
   }

   /**
    * Prints the text that corresponds to the closing of the SELRESTRS
    * element in the VerbNet XML files.  The text is also appended
    * to the global event string that will be used in the events that
    * fire for the THEMROLE or SYNTAX (NP or PREP) elements.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active SELRESTRS element
    */
   static void endSELRESTRS( Node n )
   {
      String type;

      // Decide which closing bracket is to be used.  Preposition selectional
      // restrictions get curly braces.
      if( prepSelRestrs )
         type = "}";

      else
      {
         type = "]";

         if( restrsLevel == 1 )
            type += " ";
      }

      // Construct local output string (simple-text representation) for this element.
      evTextLocal = "";

      // If there was any selectional restrictions visited, then add the
      // closing bracket.
      if( hasBeenOther )
         evTextLocal = type;

      // Add local output string to global event string for THEMROLE or SYNTAX element.
      // The global event string is initialized in startTHEMROLE or startSYNTAX and added to
      // by each of that element's children elements.  Events are fired with
      // the final event text in endTHEMROLE or endSYNTAX.
      evText += evTextLocal;

      // Decrease the depth of the SELRESTRS nodes.  Only needed since
      // SELRESTRS is a recursive node and to know if an operator must be
      // printed before one.
      restrsLevel--;

      // If the proper view options were supplied, display the text
      // for the closing of this element (the local output string).
      if( ( !trSelRestrs   || ( Inspector.voThemRole && Inspector.voTRSelRestr ) ) &&
          ( !prepSelRestrs || ( Inspector.voSyntax ) ) &&
          ( !npSelRestrs   || ( Inspector.voSyntax && Inspector.voXSelRestr ) ) )
      {
         print( evTextLocal );
      }
   }

   /**
    * Prints the text that corresponds to the beginning of the SELRESTR
    * element in the VerbNet XML files.  The text is also appended
    * to the global event string that will be used in the events that
    * fire for the THEMROLE or SYNTAX (NP or PREP) elements.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active SELRESTR element
    */
   static void startSELRESTR( Node n )
   {

      // Grab all attributes from the element.
      String value = ( ( Element ) n ).getAttribute( "Value" );
      String type  = ( ( Element ) n ).getAttribute( "type" );

      String op = "";        // Default is no preceding operator.

      // If there has already been a selectional restriction printed,
      // set an additional string to the appropriate operator.
      // Which operator to add is based off of the 'logic' attribute
      // of the SELRESTRS element.
      if( hasBeenOther )
         op = usingOr ? " | " : " & ";

      // Construct local output string (simple-text representation) for this element.
      evTextLocal = op + value + type;

      // Add local output string to global event string for THEMROLE or SYNTAX element.
      // The global event string is initialized in startTHEMROLE or startSYNTAX and added to
      // by each of that element's children elements.  Events are fired with
      // the final event text in endTHEMROLE or endSYNTAX.
      evText += evTextLocal;

      // Signal that at least one SELRESTR element has been encountered.
      hasBeenOther = true;

      // If the proper view options were supplied, display the text
      // for the beginning of this element (the local output string).
      if( ( !trSelRestrs   || ( Inspector.voThemRole && Inspector.voTRSelRestr ) ) &&
          ( !prepSelRestrs || ( Inspector.voSyntax ) ) &&
          ( !npSelRestrs   || ( Inspector.voSyntax && Inspector.voXSelRestr ) ) )
      {
         print( evTextLocal );
      }
   }

   /**
    * Prints the text that corresponds to the closing of the SELRESTR
    * element in the VerbNet XML files.
    * Although it is specified for completeness, this method does
    * not do anything useful.  This is because <CODE>&lt;!ELEMENT SELRESTR EMPTY></CODE>
    * in the DTD, so any "closing text" could just be placed at the
    * end of the {@link vn.Sweeper#startSELRESTR(Node)} method.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active SELRESTR element
    */
   static void endSELRESTR( Node n )
   {

      // If the proper view options were supplied, display the text
      // for the closing of this element (nothing as of yet).
      if( ( !trSelRestrs   || ( Inspector.voThemRole && Inspector.voTRSelRestr ) ) &&
          ( !prepSelRestrs || ( Inspector.voSyntax ) ) &&
          ( !npSelRestrs   || ( Inspector.voSyntax && Inspector.voXSelRestr ) ) )
      {
      }
   }

   // --------------------- //
   // -- Frame Elements  -- //
   // --------------------- //

   /**
    * Prints the text that corresponds to the beginning of the FRAMES
    * element in the VerbNet XML files.  There is no text actually
    * printed here other than the <CODE>&lt;NO FRAMES></CODE> label
    * if there are no frames for this class or subclass and
    * the "no-absence" flag (-z) was <I>not</I> supplied on the
    * command line.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active FRAMES element
    * @see vn.Sweeper#iprintln(String)
    */
   static void startFRAMES( Node n )
   {

      // If the proper view options were supplied, display the text
      // for the beginning of this element.  Currently the only
      // thing that needs to be printed here, is the NO FRAMES
      // label if there are no frames for this class or subclass.
      if( !Inspector.flNoAbsence && Inspector.voFrame && !Inspector.flVFPairs )
         if( !hasKids( n, "FRAME" ) )
         {

            // Reprint labels for all files, classes, subclasses, and frames in which
            // this frame absence label is contained.
            if( Inspector.flReplicate )
               replicateLabels();

            iprintln( "<NO FRAMES>" );
         }
   }

   /**
    * Prints the text that corresponds to the closing of the FRAMES
    * element in the VerbNet XML files.  Although no text is actually
    * required at this point, this method does have the important
    * task of printing verb-frame pairs and class counts.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active FRAMES element
    * @see vn.Sweeper#printVerbFramePairs()
    * @see vn.Inspector#printTagCounts(boolean)
    */
   static void endFRAMES( Node n )
   {

      // Print all the verb-frame pairs if the Inspector is running in that mode.
      // The method vn.Inspector#processNodeByPairs() skips all FRAME
      // elements during its initial processing, adding them manually to the
      // frames list that it is giving to the Sweeper class for this very moment.
      // Now all the members have been added to vn.Sweeper#members and the
      // frames list has been given to this class, so it's ready to go for
      // verb-frame pair printing.
      if( Inspector.flVFPairs )
         printVerbFramePairs();

      // The end of the FRAMES element is regarded not as the end of a
      // subclass or frame, but rather the point right before a new subclass
      // begins.  Therefore, since counts are per class or subclass, it makes
      // sense to display them right after the frames have been printed.
      if( Inspector.flClassCounts )
         Inspector.printTagCounts( true );

      // If the proper view options were supplied, display the text
      // for the closing of this element.
      if( Inspector.voFrame )
      {
         // Text to display for end of FRAMES element.
      }

      // Signal that a new class will be beginning soon, not synonymous with
      // end of class because of the nesting nature of VerbNet classes.
      EventManager.fireEventMaybe( EventManager.EVENT_END_FRAMES, EventManager.EVENT_END, curFile, curClass, "", n, null );
   }

   /**
    * Prints the text that corresponds to the beginning of the FRAME
    * element in the VerbNet XML files.  The global event string will
    * be initialized to this text in preparation for the events that
    * fire for the FRAME element or verb-frame pair.  The FRAME
    * element is used to print verb-frame pairs.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active FRAME element
    * @see vn.Sweeper#iprint(String)
    * @see vn.Inspector#incrementTagCounter(String)
    */
   static void startFRAME( Node n )
   {

      // Construct local output string (simple-text representation) for this element.
      if( Inspector.flVFPairs )
         evTextLocal = "VF-PAIR: ";

      else
         evTextLocal = "FRAME: ";

      // Initialize the global event string to the local output string since this
      // is the first text to display on the line.
      evText = evTextLocal;

      // If the proper view options were supplied, display the text
      // for the beginning of this element (the local output string).
      if( Inspector.voFrame )
      {

         // Reprint labels for all files, classes, subclasses, and frames in which
         // this frame or verb-frame pair is contained.
         if( Inspector.flReplicate )
            replicateLabels();

         // Print the local output string with proper indentation.
         iprint( evTextLocal );

         // Since the FRAME and VF-PAIR elements are some which indent all elements under them,
         // increase the indentation level so that if indentation is enabled
         // (via appropriate flag), iprint & iprintln will indent text given to them.
         curIndentLevel++;

         // Increment the counter for this element, depending on whether this method
         // is being used to process verb-frame pairs, or just normal frames.
         if( Inspector.voVFPairs )
            Inspector.incrementTagCounter( "VF-PAIR" );

         else
            Inspector.incrementTagCounter( "FRAME" );
      }
   }

   /**
    * Prints the text that corresponds to the closing of the FRAME
    * element in the VerbNet XML files.  No additional text is
    * required to be printed, but the 'end' events are fired for
    * the FRAME element or verb-frame pair.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active FRAME element
    */
   static void endFRAME( Node n )
   {

      // If the proper view options were supplied, display the text
      // for the closing of this element.  Although there is no text
      // to display in this method, the indentation level must now be
      // decreased.
      if( Inspector.voFrame )
      {

         // Remove this element's text from the replication stack
         // now that it's ending.
         popTextForReplicate();

         curIndentLevel--;
      }

      // Retrieve the global event string for this element that was previously
      // saved to a stack.  This method sets the class-level variable evText.
      popText();

      // Fire the 'end' events for either the verb-frame pair or the frame.
      // The FRAME element is used to display verb-frame pairs.  It is just
      // given the verb name and verb WordNet information in order to display as a
      // verb-frame pair instead of a normal FRAME element.
      if( Inspector.flVFPairs )
         EventManager.fireEventMaybe( EventManager.EVENT_VF_PAIR, EventManager.EVENT_END, curFile, curClass, evText, curVFMemberNode, curVFFrameNode );

      else
         EventManager.fireEventMaybe( EventManager.EVENT_FRAME, EventManager.EVENT_END, curFile, curClass, evText, n, null );
   }

   /**
    * Prints the text that corresponds to the beginning of the DESCRIPTION
    * element in the VerbNet XML files.  This adds the bulk of the header
    * label for both verb-frame pairs and regular frames elements.
    * The 'start' events for the verb-frame pairs and regular frame elements
    * are fired here since their text is completed in this method.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active DESCRIPTION element
    */
   static void startDESCRIPTION( Node n )
   {

      // Grab all attributes from the element.
      String p = ( ( Element ) n ).getAttribute( "primary" );
      String s = ( ( Element ) n ).getAttribute( "secondary" );
      String d = ( ( Element ) n ).getAttribute( "descriptionNumber" );
      String x = ( ( Element ) n ).getAttribute( "xtag" );

      String fullText;

      // If there is a secondary description, prepend a divider between
      // it and the primary description.
      if( !s.equals( "" ) )
         s = " // " + s;

      // Construct the members only shown in event text or when -Vb is supplied.
      String extra = " (descriptionNumber=" + d + ", xtag=" + x + ")";

      // Construct local output string (simple-text representation) for this element.

      // If the Inspector is running in verb-frame pair mode, then both verb and frame
      // information should be included in this frame.
      if( Inspector.flVFPairs )
      {

         // Construct the full text needed for the event text.
         fullText = "VERB: " + curVFVerbName + " (wn=" + curVFVerbWN + ") FRAME: [" + p + s + "]" + extra;

         // The text that is printed for a verb-frame pair is dependent on
         // both whether the user wants to see the WordNet information as well
         // as whether the user wants to see the complete (non-standard)
         // information.

         // Wordnet and complete...
         if( Inspector.voWordNet && Inspector.voComplete)
            evTextLocal = fullText;

         // Not wordnet and complete...
         else if( !Inspector.voWordNet && Inspector.voComplete )
            evTextLocal = "VERB: " + curVFVerbName + " FRAME: [" + p + s + "]" + extra;

         // Wordnet and not complete...
         else if( Inspector.voWordNet && !Inspector.voComplete )
            evTextLocal = "VERB: " + curVFVerbName + " (wn=" + curVFVerbWN + ") FRAME: [" + p + s + "]";

         // Not wordnet and not complete...
         else if( !Inspector.voWordNet && !Inspector.voComplete )
            evTextLocal = "VERB: " + curVFVerbName + " FRAME: [" + p + s + "]";
      }

      // Else if the Inspector is running in normal mode, just print the basic frame
      // information.
      else
      {

         // Construct the full text needed for the event text.
         fullText = "[" + p + s + "]" + extra;

         // The text that is printed depends on whether the user wants to see
         // the complete (non-standard) information.
         if( Inspector.voComplete )
            evTextLocal = fullText;

         else
            evTextLocal = "[" + p + s + "]";
      }

      // Add local output string to global event string for FRAME element.
      // The global event string is initialized in startFRAME and added to
      // by each of that element's children elements.  Events are fired with
      // the final event text in startDESCRIPTION and endFRAME.
      evText += fullText;

      // If the proper view options were supplied, display the text
      // for the beginning of this element (the local output string).
      if( Inspector.voFrame )
      {
         String rText = ( Inspector.flVFPairs ) ? "VF-PAIR: " : "FRAME: ";

         // Save the text that will be printed for this element
         // for possible replication.
         pushTextForReplicate( rText + evTextLocal );

         println( evTextLocal );
      }

      // Fire the 'start' events for either the verb-frame pair or the frame.
      // The FRAME element is used to display verb-frame pairs.  It is just
      // given the verb name and verb WordNet information in order to display as a
      // verb-frame pair instead of a normal FRAME element.
      if( Inspector.flVFPairs )
         EventManager.fireEventMaybe( EventManager.EVENT_VF_PAIR, EventManager.EVENT_START, curFile, curClass, evText, curVFMemberNode, curVFFrameNode );

      else
         EventManager.fireEventMaybe( EventManager.EVENT_FRAME, EventManager.EVENT_START, curFile, curClass, evText, n, null );

      // Add this global event string to a stack for retrieval when the 'end'
      // event fires for this element (the 'end' event has the same event text
      // as the 'start' event for every element).
      pushText();
   }

   /**
    * Prints the text that corresponds to the closing of the DESCRIPTION
    * element in the VerbNet XML files.
    * Although it is specified for completeness, this method does
    * not do anything useful.  This is because <CODE>&lt;!ELEMENT DESCRIPTION EMPTY></CODE>
    * in the DTD, so any "closing text" could just be placed at the
    * end of the {@link vn.Sweeper#startDESCRIPTION(Node)} method.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active DESCRIPTION element
    */
   static void endDESCRIPTION( Node n )
   {

      // If the proper view options were supplied, display the text
      // for the closing of this element (nothing as of yet).
      if( Inspector.voFrame )
      {
         // Text to display for end of DESCRIPTION element.
      }
   }

   // ----------------------- //
   // -- Example Elements  -- //
   // ----------------------- //

   /**
    * Prints the text that corresponds to the beginning of the EXAMPLES
    * element in the VerbNet XML files.  No text is currently printed
    * for the start of the examples section.  Each example is printed
    * independently on its own line.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active EXAMPLES element
    */
   static void startEXAMPLES( Node n )
   {

      // If the proper view options were supplied, display the text
      // for the beginning of this element (nothing as of yet).
      if( Inspector.voExample )
      {
         // Text to display for beginning of EXAMPLES element.
      }
   }

   /**
    * Prints the text that corresponds to the closing of the EXAMPLES
    * element in the VerbNet XML files.  No text is currently printed
    * for the end of the examples section.  Each example is printed
    * independently on its own line.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active EXAMPLES element
    */
   static void endEXAMPLES( Node n )
   {

      // If the proper view options were supplied, display the text
      // for the closing of this element (nothing as of yet).
      if( Inspector.voExample )
      {
         // Text to display for end of EXAMPLES element.
      }
   }

   /**
    * Prints the text that corresponds to the beginning of the EXAMPLE
    * element in the VerbNet XML files.  The global event string will
    * be initialized to this text in preparation for the events that
    * fire for the EXAMPLE element.  There is one line of text output
    * for each VerbNet EXAMPLE element.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active EXAMPLE element
    * @see vn.Sweeper#iprintln(String)
    * @see vn.Inspector#incrementTagCounter(String)
    */
   static void startEXAMPLE( Node n )
   {
      NodeList kids = n.getChildNodes();

      // Construct local output string (simple-text representation) for this element.
      evTextLocal = "";

      // Search for the child node of this EXAMPLE element which
      // contains the example text.
      for( int k = 0; k < kids.getLength(); k++ )
      {
         Node kid = ( Node ) kids.item( k );

         if( kid.getNodeName().equals( "#text" ) || kid.getNodeName().equals( "#cdata-section" ) )
         {
            evTextLocal = "EXAMPLE: " + kid.getNodeValue();
            break;
         }
      }

      // Initialize the global event string to the local output string since this
      // is the first text to display on the line.
      evText = evTextLocal;

      // If the proper view options were supplied, display the text
      // for the beginning of this element (the local output string).
      if( Inspector.voExample )
      {

         // Reprint labels for all files, classes, subclasses, and frames in which
         // this example is contained.
         if( Inspector.flReplicate )
            replicateLabels();

         // Print the local output string with proper indentation.
         iprintln( evTextLocal );

         // Increment the counter for this element.
         Inspector.incrementTagCounter( "EXAMPLE" );
      }
   }

   /**
    * Prints the text that corresponds to the closing of the EXAMPLE
    * element in the VerbNet XML files.
    * Although it is specified for completeness, this method does
    * not do anything useful.  This is because <CODE>&lt;!ELEMENT EXAMPLE (#PCDATA)></CODE>
    * in the DTD, so any "closing text" could just be placed at the
    * end of the {@link vn.Sweeper#startEXAMPLE(Node)} method. However,
    * for symmetry with other sweeper methods, it does fire the 'start'
    * and 'end' events for the EXAMPLE element.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active EXAMPLE element
    */
   static void endEXAMPLE( Node n )
   {

      // If the proper view options were supplied, display the text
      // for the closing of this element (nothing as of yet).
      if( Inspector.voExample )
      {
         // Text to display for end of EXAMPLE element.
      }

      // Fire both the start and end events for the EXAMPLE element.  See note
      // in EventManager class for more information on why these fire back-to-back.
      EventManager.fireEventMaybe( EventManager.EVENT_EXAMPLE, EventManager.EVENT_START, curFile, curClass, evText, n, null );
      EventManager.fireEventMaybe( EventManager.EVENT_EXAMPLE, EventManager.EVENT_END,   curFile, curClass, evText, n, null );
   }

   // ------------------------- //
   // -- Semantics Elements  -- //
   // ------------------------- //

   /**
    * Prints the text that corresponds to the beginning of the SEMANTICS
    * element in the VerbNet XML files.  No text is needed to
    * be printed here, as PRED elements are printed independently on
    * their own line (unlike the Unified Verb Index).
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active SEMANTICS element
    */
   static void startSEMANTICS( Node n )
   {

      // If the proper view options were supplied, display the text
      // for the beginning of this element (nothing as of yet).
      if( Inspector.voSemantics )
      {
         // Text to display for beginning of SEMANTICS element.
      }
   }

   /**
    * Prints the text that corresponds to the closing of the SEMANTICS
    * element in the VerbNet XML files.  No text is needed to
    * be printed here, as PRED elements are printed independently on
    * their own line (unlike the Unified Verb Index).
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active SEMANTICS element
    */
   static void endSEMANTICS( Node n )
   {

      // If the proper view options were supplied, display the text
      // for the closing of this element (nothing as of yet).
      if( Inspector.voSemantics )
      {
         // Text to display for end of SEMANTICS element.
      }
   }

   /**
    * Prints the text that corresponds to the beginning of the PRED
    * element in the VerbNet XML files.  The global event string will
    * be initialized to this text in preparation for the events that
    * fire for the PRED element.  There is one line of text output
    * for each VerbNet PRED element.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active PRED element
    * @see vn.Sweeper#iprint(String)
    * @see vn.Inspector#incrementTagCounter(String)
    */
   static void startPRED( Node n )
   {

      // Grab all attributes from the element.
      String value = ( ( Element ) n ).getAttribute( "value" );
      String bool  = ( ( Element ) n ).getAttribute( "bool" );

      // If this predicate is negated, reuse the variable above
      // to hold text to that effect.  If the predicate is not
      // negated the value of this variable will be the empty string.
      if( bool.equals( "!" ) )
         bool = "not(";

      // Construct local output string (simple-text representation) for this element.
      evTextLocal = "SEMANTIC PRED: " + bool + value + "(";

      // Initialize the global event string to the local output string since this
      // is the first text to display on the line.
      evText = evTextLocal;

      // If the proper view options were supplied, display the text
      // for the beginning of this element (the local output string).
      // This output will be followed by all arguments of the predicate.
      if( Inspector.voSemantics )
      {

         // Reprint labels for all files, classes, subclasses, and frames in which
         // this semantic predicate is contained.
         if( Inspector.flReplicate )
            replicateLabels();

         // Print the local output string with proper indentation.
         iprint( evTextLocal );

         // Increment the counter for this element.
         Inspector.incrementTagCounter( "SEMANTIC PRED" );
      }
   }

   /**
    * Prints the text that corresponds to the closing of the PRED
    * element in the VerbNet XML files.  The text is also appended
    * to the global event string that will be used in the events that
    * fire for the SYNTAX element.  The events for PRED (SEMANTIC PRED)
    * are fired in this method, since all the text has been accumulated
    * for the predicate and arguments at this point.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active PRED element
    */
   static void endPRED( Node n )
   {

      // Grab attributes from the element.
      String bool = ( ( Element ) n ).getAttribute( "bool" );

      // Construct local output string (simple-text representation) for this element.
      evTextLocal = ")" + ( bool.equals( "!" ) ? ")" : "" );

      // Add local output string to global event string for PRED element.
      // The global event string is initialized in startPRED and added to
      // by each of that element's children elements.  Events are fired with
      // the final event text in endPRED.
      evText += evTextLocal;

      // If the proper view options were supplied, display the text
      // for the closing of this element (the local output string).
      if( Inspector.voSemantics )
         println( evTextLocal );

      // Fire both the start and end events for the PRED element.  See note
      // in EventManager class for more information on why these fire back-to-back.
      EventManager.fireEventMaybe( EventManager.EVENT_SEMANTIC_PRED, EventManager.EVENT_START, curFile, curClass, evText, n, null );
      EventManager.fireEventMaybe( EventManager.EVENT_SEMANTIC_PRED, EventManager.EVENT_END,   curFile, curClass, evText, n, null );
   }

   /**
    * Prints the text that corresponds to the beginning of the ARG
    * element in the VerbNet XML files.  No text is needed to
    * be printed here, as the beginning text for arguments is
    * printed in {@link vn.Sweeper#startPRED}.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active ARGS element
    */
   static void startARGS( Node n )
   {

      // Signal that there have not been any ARG elements encountered as of yet.
      hasBeenOther = false;

      // If the proper view options were supplied, display the text
      // for the beginning of this element (nothing as of yet).
      if( Inspector.voSemantics )
      {
         // Text to display for beginning of ARGS element.
      }
   }

   /**
    * Prints the text that corresponds to the closing of the ARGS
    * element in the VerbNet XML files.  No text is needed to
    * be printed here, as the ending text for arguments is
    * printed in {@link vn.Sweeper#endPRED}.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active ARGS element
    */
   static void endARGS( Node n )
   {

      // If the proper view options were supplied, display the text
      // for the closing of this element (nothing as of yet).
      if( Inspector.voSemantics )
      {
         // Text to display for end of ARGS element.
      }
   }

   /**
    * Prints the text that corresponds to the beginning of the ARG
    * element in the VerbNet XML files.  The text is also appended
    * to the global event string that will be used in the events that
    * fire for the PRED (SEMANTIC PRED) element.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active ARG element
    */
   static void startARG( Node n )
   {

      // Grab all attributes from the element.
      String value = ( ( Element ) n ).getAttribute( "value" );
      String type  = ( ( Element ) n ).getAttribute( "type" );

      String cm = "";         // Default is no preceding characters.

      String t  = "{" + type + "}";    // Used for complete output.

      // If there has already been an argument printed,
      // set an additional string to a comma and space.
      if( hasBeenOther )
         cm = ", ";

      // Construct the full text needed for the event text.
      String fullText = cm + value + t;

      // Construct local output string (simple-text representation) for this element.
      if( Inspector.voComplete )
         evTextLocal =  fullText;

      else
         evTextLocal =  cm + value;    // No type.

      // Add local output string to global event string for PRED element.
      // The global event string is initialized in startPRED and added to
      // by each of that element's children elements.  Events are fired with
      // the final event text in endPRED.
      evText += fullText;

      // Signal that at least one ARG element has been encountered.
      hasBeenOther = true;

      // If the proper view options were supplied, display the text
      // for the beginning of this element (the local output string).
      if( Inspector.voSemantics )
         print( evTextLocal );
   }

   /**
    * Prints the text that corresponds to the closing of the ARG
    * element in the VerbNet XML files.
    * Although it is specified for completeness, this method does
    * not do anything useful.  This is because <CODE>&lt;!ELEMENT ARG EMPTY></CODE>
    * in the DTD, so any "closing text" could just be placed at the
    * end of the {@link vn.Sweeper#startARG(Node)} method.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active ARG element
    */
   static void endARG( Node n )
   {

      // If the proper view options were supplied, display the text
      // for the closing of this element (nothing as of yet).
      if( Inspector.voSemantics )
      {
         // Text to display for end of ARG element.
      }
   }

   // ---------------------------------------------------------------------------------------- //
   // -- Syntax Elements (SELRESTRS/SELRESTR above are also used in syntax representations) -- //
   // ---------------------------------------------------------------------------------------- //

   /**
    * Prints the text that corresponds to the beginning of the SYNTAX
    * element in the VerbNet XML files.  The global event string will
    * be initialized to this text in preparation for the events that
    * fire for the SYNTAX element.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active SYNTAX element
    * @see vn.Sweeper#iprint(String)
    * @see vn.Inspector#incrementTagCounter(String)
    */
   static void startSYNTAX( Node n )
   {

      // Construct local output string (simple-text representation) for this element.
      evTextLocal = "SYNTAX: ";

      // Initialize the global event string to the local output string since this
      // is the first text to display on the line.
      evText = evTextLocal;

      // If the proper view options were supplied, display the text
      // for the beginning of this element (the local output string).
      // This output will be followed by all syntax elements.
      if( Inspector.voSyntax )
      {

         // Reprint labels for all files, classes, subclasses, and frames in which
         // this syntax line is contained.
         if( Inspector.flReplicate )
            replicateLabels();

         // Print the local output string with proper indentation.
         iprint( evTextLocal );

         // Increment the counter for this element.
         Inspector.incrementTagCounter( "SYNTAX" );
      }
   }

   /**
    * Prints the text that corresponds to the closing of the SYNTAX
    * element in the VerbNet XML files.  Right now the primary
    * responsibility of this method is to fire both the 'start SYNTAX'
    * and 'end SYNTAX' events.  The gloabl event string will have been
    * appended to by all of SYNTAX's children elements and the events
    * are ready to be fired.  Since the SYNTAX element takes up only
    * one line in the console, the 'start' and 'end' events are
    * fired one right after the other.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active SYNTAX element
    */
   static void endSYNTAX( Node n )
   {

      // If the proper view options were supplied, display the text
      // for the closing of this element.
      if( Inspector.voSyntax )
         println( "" );             // Carriage return does not affect event text.

      // Fire both the start and end events for the SYNTAX element.  See note
      // in EventManager class for more information on why these fire back-to-back.
      EventManager.fireEventMaybe( EventManager.EVENT_SYNTAX, EventManager.EVENT_START, curFile, curClass, evText.trim(), n, null );
      EventManager.fireEventMaybe( EventManager.EVENT_SYNTAX, EventManager.EVENT_END,   curFile, curClass, evText.trim(), n, null );
   }

   /**
    * Prints the text that corresponds to the beginning of the NP
    * element in the VerbNet XML files.  The text is also appended
    * to the global event string that will be used in the events that
    * fire for the SYNTAX element.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active NP element
    */
   static void startNP( Node n )
   {

      // Grab all attributes from the element.
      String value = ( ( Element ) n ).getAttribute( "value" );

      // Construct local output string (simple-text representation) for this element.
      evTextLocal = "%" + value + " ";

      // Add local output string to global event string for SYNTAX element.
      // The global event string is initialized in startSYNTAX and added to
      // by each of that element's children elements.  Events are fired with
      // the final event text in endSYNTAX.
      evText += evTextLocal;

      // Signal that any SELRESTRS or SELRESTR elements that are visited
      // immediately after this method are children of this NP element,
      // and should be displayed as such.
      npSelRestrs = true;

      // If the proper view options were supplied, display the text
      // for the beginning of this element (the local output string).
      // This output will be followed by any existing syntax restrictions
      // or selectional restrictions.
      if( Inspector.voSyntax )
         print( evTextLocal );
   }

   /**
    * Prints the text that corresponds to the closing of the NP
    * element in the VerbNet XML files.  Right now there is not
    * actually any printing required as all NP and SELRESTR/SYNRESTR
    * elements will have been printed before this point and there
    * is no closing text for the NP as a whole.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active NP element
    */
   static void endNP( Node n )
   {

      // Signal that any SELRESTRS or SELRESTR elements that are visited
      // immediately after this method are no longer necessarily
      // children of this NP element.
      npSelRestrs = false;

      // If the proper view options were supplied, display the text
      // for the closing of this element (nothing as of yet).
      if( Inspector.voSyntax )
      {
         // Text to display for end of NP element.
      }
   }

   /**
    * Prints the text that corresponds to the beginning of the SYNRESTRS
    * element in the VerbNet XML files.  The text is also appended
    * to the global event string that will be used in the events that
    * fire for the SYNTAX element.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active SYNRESTRS element
    */
   static void startSYNRESTRS( Node n )
   {

      // Grab all attributes from the element.
      String logic = ( ( Element ) n ).getAttribute( "logic" );

      // Decide whether or not the operator to be applied between multiple
      // SYNRESTR children elements is the 'Or' operator.  If the 'logic'
      // attribute of this element is not "or" then the operator is
      // assumed to be the 'And' operator.
      usingOr = logic.equals( "or" );

      // Construct local output string (simple-text representation) for this element.
      evTextLocal = "";

      // If there will be any syntax restrictions printed, then add
      // the opening caret.
      if( hasKids( n, "SYNRESTR" ) )
         evTextLocal = "<";

      // Add local output string to global event string for SYNTAX element.
      // The global event string is initialized in startSYNTAX and added to
      // by each of that element's children elements.  Events are fired with
      // the final event text in endSYNTAX.
      evText += evTextLocal;

      // Signal that there have not been any SYNRESTR elements encountered as of yet.
      hasBeenOther = false;

      // If the proper view options were supplied, display the text
      // for the beginning of this element (the local output string).
      if( Inspector.voSyntax && Inspector.voXSynRestr )
         print( evTextLocal );
   }

   /**
    * Prints the text that corresponds to the closing of the SYNRESTRS
    * element in the VerbNet XML files.  The text is also appended
    * to the global event string that will be used in the events that
    * fire for the SYNTAX element.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active SYNRESTRS element
    */
   static void endSYNRESTRS( Node n )
   {

      // Construct local output string (simple-text representation) for this element.
      evTextLocal = "";

      // If there were any syntax restrictions printed, then add
      // the closing caret.
      if( hasBeenOther )
         evTextLocal = "> ";

      // Add local output string to global event string for SYNTAX element.
      // The global event string is initialized in startSYNTAX and added to
      // by each of that element's children elements.  Events are fired with
      // the final event text in endSYNTAX.
      evText += evTextLocal;

      // If the proper view options were supplied, display the text
      // for the closing of this element (the local output string).
      if( Inspector.voSyntax && Inspector.voXSynRestr )
         print( evTextLocal );
   }

   /**
    * Prints the text that corresponds to the beginning of the SYNRESTR
    * element in the VerbNet XML files.  The text is also appended
    * to the global event string that will be used in the events that
    * fire for the SYNTAX element.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active SYNRESTR element
    */
   static void startSYNRESTR( Node n )
   {

      // Grab all attributes from the element.
      String value = ( ( Element ) n ).getAttribute( "Value" );
      String type  = ( ( Element ) n ).getAttribute( "type" );

      String op = "";         // Default is no preceding operator.

      // If there has already been a syntax restriction printed,
      // set an additional string to the appropriate operator.
      // Which operator to add is based off of the 'logic' attribute
      // of the SYNRESTRS element.
      if( hasBeenOther )
         op = usingOr ? " | " : " & ";

      // Construct local output string (simple-text representation) for this element.
      evTextLocal =  op + value + type;

      // Add local output string to global event string for SYNTAX element.
      // The global event string is initialized in startSYNTAX and added to
      // by each of that element's children elements.  Events are fired with
      // the final event text in endSYNTAX.
      evText += evTextLocal;

      // Signal that at least one SYNRESTR element has been encountered.
      hasBeenOther = true;

      // If the proper view options were supplied, display the text
      // for the beginning of this element (the local output string).
      if( Inspector.voSyntax && Inspector.voXSynRestr )
         print( evTextLocal );
   }

   /**
    * Prints the text that corresponds to the closing of the SYNRESTR
    * element in the VerbNet XML files.
    * Although it is specified for completeness, this method does
    * not do anything useful.  This is because <CODE>&lt;!ELEMENT SYNRESTR EMPTY></CODE>
    * in the DTD, so any "closing text" could just be placed at the
    * end of the {@link vn.Sweeper#startSYNRESTR(Node)} method.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active SYNRESTR element
    */
   static void endSYNRESTR( Node n )
   {

      // If the proper view options were supplied, display the text
      // for the closing of this element (nothing as of yet).
      if( Inspector.voSyntax && Inspector.voXSynRestr )
      {
         // Text to display for end of SYNRESTR element.
      }
   }

   /**
    * Prints the text that corresponds to the beginning of the PREP
    * element in the VerbNet XML files.  The text is also appended
    * to the global event string that will be used in the events that
    * fire for the SYNTAX element.  Selectional restriction output
    * may follow this method to show preposition classes.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active PREP element
    * @see vn.Sweeper#startSELRESTRS(Node)
    * @see vn.Sweeper#endSELRESTRS(Node)
    */
   static void startPREP( Node n )
   {

      // Grab all attributes from the element.
      String value = ( ( Element ) n ).getAttribute( "value" ).toLowerCase();

      // Construct local output string (simple-text representation) for this element.
      // The 'value' attribute will be the empty string if there are selectional
      // restrictions that will follow to specify a preposition class.
      evTextLocal = "{" + value.replaceAll( " ", ", " );

      // Add local output string to global event string for SYNTAX element.
      // The global event string is initialized in startSYNTAX and added to
      // by each of that element's children elements.  Events are fired with
      // the final event text in endSYNTAX.
      evText += evTextLocal;

      // Signal that any SELRESTRS or SELRESTR elements that are visited
      // immediately after this method are children of this PREP element,
      // and should be displayed as such.
      prepSelRestrs = true;

      // If the proper view options were supplied, display the text
      // for the beginning of this element (the local output string).
      // This output will be followed by any existing preposition classes,
      // which are implemented via selectional restrictions.
      if( Inspector.voSyntax )
         print( evTextLocal );
   }

   /**
    * Prints the text that corresponds to the closing of the PREP
    * element in the VerbNet XML files.  The text is also appended
    * to the global event string that will be used in the events that
    * fire for the SYNTAX element.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active PREP element
    */
   static void endPREP( Node n )
   {

      // Construct local output string (simple-text representation) for this element.
      evTextLocal = "} ";

      // Add local output string to global event string for SYNTAX element.
      // The global event string is initialized in startSYNTAX and added to
      // by each of that element's children elements.  Events are fired with
      // the final event text in endSYNTAX.
      evText += evTextLocal;

      // Signal that any SELRESTRS or SELRESTR elements that are visited
      // immediately after this method are no longer necessarily
      // children of this PREP element.
      prepSelRestrs = false;

      // If the proper view options were supplied, display the text
      // for the closing of this element (the local output string).
      if( Inspector.voSyntax )
         print( evTextLocal );
   }

   /**
    * Prints the text that corresponds to the beginning of the VERB
    * element in the VerbNet XML files.  The text is also appended
    * to the global event string that will be used in the events that
    * fire for the SYNTAX element.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active VERB element
    */
   static void startVERB( Node n )
   {

      // Construct local output string (simple-text representation) for this element.
      evTextLocal = "V ";

      // Add local output string to global event string for SYNTAX element.
      // The global event string is initialized in startSYNTAX and added to
      // by each of that element's children elements.  Events are fired with
      // the final event text in endSYNTAX.
      evText += evTextLocal;

      // If the proper view options were supplied, display the text
      // for the beginning of this element (the local output string).
      if( Inspector.voSyntax )
         print( evTextLocal );
   }

   /**
    * Prints the text that corresponds to the closing of the VERB
    * element in the VerbNet XML files.
    * Although it is specified for completeness, this method does
    * not do anything useful.  This is because <CODE>&lt;!ELEMENT VERB EMPTY></CODE>
    * in the DTD, so any "closing text" could just be placed at the
    * end of the {@link vn.Sweeper#startVERB(Node)} method.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active VERB element
    */
   static void endVERB( Node n )
   {

      // If the proper view options were supplied, display the text
      // for the closing of this element (nothing as of yet).
      if( Inspector.voSyntax )
      {
         // Text to display for end of VERB element.
      }
   }

   /**
    * Prints the text that corresponds to the beginning of the ADJ
    * element in the VerbNet XML files.  The text is also appended
    * to the global event string that will be used in the events that
    * fire for the SYNTAX element.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active ADJ element
    */
   static void startADJ( Node n )
   {

      // Construct local output string (simple-text representation) for this element.
      evTextLocal = "ADJ ";

      // Add local output string to global event string for SYNTAX element.
      // The global event string is initialized in startSYNTAX and added to
      // by each of that element's children elements.  Events are fired with
      // the final event text in endSYNTAX.
      evText += evTextLocal;

      // If the proper view options were supplied, display the text
      // for the beginning of this element (the local output string).
      if( Inspector.voSyntax )
         print( evTextLocal );
   }

   /**
    * Prints the text that corresponds to the closing of the ADJ
    * element in the VerbNet XML files.
    * Although it is specified for completeness, this method does
    * not do anything useful.  This is because <CODE>&lt;!ELEMENT ADJ EMPTY></CODE>
    * in the DTD, so any "closing text" could just be placed at the
    * end of the {@link vn.Sweeper#startADJ(Node)} method.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active ADJ element
    */
   static void endADJ( Node n )
   {

      // If the proper view options were supplied, display the text
      // for the closing of this element (nothing as of yet).
      if( Inspector.voSyntax )
      {
         // Text to display for end of ADJ element.
      }
   }

   /**
    * Prints the text that corresponds to the beginning of the ADV
    * element in the VerbNet XML files.  The text is also appended
    * to the global event string that will be used in the events that
    * fire for the SYNTAX element.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active ADV element
    */
   static void startADV( Node n )
   {

      // Construct local output string (simple-text representation) for this element.
      evTextLocal = "ADV ";

      // Add local output string to global event string for SYNTAX element.
      // The global event string is initialized in startSYNTAX and added to
      // by each of that element's children elements.  Events are fired with
      // the final event text in endSYNTAX.
      evText += evTextLocal;

      // If the proper view options were supplied, display the text
      // for the beginning of this element (the local output string).
      if( Inspector.voSyntax )
         print( evTextLocal );
   }

   /**
    * Prints the text that corresponds to the closing of the ADV
    * element in the VerbNet XML files.
    * Although it is specified for completeness, this method does
    * not do anything useful.  This is because <CODE>&lt;!ELEMENT ADV EMPTY></CODE>
    * in the DTD, so any "closing text" could just be placed at the
    * end of the {@link vn.Sweeper#startADV(Node)} method.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active ADV element
    */
   static void endADV( Node n )
   {

      // If the proper view options were supplied, display the text
      // for the closing of this element (nothing as of yet).
      if( Inspector.voSyntax )
      {
         // Text to display for end of ADV element.
      }
   }

   /**
    * Prints the text that corresponds to the beginning of the LEX
    * element in the VerbNet XML files.  The text is also appended
    * to the global event string that will be used in the events that
    * fire for the SYNTAX element.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active LEX element
    */
   static void startLEX( Node n )
   {

      // Grab all attributes from the element.
      String value = ( ( Element ) n ).getAttribute( "value" );

      // Construct local output string (simple-text representation) for this element.
      evTextLocal = "(" + value + ") ";

      // Add local output string to global event string for SYNTAX element.
      // The global event string is initialized in startSYNTAX and added to
      // by each of that element's children elements.  Events are fired with
      // the final event text in endSYNTAX.
      evText += evTextLocal;

      // If the proper view options were supplied, display the text
      // for the beginning of this element (the local output string).
      if( Inspector.voSyntax )
         print( evTextLocal );
   }

   /**
    * Prints the text that corresponds to the closing of the LEX
    * element in the VerbNet XML files.
    * Although it is specified for completeness, this method does
    * not do anything useful.  This is because <CODE>&lt;!ELEMENT LEX EMPTY></CODE>
    * in the DTD, so any "closing text" could just be placed at the
    * end of the {@link vn.Sweeper#startLEX(Node)} method.
    *
    * @param n the {@link org.w3c.dom.Node} object representing
    *        the active LEX element
    */
   static void endLEX( Node n )
   {

      // If the proper view options were supplied, display the text
      // for the closing of this element (nothing as of yet).
      if( Inspector.voSyntax )
      {
         // Text to display for end of LEX element.
      }
   }

   //////////////////////////////////
   // Supplemental Sweeper Methods //
   //////////////////////////////////

   /**
    * Prints the text for all the members in this class.
    * The members would have just been printed in {@link vn.Sweeper#startMEMBER(Node)}
    * as they were encountered but in order to implement the sorting feature, all the members
    * need to be visited and saved before the printing can occur.
    * The body of the loop follows the standard format of a single
    * sweeper method, as described in {@link vn.Sweeper} class's description.
    *
    * @see vn.Sweeper#startMEMBER(Node)
    * @see vn.Sweeper#endMEMBERS(Node)
    * @see vn.Sweeper#iprintln(String)
    * @see vn.Inspector#incrementTagCounter(String)
    */
   private static void printMembers()
   {

      // Print all the member's (which are already in sorted order).
      for( int v = 0; v < members.size(); v++ )
      {
         MemberNode mn = ( MemberNode ) members.get( v );

         // Grab all attributes from the node stored in the array.
         String vbName = mn.verb;
         String wn     = mn.wn;

         // Construct the full text needed for the event text.
         String fullText = "MEMBER: " + mn.verb + " (wn=" + mn.wn + ")";

         // Construct local output string (simple-text representation) for this element.
         if( Inspector.voWordNet )
            evTextLocal = fullText;

         else
            evTextLocal = "MEMBER: " + mn.verb;

         // Initialize the global event string to the local output string since this
         // is the first text to display on the line.
         evText = fullText;

         // If the proper view options were supplied, display the text
         // for the beginning of this element (the local output string).
         if( Inspector.voMember )
         {

            // Reprint labels for all files, classes, subclasses, and frames in which
            // this member is contained.
            if( Inspector.flReplicate )
               replicateLabels();

            // Print the local output string with proper indentation.
            iprintln( evTextLocal );

            // Increment the counter for this element.
            Inspector.incrementTagCounter( "MEMBER" );
         }

         // Fire both the start and end events for the MEMBER element.  See note
         // in EventManager class for more information on why these fire back-to-back.
         EventManager.fireEventMaybe( EventManager.EVENT_MEMBER, EventManager.EVENT_START, curFile, curClass, evText, mn.node, null );
         EventManager.fireEventMaybe( EventManager.EVENT_MEMBER, EventManager.EVENT_END,   curFile, curClass, evText, mn.node, null );
      }
   }

   /**
    * Prints all verb-frame pairs if the Inspector is running in verb-frame
    * pair mode.  This method is called once a FRAMES
    * element has completed, signalling the point right before the start
    * of a new class or subclass.  This is the point when the verb-frame
    * pairs should be printed.  The {@link vn.Sweeper#members} array has already been properly
    * loaded and all the frames visited up to this point since the main
    * (root) class has been given to the {@link vn.Sweeper} class via
    * {@link vn.Sweeper#setFrameList(ArrayList)}.  This method either visits verb-frame
    * pairs for this class or subclass in verb-major order or frame-major order depending
    * on the "invert-verb-frame-pair-order" flag (-v, {@link vn.Inspector#flVFPairsInvert}).
    *
    * @see vn.Sweeper#iprint(String)
    * @see vn.Sweeper#endFRAMES(Node)
    * @see vn.Sweeper#startMEMBER(Node)
    * @see vn.Sweeper#curVFFrameList
    * @see vn.Inspector#processNodeByPairs(Node, ArrayList)
    */
   private static void printVerbFramePairs()
   {

      // If there are no verb-frame pairs, show the absence label
      // if the "no-absence" flag (-z) was not provided and view
      // verb-frame pairs is active.
      if( members.size() == 0 || curVFFrameList.size() == 0 )
      {
         if( !Inspector.flNoAbsence && Inspector.voVFPairs )
         {

            // Reprint labels for all files, classes, subclasses, and frames in which
            // this verb-frame pair absence label is contained.
            if( Inspector.flReplicate )
               replicateLabels();

            iprint( "<NO VF-PAIRS: " );

            if( members.size() != 0 )
               print( "NO FRAMES" );

            else if( curVFFrameList.size() != 0 )
               print( "NO MEMBERS" );

            else
               print( "NO MEMBERS NOR FRAMES" );

            println( ">" );
         }

         return;           // Stop the method here.
      }

      // If the user wants to invert the normal order...
      //   FRAME1 VERB1
      //   FRAME1 VERB2
      //   FRAME2 VERB1
      //   FRAME2 VERB2
      if( Inspector.flVFPairsInvert )
      {

         // Cycle through all the frames.  The frames in the list are all
         // those accumulated since the main class of the file.  So if
         // the current class is a subclass at depth 2, the frames list contains
         // frames from three classes and subclasses.
         for( int f = 0; f < curVFFrameList.size(); f++ )
         {
            curVFFrameNode = ( Node ) curVFFrameList.get( f );

            // Cycle through all the members.  The members in the list will
            // only represent the members in the current class or subclass.
            for( int v = 0; v < members.size(); v++ )
            {
               MemberNode mn = ( MemberNode ) members.get( v );

               // Set the verb information for this pair to class level
               // variables so they are available when the pair is processed.
               curVFVerbName   = mn.verb;
               curVFVerbWN     = mn.wn;
               curVFMemberNode = mn.node;

               // Ask the Inspector class to process the frame node in this
               // pair, now that the verb information for this pair has
               // been set at a class level.  This will make the
               // startDESCRIPTION method print things in a verb-frame pair
               // format instead of the standard frame format.
               Inspector.processNodeByPairs( curVFFrameNode, curVFFrameList );
            }
         }
      }

      // Else if normal order is to be used...
      //   VERB1 FRAME1
      //   VERB1 FRAME2
      //   VERB2 FRAME1
      //   VERB2 FRAME2
      else
      {

         // Cycle through all the members.  The members in the list will
         // only represent the members in the current class or subclass.
         for( int v = 0; v < members.size(); v++ )
         {
            MemberNode mn = ( MemberNode ) members.get( v );

            // Set the verb information for this pair to class level
            // variables so they are available when the pair is processed.
            curVFVerbName   = mn.verb;
            curVFVerbWN     = mn.wn;
            curVFMemberNode = mn.node;

            // Cycle through all the frames.  The frames in the list are all
            // those accumulated since the main class of the file.  So if
            // the current class is a subclass at depth 2, the frames list contains
            // frames from three classes and subclasses.
            for( int f = 0; f < curVFFrameList.size(); f++ )
            {
               curVFFrameNode = ( Node ) curVFFrameList.get( f );

               // Ask the Inspector class to process the frame node in this
               // pair, now that the verb information for this pair has
               // been set at a class level.  This will make the
               // startDESCRIPTION method print things in a verb-frame pair
               // format instead of the standard frame format.
               Inspector.processNodeByPairs( curVFFrameNode, curVFFrameList );
            }
         }
      }
   }
}

