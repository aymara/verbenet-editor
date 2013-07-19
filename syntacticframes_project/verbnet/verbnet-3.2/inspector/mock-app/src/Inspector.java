
//////////////////////////////
// The Inspector            //
// Mock Application         //
// University of Colorado   //
// Fall 2006                //
//////////////////////////////

package vn;

import java.util.*;
import java.io.*;
import java.lang.reflect.*;
import javax.xml.parsers.*;
import org.w3c.dom.*;

/**
 * The driver class for the Inspector.  This class parses the command-line arguments
 * given to it and scans the VerbNet XML files while taking the desired actions.
 * The arguments are used to set flag and view option variables that both
 * this class and the {@link vn.Sweeper} class use to customize the output.
 * The general usage is: <BR>
 * <PRE>&nbsp;&nbsp;&nbsp;java vn.Inspector [flags] &lt;x> [-V &lt;v>] [-O &lt;o>]</PRE>
 * See the usage note (<CODE>java vn.Inspector -?</CODE>) for full details.
 * <BR><BR>The Inspector has two basic output modes: normal output mode, and class
 * hierarchy mode.  The first is the default action to take when scanning the XML
 * files - print those elements specified by the view option operator (-V operator).
 * The second is to just print the class hierarchy of the selected XML files and
 * is activated by using the -c option.
 * <BR><BR>
 * The default action is to process all XML files in the XML input directory.  The
 * -O operator allows the user to limit the processing to specific XML files, in
 * order to avoid processing unwanted files.
 * <BR><BR>
 * Errors are sent to <B>stderr</B>.  All other output is sent to <B>stdout</B>.  There
 * are very few errors generated in the Inspector and usually deal with validating
 * the command-line parameters.  If using the Inspector as a stand-alone application you
 * may use your shell to redirect the output to a file:
 * <PRE> sh/bash/csh/tcsh:
 *    java vn.Inspector verbnet-xml/ -Vfcm -Och > output.txt</PRE>
 * However, if you are embedding these classes in an application, then you can
 * utilize the {@link java.lang.System#setOut(PrintStream)} method to redirect stdout
 * to an external file from within the Java code.  One would most likely call this
 * method in the 'start' event for the program in
 * {@link vn.EventManager#fireEvent(int, int, String, String, String, Element, Element)}.
 * <BR><BR>
 * For information about adding command line parameters when extending the Inspector into
 * a custom application, refer to the last section
 * of the <A href='http://verbs.colorado.edu/verb-index/inspector/extguide.html' target='_blank'>Extension Guide</A>.
 * <BR><BR>
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
public class Inspector
{

   ////////////
   // Fields //
   ////////////

   // ------------------------- //
   // -- XML Input Directory -- //
   // ------------------------- //

   /**
    * The directory where the VerbNet XML files are located.  This
    * is the only required argument to the Inspector.  The path supplied
    * must exist, be a directory, and be readable by the Inspector.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Inspector#printHeader()
    */
   private static File vnDir;

   /**
    * A list of just the XML files located in the XML input directory.
    * A filter is used ({@link vn.Inspector.MyFilter}) to list just
    * the XML files.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Inspector#performInspection()
    */
   private static File[] xmlFiles;

   // ----------- //
   // -- Flags -- //
   // ----------- //

   /**
    * A string representation of all of the flags supplied on the
    * command line.  All flags can be separate from one another
    * or combined into a single command line token.  This
    * string accumulates all the flags supplied on the command line
    * so they can all be printed out nicely in the header.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Inspector#printHeader()
    */
   static String flags;

   /**
    * A flag set in {@link vn.Inspector#analyzeArguments(String[])} and
    * used to indicate that the user would like to see the help/usage
    * message.  This flag is set with the -? option.  If this option
    * is supplied, the program prints the usage message and exits.
    * No further processing occurs.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    */
   static boolean flHelp;

   /**
    * A flag set in {@link vn.Inspector#analyzeArguments(String[])} and
    * used to indicate that the user would like to see the key for the
    * thematic role and syntax restrictions.  This flag is set
    * with the -k option.  If this option is supplied, the program prints
    * the key and exits.  No further processing occurs.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    */
   static boolean flKey;

   /**
    * A flag set in {@link vn.Inspector#analyzeArguments(String[])} and
    * used to indicate that the user would like to see the class hierarchy.
    * This flag is set with the -c option.  If this option is supplied, the
    * program prints the class hierarchy and exits.  No further processing
    * occurs.  The -V operator is ignored and the -m option is not honored.
    * Only final counts can be seen when viewing the class hierarchy.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Inspector#processNode(Node)
    * @see vn.Sweeper#startVNCLASS(Node)
    * @see vn.Sweeper#classHierarchyPrint(Element, int)
    */
   static boolean flClassH;

   /**
    * A flag set in {@link vn.Inspector#analyzeArguments(String[])} and
    * used to indicate that the user would like to suppress the header
    * information that is printed before normal output and class hierarchy.
    * This flag is set with the -h option.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Inspector#main(String[])
    */
   static boolean flNoHeader;

   /**
    * A flag set in {@link vn.Inspector#analyzeArguments(String[])} and
    * used to indicate that the user would like to suppress the final count
    * information that is printed after normal output and class hierarchy.
    * This flag is set with the -n option.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Inspector#main(String[])
    */
   static boolean flNoFinalCounts;

   /**
    * A flag set in {@link vn.Inspector#analyzeArguments(String[])} and
    * used to indicate that the user would like to view count information
    * for each class and subclass that is displayed in normal output.
    * This flag is set with the -m option.  This option has no effect
    * when the class hierarchy is printed.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Inspector#incrementTagCounter(String, int)
    * @see vn.Sweeper#endFRAMES(Node)
    * @see vn.Inspector#printTagCounts(boolean)
    */
   static boolean flClassCounts;

   /**
    * A flag set in {@link vn.Inspector#analyzeArguments(String[])} and
    * used to indicate that the user would like to view those counts
    * in both class counts and final counts that are equal to zero in
    * addition to the non-zero counts.  This flag is set with the -0 option.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Inspector#printTagCounts(boolean)
    * @see vn.Inspector#printTagCount(HashMap, String)
    */
   static boolean flZeroCounts;

   /**
    * A flag set in {@link vn.Inspector#analyzeArguments(String[])} and
    * used to indicate that the user would like each file name to be
    * printed to stderr as it is encountered. This flag is set with the
    * -w option.  This option exists only as a convenience so that if
    * stdout is being redirected to a file, one can still view the progress
    * of the Inspector.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Inspector#performInspection()
    */
   static boolean flErrProgress;

   /**
    * A flag set in {@link vn.Inspector#analyzeArguments(String[])} and
    * used to indicate that the user would like the verbs in the members
    * section sorted.  This flag is set with the -s option.  If the
    * Inspector is running in verb-frame pair mode (-q or -Vq supplied) then
    * the verb-frame pairs will also be sorted by the verb.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Sweeper#startMEMBER(Node)
    * @see vn.Sweeper#printMembers()
    */
   static boolean flSortMembers;

   /**
    * A flag set in {@link vn.Inspector#analyzeArguments(String[])} and
    * used to indicate that the user would like both the normal output
    * and class hierarchy indented.  This flag is set with the -i option.
    * Indentation occurs with files, classes, subclasses, and frames.
    * All output which is logically under these elements is indented over
    * one additional indent width.  The indent width is 3 spaces.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Sweeper#iprintln(String)
    * @see vn.Sweeper#iprint(String)
    * @see vn.Sweeper#classHierarchyPrint(Element, int)
    * @see vn.Sweeper#INDENT_WIDTH
    */
   static boolean flIndent;

   /**
    * A flag set in {@link vn.Inspector#analyzeArguments(String[])} and
    * used to indicate that the user would like to supress the absence
    * labels in the normal output and class hierarchy.  This flag is set
    * with the -z option.  An absence label is one of the following:
    * &lt;NO SUBCLASSES>, &lt;NO MEMBERS>, &lt;NO THEMROLES>,
    * &lt;NO FRAMES>, or &lt;NO <NOBR>VF-PAIRS</NOBR>: reason>.  The NO SUBCLASSES label
    * is only printed in the class hierarchy.  The NO VF-PAIRS label
    * is paired with the reason why there are no verb-frame pairs for
    * that class: no members, no frames, or both.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Sweeper#classHierarchyPrint(Element, int)
    * @see vn.Sweeper#startMEMBERS(Node)
    * @see vn.Sweeper#startTHEMROLES(Node)
    * @see vn.Sweeper#startFRAMES(Node)
    * @see vn.Sweeper#printVerbFramePairs()
    */
   static boolean flNoAbsence;

   /**
    * A flag set in {@link vn.Inspector#analyzeArguments(String[])} and
    * used to indicate that the user would like the Inspector to run
    * in verb-frame pair mode.  This flag is set with the -q option.
    * The -Vq option implies the -q option.  If the -q is set, then
    * -Vm or -Vr imply -Vq.<BR><BR>Essentially a verb is a member of a class
    * because it can participate in each of the frames of that class
    * and each of the frames in ancestor classes.  So if there are
    * 5 members in a main class with 4 frames, then there are 20
    * verb-frame pairs for that class alone.  A verb-frame pair
    * means <I>this verb can be used like this</I>.  If a subclass
    * of that class contains 2 members and 2 frames, then there are
    * <U>2 members x (2+4) frames = 12 verb-frame pairs</U>, since
    * members can participate in all frames contained in ancestor classes.
    * <BR><BR>The processing changes in that a different recursive method
    * is used in the driver ({@link vn.Inspector#processNodeByPairs(Node, ArrayList)}
    * instead of {@link vn.Inspector#processNode(Node)}).  Also, nothing besides
    * thematic roles is printed until the closing of the FRAMES element.
    * At which point, {@link vn.Sweeper#printVerbFramePairs} is called to
    * print all the pairs.<BR><BR>Regardless of what is sent to stdout, there are
    * almost 30,000 verb-frame pairs in VerbNet, so any execution with the
    * options -q or -Vq could take a few moments (unless you are just looking
    * at a subset of the XML files with the -O operator).
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Inspector#performInspection()
    * @see vn.Sweeper#startMEMBERS(Node)
    * @see vn.Sweeper#endMEMBERS(Node)
    * @see vn.Sweeper#startFRAMES(Node)
    * @see vn.Sweeper#endFRAMES(Node)
    * @see vn.Sweeper#startFRAME(Node)
    * @see vn.Sweeper#endFRAME(Node)
    * @see vn.Sweeper#startDESCRIPTION(Node)
    * @see vn.Sweeper#curVFFrameList
    */
   static boolean flVFPairs;

   /**
    * A flag set in {@link vn.Inspector#analyzeArguments(String[])} and
    * used to indicate that the user would like the Sweeper to visit
    * verb-frame pairs in frame-major order instead of a verb-major
    * order.  This flag is set with the -v option.  This option is
    * ineffective unless -q or -Vq is supplied.  To illustrate this
    * option, here is a small table:<BR><BR>
    * <TABLE border=1 cellpadding=5>
    *   <TR><TD align='center'>Verb Major</TD><TD align='center'>Frame Major</TD></TR>
    *   <TR><TD>VERB 1 - FRAME 1<BR>VERB 1 - FRAME 2<BR>VERB 2 - FRAME 1<BR>VERB 2 - FRAME 2</TD>
    *   <TD>FRAME 1 - VERB 1<BR>FRAME 1 - VERB 2<BR>FRAME 2 - VERB 1<BR>FRAME 2 - VERB 2</TD></TR>
    * </TABLE>
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Sweeper#printVerbFramePairs()
    */
   static boolean flVFPairsInvert;

   /**
    * A flag set in {@link vn.Inspector#analyzeArguments(String[])} and
    * used to suppress the firing of all events.  If this flag is set,
    * the Inspector is only acting as a VerbNet viewer, printing out
    * those elements of the XML files as specified by the -V operator.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    */
   static boolean flSuppressEvents;

   /**
    * A flag set in {@link vn.Inspector#analyzeArguments(String[])} and
    * used to print all the labels that represent additional nesting
    * (file, class, subclass, and frame) before every element that is printed.  The
    * output becomes abundant but this option is provided only for added
    * interoperability with grep.  The additional labels that are printed
    * are still dependent on view options, but do not affect class or
    * final counts.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    */
   static boolean flReplicate;

   // --------------- //
   // -- Operators -- //
   // --------------- //

   /**
    * All operators used on the command line.  Right now there are only
    * two of them: view options and only-these-files.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    */
   private static final String ALL_OPER_CHARS = "VO";

   // --------------------------- //
   // -- View Options (-V <v>) -- //
   // --------------------------- //

   /**
    * All view options.  These are all the letters which may comprise &lt;v>,
    * the argument to the -V operator.  They may be listed in any order.
    * This string is used to validate and set the appropriate view options in
    * {@link vn.Inspector#analyzeArguments(String[])}.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    */
   private static final String ALL_VIEW_OPTS = "fcnmwturexyzsaqb";

   /**
    * A string representation of all of the view options supplied on the
    * command line.  All view options can be provided in separate -V
    * operators or combined into a single -V operator.  This
    * string accumulates all the view options supplied on the command line
    * so they can all be printed out nicely in the header.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Inspector#printHeader()
    */
   static String viewOpts;

   /**
    * A view option set in {@link vn.Inspector#analyzeArguments(String[])} and
    * used to display file names in normal output mode.  This view
    * option is set with the letter <CODE>f</CODE>.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Sweeper#startVNCLASS(Node)
    * @see vn.Sweeper#endVNCLASS(Node)
    */
   static boolean voFileName;

   /**
    * A view option set in {@link vn.Inspector#analyzeArguments(String[])} and
    * used to display class and subclass names in normal output mode.  This view
    * option is set with the letter <CODE>c</CODE>.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Sweeper#startVNCLASS(Node)
    * @see vn.Sweeper#endVNCLASS(Node)
    * @see vn.Sweeper#startVNSUBCLASS(Node)
    * @see vn.Sweeper#endVNSUBCLASS(Node)
    */
   static boolean voClassName;

   /**
    * A view option set in {@link vn.Inspector#analyzeArguments(String[])} and
    * used to display member and frame counts in normal output mode.  This view
    * option is set with the letter <CODE>n</CODE>.  For this view option to
    * have any effect, the -Vc option must also be supplied.  Member and frame
    * counts include only the class being processed, not ancestor or
    * descendant classes.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Sweeper#startVNCLASS(Node)
    * @see vn.Sweeper#startVNSUBCLASS(Node)
    */
   static boolean voCount;

   /**
    * A view option set in {@link vn.Inspector#analyzeArguments(String[])} and
    * used to display member (verbs) in normal output mode.  This view
    * option is set with the letter <CODE>m</CODE>.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Sweeper#startMEMBERS(Node)
    * @see vn.Sweeper#endMEMBER(Node)
    * @see vn.Sweeper#printMembers()
    */
   static boolean voMember;

   /**
    * A view option set in {@link vn.Inspector#analyzeArguments(String[])} and
    * used to display WordNet senses in normal output mode.  This view
    * option is set with the letter <CODE>w</CODE>.  For this view option to
    * have any effect, the -Vm option must also be supplied.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Sweeper#startDESCRIPTION(Node)
    * @see vn.Sweeper#printMembers()
    */
   static boolean voWordNet;

   /**
    * A view option set in {@link vn.Inspector#analyzeArguments(String[])} and
    * used to display thematic roles in normal output mode.  This view
    * option is set with the letter <CODE>t</CODE>.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Sweeper#startTHEMROLES(Node)
    * @see vn.Sweeper#endTHEMROLES(Node)
    * @see vn.Sweeper#startTHEMROLE(Node)
    * @see vn.Sweeper#endTHEMROLE(Node)
    * @see vn.Sweeper#startSELRESTRS(Node)
    * @see vn.Sweeper#endSELRESTRS(Node)
    * @see vn.Sweeper#startSELRESTR(Node)
    * @see vn.Sweeper#endSELRESTR(Node)
    */
   static boolean voThemRole;

   /**
    * A view option set in {@link vn.Inspector#analyzeArguments(String[])} and
    * used to display selectional restrictions for thematic roles in normal output
    * mode.  This view option is set with the letter <CODE>u</CODE>.  For this view
    * option to have any effect, the -Vt option must also be supplied.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Sweeper#startSELRESTRS(Node)
    * @see vn.Sweeper#endSELRESTRS(Node)
    * @see vn.Sweeper#startSELRESTR(Node)
    * @see vn.Sweeper#endSELRESTR(Node)
    */
   static boolean voTRSelRestr;

   /**
    * A view option set in {@link vn.Inspector#analyzeArguments(String[])} and
    * used to display frame descriptions in normal output mode.  This view
    * option is set with the letter <CODE>r</CODE>.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Sweeper#startFRAMES(Node)
    * @see vn.Sweeper#endFRAMES(Node)
    * @see vn.Sweeper#startFRAME(Node)
    * @see vn.Sweeper#endFRAME(Node)
    * @see vn.Sweeper#startDESCRIPTION(Node)
    * @see vn.Sweeper#endDESCRIPTION(Node)
    */
   static boolean voFrame;

   /**
    * A view option set in {@link vn.Inspector#analyzeArguments(String[])} and
    * used to display examples in normal output mode.  This view
    * option is set with the letter <CODE>e</CODE>.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Sweeper#startEXAMPLES(Node)
    * @see vn.Sweeper#endEXAMPLES(Node)
    * @see vn.Sweeper#startEXAMPLE(Node)
    * @see vn.Sweeper#endEXAMPLE(Node)
    */
   static boolean voExample;

   /**
    * A view option set in {@link vn.Inspector#analyzeArguments(String[])} and
    * used to display syntax in normal output mode.  This view
    * option is set with the letter <CODE>x</CODE>.  The format used is
    * congruent to the Unified Verb Index save for the noun phrase
    * thematic roles, which are preceded by a % sign instead of underline.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Sweeper#startSELRESTRS(Node)
    * @see vn.Sweeper#endSELRESTRS(Node)
    * @see vn.Sweeper#startSELRESTR(Node)
    * @see vn.Sweeper#endSELRESTR(Node)
    * @see vn.Sweeper#startSYNTAX(Node)
    * @see vn.Sweeper#endSYNTAX(Node)
    * @see vn.Sweeper#startNP(Node)
    * @see vn.Sweeper#endNP(Node)
    * @see vn.Sweeper#startSYNRESTRS(Node)
    * @see vn.Sweeper#endSYNRESTRS(Node)
    * @see vn.Sweeper#startSYNRESTR(Node)
    * @see vn.Sweeper#endSYNRESTR(Node)
    * @see vn.Sweeper#startPREP(Node)
    * @see vn.Sweeper#endPREP(Node)
    * @see vn.Sweeper#startVERB(Node)
    * @see vn.Sweeper#endVERB(Node)
    * @see vn.Sweeper#startADJ(Node)
    * @see vn.Sweeper#endADJ(Node)
    * @see vn.Sweeper#startADV(Node)
    * @see vn.Sweeper#endADV(Node)
    * @see vn.Sweeper#startLEX(Node)
    * @see vn.Sweeper#endLEX(Node)
    */
   static boolean voSyntax;

   /**
    * A view option set in {@link vn.Inspector#analyzeArguments(String[])} and
    * used to display the current file in normal output mode.  This view
    * option is set with the letter <CODE>y</CODE>.  For this view
    * option to have any effect, the -Vx option must also be supplied.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Sweeper#startSYNRESTRS(Node)
    * @see vn.Sweeper#endSYNRESTRS(Node)
    * @see vn.Sweeper#startSYNRESTR(Node)
    * @see vn.Sweeper#endSYNRESTR(Node)
    */
   static boolean voXSynRestr;

   /**
    * A view option set in {@link vn.Inspector#analyzeArguments(String[])} and
    * used to display selectional restrictions for noun phrases in normal output
    * mode.  This view option is set with the letter <CODE>z</CODE>.  For this view
    * option to have any effect, the -Vx option must also be supplied.  Preposition
    * classes also use selectional restrictions but are not affected by this
    * view option.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Sweeper#startSELRESTRS(Node)
    * @see vn.Sweeper#endSELRESTRS(Node)
    * @see vn.Sweeper#startSELRESTR(Node)
    * @see vn.Sweeper#endSELRESTR(Node)
    */
   static boolean voXSelRestr;

   /**
    * A view option set in {@link vn.Inspector#analyzeArguments(String[])} and
    * used to display semantics in normal output mode.  This view
    * option is set with the letter <CODE>s</CODE>.  One line of text is
    * printed for each predicate.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Sweeper#startSEMANTICS(Node)
    * @see vn.Sweeper#endSEMANTICS(Node)
    * @see vn.Sweeper#startPRED(Node)
    * @see vn.Sweeper#endPRED(Node)
    * @see vn.Sweeper#startARGS(Node)
    * @see vn.Sweeper#endARGS(Node)
    * @see vn.Sweeper#startARG(Node)
    * @see vn.Sweeper#endARG(Node)
    */
   static boolean voSemantics;

   /**
    * A view option set in {@link vn.Inspector#analyzeArguments(String[])} and
    * used to enable all basic view options in normal output mode.  This view
    * option is set with the letter <CODE>a</CODE>.  All basic view options
    * include: <CODE>fcnmwturexyzs</CODE>.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    */
   static boolean voAll;

   /**
    * A view option set in {@link vn.Inspector#analyzeArguments(String[])} and
    * used to display verb-frame pair descriptions in normal output mode.  This view
    * option is set with the letter <CODE>q</CODE>.  This forces the Inspector
    * to run in verb-frame pair mode (see {@link vn.Inspector#flVFPairs}).  This
    * view option will display the line which shows the the verb and the frame
    * description.  Examples, syntax, and semantics will follow this line, if
    * their corresponding view options are supplied.  Although the flag
    * {@link vn.Inspector#flVFPairs} creates most of the processing changes
    * for verb-frame pairs, this flag makes sure the counters get incremented
    * if a verb-frame pair description is printed and decides whether or not
    * to print the absence label if a class or subclass has no verb-frame pairs.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Sweeper#startFRAME(Node)
    * @see vn.Sweeper#printVerbFramePairs()
    */
   static boolean voVFPairs;

   /**
    * A view option set in {@link vn.Inspector#analyzeArguments(String[])} and
    * used to display non-standard attributes in normal output mode.  This view
    * option is set with the letter <CODE>b</CODE>.  The non-standard attributes
    * that are included are: DESCRIPTION/descriptionNumber, DESCRIPTION/xtag, and
    * ARG/type.  So to view as much of the XML files as possible, use -Vab.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Sweeper#startDESCRIPTION(Node)
    * @see vn.Sweeper#startARG(Node)
    */
   static boolean voComplete;

   // ------------------------------- //
   // -- Only These Files (-O <o>) -- //
   // ------------------------------- //

   /**
    * The files that the user has requested to see.  This string remains
    * <CODE>null</CODE> if the user did not specify the -O operator.  If the user
    * did not specify the -O operator, then all the XML files in the input
    * directory are proessed.  If the -O operator is supplied, its argument
    * limits which XML files that are actually processed.  Only those files whose
    * names start with one of the tokens supplied to -O will be processed.
    * For example, a possible value for this variable could be "ch,care" if
    * the user supplied the option "-Och,care".   If one of the tokens is not
    * the beginning of any XML file name (i.e. -Oxyz), then it is ignored.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Inspector#printHeader()
    * @see vn.Inspector#performInspection()
    */
   private static String onlyTheseFiles;

   /**
    * An array representing all the tokens supplied to the -O operator.
    * The argument to the -O operator is a comma-delimited list of tokens.
    * That list is broken apart into an array inside
    * {@link vn.Inspector#analyzeArguments(String[])}.  Later, each
    * XML file is compared against the elements in this array.  If its name
    * starts with any one of the elements of this array, it is processed.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Inspector#performInspection()
    */
   private static String[] allOnlyFiles;

   // ------------------ //
   // -- Tag Counters -- //
   // ------------------ //

   /**
    * A map which ties an integer to a string.  In our case the integer
    * is the number of times that the string has been encountered and the
    * string is the label preceding each line of simple text sent
    * to stdout.  These labels are: FILE, CLASS, SUBCLASS, MEMBER,
    * THEMROLE, FRAME, EXAMPLE, SYNTAX, SEMANTIC PRED, VF-PAIR.  Counters
    * hold only those labels that are actually printed to stdout,
    * not those only for which events are fired.
    * This counter holds the counts for each label (or "tag") for a given
    * class or subclass ("class counts").  It is reset right before each new class or
    * subclass begins.  This counter is only active if the -m option is supplied.
    *
    * @see vn.Inspector#incrementTagCounter(String, int)
    * @see vn.Inspector#clearClassTagCounter()
    * @see vn.Inspector#printTagCounts(boolean)
    */
   private static HashMap tagCounterClass = new HashMap();

   /**
    * A map which ties an integer to a string.  In our case the integer
    * is the number of times that the string has been encountered and the
    * string is the label preceding each line of simple text sent
    * to stdout.  These labels are: FILE, CLASS, SUBCLASS, MEMBER,
    * THEMROLE, FRAME, EXAMPLE, SYNTAX, SEMANTIC PRED, VF-PAIR.  Counters
    * hold only those labels that are actually printed to stdout,
    * not those only for which events are fired.
    * This counter holds the counts for each label (or "tag") for the
    * entire execution of the program ("final counts").
    *
    * @see vn.Inspector#incrementTagCounter(String, int)
    * @see vn.Inspector#printTagCounts(boolean)
    */
   private static HashMap tagCounterGlobal = new HashMap();

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
    * Used as shorthand for <CODE>System.err.println</CODE>.
    *
    * @param s the string to print
    * @see     java.io.PrintStream#println(String)
    */
   private static void eprintln( String s ) { System.err.println( s ); }

   /**
    * Used as shorthand for <CODE>System.err.print</CODE>.
    *
    * @param s the string to print
    * @see     java.io.PrintStream#print(String)
    */
   private static void eprint( String s ) { System.err.print( s ); }

   /**
    * Concatenates all the elements in a string array, separated by spaces.
    *
    * @param array the string array
    * @return a single string that is the concatenation of all the given
    *         array elements with spaces between each pair of elements
    * @see vn.Inspector#main(String[])
    */
    private static String together( String[] array )
    {
      String all = "";

      for( int a = 0; a < array.length; a++ )
         all += array[ a ] + " ";

      return all;
    }

   /////////////////
   // Constructor //
   /////////////////

   /**
    * This constructor is private because the class is not intended to ever
    * be instantiated.  The Inspector is a very procedural process and
    * thus all the members are static.
    */
   private Inspector() {}

   ////////////////
   // Main & Run //
   ////////////////

   /**
    * The main method of the program.  It first scans the command line
    * and then performs the processing of the XML files.
    *
    * @param args the command line arguments supplied to the Inspector
    * @see vn.Inspector#analyzeArguments(String[])
    * @see vn.Inspector#performInspection()
    * @see vn.Inspector#printHeader()
    * @see vn.Inspector#printTagCounts(boolean)
    */
   public static void main( String[] args )
   {
      boolean fireEndEvent = false;

      try
      {

         // Scan the command line.
         analyzeArguments( args );

         // Fire the 'start' event for the program.
         EventManager.fireEventMaybe( EventManager.EVENT_PROGRAM, EventManager.EVENT_START, null, null, together( args ), null, null );

         // Since the 'start' event for the program fired, make sure the
         // 'end' event fires now.
         fireEndEvent = true;

         // Print the header if the user doesn't want to suppress it.
         if( !flNoHeader )
            printHeader();

         // Process all the desired XML files.
         performInspection();

         // Print the final counts if the user doesn't want to suppress it.
         if( !flNoFinalCounts )
            printTagCounts( false );
      }

      // There was a problem with the command line...
      catch( InvalidCommandLineArgumentException iclae )
      {
         eprintln( "ERROR: " + iclae.getMessage() );
         eprintln( "" );
         eprintln( "Usage: java Inspector [flags] <x> [-V <v>] [-O <o>]" );
         eprintln( "Type 'java Inspector -?' for complete usage information." );
      }

      // The user supplied -? on the command line...
      catch( UserWantsHelpMessage uwhm )
      {
         printUsage();
      }

      // The user supplied -k on the command line...
      catch( UserWantsKey uwk )
      {
         printKey();
      }

      // There was an error with the supplied XML input directory...
      catch( InvalidPathException ipe )
      {
         eprintln( "ERROR: " + ipe.getMessage() );
      }

      // There was another, unexpected error...
      catch( Exception e )
      {
         eprintln( "ERROR: [Generic/main] " + e.getMessage() );
      }

      // Make sure the 'end' event for the program always fires, regardless
      // of exception (assuming start event fired).
      finally
      {

         // Fire the 'end' event for the program.
         if( fireEndEvent )
            EventManager.fireEventMaybe( EventManager.EVENT_PROGRAM, EventManager.EVENT_END, null, null, together( args ), null, null );
      }
   }

   /**
    * Executes the Inspector application.  Both this method and the
    * main method execute the Inspector application, but this method
    * is a wrapper for the main method that facilitates the easy
    * integration of the Inspector into an existing application.
    * The main method is required to execute the Inspection as a
    * stand-alone application on the command line.  The main method
    * can also be invoked from another
    * application but it requires an array of strings for the
    * command line arguments, which is more complicated to produce than
    * a single string of arguments.  Here is how the Inspector
    * would be invoked using the main method (for example):
    * <BR><BR><CODE>&nbsp;&nbsp;&nbsp;&nbsp;vn.Inspector.main( new String[] { "../vn-xml", "-Vab", "-ir", "-Ocare" } );</CODE><BR><BR>
    * The same thing can be accomplished more easily using this method:
    * <BR><BR><CODE>&nbsp;&nbsp;&nbsp;&nbsp;vn.Inspector.run( "../vn-xml -Vab -ir -Ocare" );</CODE><BR><BR>
    * The command line arguments can contain any number of spaces or tabs
    * before, after, and between each one (just like the normal command line).
    * See the <I>Extension Guide</I> for more information.
    *
    * @param commandLine a single string of all the command line arguments,
    *        separated by spaces
    * @see vn.Inspector#main(String[])
    */
   public static void run( String commandLine )
   {

      // Show an error and exit if no string was supplied.
      if( commandLine == null )
      {
         eprintln( "ERROR: Command line parameter was null." );
         return;
      }

      // Extract the arguments from the string, ignoring all spaces and
      // tabs before, after, and between each one.
      String[] args = commandLine.trim().split( "[ \t]+" );

      // Invoke the main method with these arguments.
      main( args );
   }

   //////////////////////////
   // Informational Output //
   //////////////////////////

   /**
    * Prints the usage (a.k.a.&nbsp;help message) for the Inspector.
    *
    * @see vn.Inspector#main(String[])
    */
   private static void printUsage()
   {
      println( "Usage: java vn.Inspector [flags] <x> [-V <v>] [-O <o>]" );
      println( "" );
      println( "NOTE: Command-line elements can occur in any order.  Any element between" );
      println( "      [ ] is optional.  -V, -O are called \"operators\".  Space between" );
      println( "      operators and their arguments is optional.  Command-line elements" );
      println( "      are case-sensitive." );
      println( "" );
      println( "Flags:" );
      println( "  -?    Display usage message and exit" );
      println( "  -k    Display key and exit" );
      println( "  -c    Display class hierarchy and exit (-V operator irrelevant)" );
      println( "  -h    Suppress header before output" );
      println( "  -n    Suppress final counts after output" );
      println( "  -m    Include more counts by class (class counts inactive by default)" );
      println( "  -0    Include count categories with a zero count" );
      println( "  -w    Print the name of the current class being processed to stderr" );
      println( "  -s    Sort the members in each class or subclass" );
      println( "  -i    Indent output" );
      println( "  -z    Suppress <NO ...> for subclasses, members, thematic roles and frames" );
      println( "  -q    Force underlying scanning system to operate on verb-frame pairs" );
      println( "        NOTE: This scans the classes in the same manner as -Vq displays them," );
      println( "        but does not imply printing anything.  Exists so that you can make" );
      println( "        verb-frame pair events fire without printing anything.  If this option" );
      println( "        is specified, -Vm and -Vr imply -Vq if either is supplied. Also," );
      println( "        -Vq implies -q." );
      println( "  -v    Invert the order of -q or -Vq so as to visit verb-frame pairs in a" );
      println( "        frame-major order instead of a verb-major order (-q or -Vq required)" );
      println( "  -e    Suppress all events from firing" );
      println( "  -r    Replicate labels that cause additional nesting (file, class, subclass," );
      println( "        and frame) before each and every line that is printed.  This option is" );
      println( "        provided for increased interoperability with grep.  Grep's -B option" );
      println( "        can be used to show the class and/or frame associated when searching" );
      println( "        for a given pattern in the Inspector's output." );
      println( "" );
      println( "<x>: \"VerbNet XML Input Directory\"" );
      println( "        Directory where all the VerbNet XML files reside (i.e. care-88.xml)." );
      println( "        Note that the DTD file should also be located in this directory." );
      println( "" );
      println( "<v>: \"View Options\"" );
      println( "        Control what output is extacted from the XML files and sent to" );
      println( "        the console.  Example: '-Vcv' shows all verbs and the classes or" );
      println( "        subclasses that they belong to.   These are the available options:" );
      println( "            f - file names" );
      println( "            c - class and subclass names" );
      println( "            n - counts (members and frames, -Vc required)" );
      println( "            m - members (i.e. verbs)" );
      println( "            w - WordNet sense tags (-Vm required)" );
      println( "            t - thematic roles" );
      println( "            u - selectional restrictions for thematic roles (-Vt required)" );
      println( "            r - frames" );
      println( "            e - examples" );
      println( "            x - syntax" );
      println( "            y - syntax restrictions for syntax (-Vx required)" );
      println( "            z - selectional restrictions for syntax (-Vx required)" );
      println( "            s - semantics" );
      println( "            a - all above options" );
      println( "            q - verb-frame pairs (implies -Vm, -Vr and -q)" );
      println( "            b - complete XML file content (includes obscure attributes)" );
      println( "" );
      println( "<o>: \"Only These Files\"" );
      println( "        An optional token used to limit the Inspector to a set of VerbNet" );
      println( "        XML files.  This is a comma-delimited list of file names.  However," );
      println( "        you do not have to specify an entire file name.  You can specify any" );
      println( "        number of characters that you want for each file name.  If an XML file" );
      println( "        begins with the characters of any one of the file names you provided," );
      println( "        it will be processed.  No space is allowed in <o> token.  Examples:" );
      println( "            -Ochase-51.6.xml - the file chase-51.6.xml" );
      println( "            -O chase-51.6.xml - same as above" );
      println( "            -O chase-51.6 - same as above" );
      println( "            -O chase - same as above (quite useful)" );
      println( "            -O chase-51.6.xml,force-59.xml - both of these files" );
      println( "            -O chase-51.6,force-59 - same as above" );
      println( "            -O chase,force - same as above" );
      println( "            -O chase, force - INVALID - no space allowed" );
      println( "            -O ch,force-59 - all files that begin with a 'ch' and force-59.xml" );
      println( "            -O m,n - all files that begin with an 'm' or an 'n'" );
      println( "" );
      println( "NOTE: This usage is fairly long.  Use can use more: 'java vn.Inspector -? | more'." );
   }

   /**
    * Prints the thematic role and syntax key.
    *
    * @see vn.Inspector#main(String[])
    */
   private static void printKey()
   {
      println( "Key For Output (Thematic Role and Frame/Syntax sections)" );
      println( "========================================================" );
      println( "   %role     Thematic Role" );
      println( "   V         Verb" );
      println( "   [...]     Selectional Restrictions" );
      println( "   <...>     Syntax Restrictions" );
      println( "   (...)     Lexical Requirements" );
      println( "   {...}     Preposition(s)" );
      println( "   {{...}}   Preposition Class(es) (via Selectional Restrictions)" );
      println( "" );
      println( "Complete Representation (these only applicable with -Vb option" );
      println( "===============================================================" );
      println( "   (...)     Additional attributes for FRAME element" );
      println( "   {...}     Additional attribute for ARG element (type)" );
   }

   /**
    * Prints the header for this execution of the Inspector.  All command
    * line arguments are regurgitated and the date and time of this execution
    * is shown.
    *
    * @see vn.Inspector#main(String[])
    * @see vn.Inspector#wrapString(String)
    * @see vn.Inspector#filePath(File)
    */
   private static void printHeader()
   {
      println( "--- Inspector: Header ---------------------------------------->" );
      println( "| XML Input Directory:    " + filePath( vnDir ) );        // Must be supplied.
      println( "| Flags:                  " + wrapString( flags ) );
      println( "| View Options:           " + wrapString( viewOpts ) );
      println( "| Only These Files:       " + wrapString( onlyTheseFiles ) );
      println( "| Executed On:            " + new Date().toString() );
      println( "-------------------------------------------------------------->" );
   }

   /**
    * Massages a string that could be null for the header.
    * All the variables {@link vn.Inspector#flags},
    * {@link vn.Inspector#vnDir}, {@link vn.Inspector#viewOpts},
    * and {@link vn.Inspector#onlyTheseFiles} begin as <CODE>null</CODE>
    * and are only given values if they have a corresponding
    * value on the command line.
    *
    * @param s the string to massage
    * @return the string given if it is not null, or the message
    *         "<not supplied>" if it is
    * @see vn.Inspector#printHeader()
    */
   private static String wrapString( String s )
   {
      if( s == null )
         return "<not supplied>";

      else
         return s;
   }

   /**
    * Returns a descriptive path for a {@link java.io.File} object.  This is
    * only a distinct method due to the possibility of the more desired method,
    * {@link java.io.File#getCanonicalPath()} to throw an exception.  If an
    * exception is thrown, the basic {@link java.io.File#getPath()} is returned.
    *
    * @param f the file whose path to retrieve
    * @return a descriptive path
    * @see vn.Inspector#printHeader()
    */
   private static String filePath( File f )
   {
      try
      {
         return f.getCanonicalPath();
      }
      catch( Exception e )
      {
         return f.getPath();
      }
   }

   //////////////////
   // Tag Counters //
   //////////////////

   /**
    * Increments the counter for a given tag by 1.  This is used all over the sweeper
    * method to count those tags (i.e. CLASS or THEMROLE) which are printed.
    * Only those tags which are printed are counted.  The counters for FILE
    * and CLASS will always be identical if both -Vf and -Vc are supplied since
    * there is exactly one main class per XML file.  This method increments
    * both the class counts tag counter and the final counts tag counter
    * simultaneously.
    *
    * @param tagName the name of the tag whose counter to increment by 1
    * @see vn.Inspector#tagCounterClass
    * @see vn.Inspector#tagCounterGlobal
    * @see vn.Sweeper#startVNCLASS(Node)
    * @see vn.Sweeper#startVNSUBCLASS(Node)
    * @see vn.Sweeper#startTHEMROLE(Node)
    * @see vn.Sweeper#startFRAME(Node)
    * @see vn.Sweeper#startEXAMPLE(Node)
    * @see vn.Sweeper#startSYNTAX(Node)
    * @see vn.Sweeper#startPRED(Node)
    * @see vn.Sweeper#printMembers()
    * @see vn.Sweeper#classHierarchyPrint(Element, int)
    */
   static void incrementTagCounter( String tagName )
   {
      incrementTagCounter( tagName, 1 );
   }

   /**
    * Increments the counter for a given tag by a given integer.  This method
    * is used directly by {@link vn.Sweeper#classHierarchyPrint(Element, int)}
    * to increment member and frame counters more quickly and indirectly by
    * all those methods which directly call {@link vn.Inspector#incrementTagCounter(String)}.
    * This method increments both the class counts tag counter and the final counts tag counter
    * simultaneously.
    *
    * @param tagName the name of the tag whose counter to increment by <CODE>howMany</CODE>
    * @param howMany the number of times to increment the tag counter for <CODE>tagName</CODE>
    * @see vn.Inspector#tagCounterGlobal
    * @see vn.Sweeper#classHierarchyPrint(Element, int)
    * @see vn.Inspector#incrementTagCounter(String)
    */
   static void incrementTagCounter( String tagName, int howMany )
   {

      // Increment the class counts tag counter if this class counts are desired.
      if( flClassCounts )

         // If the hash map does not yet contain an entry for the tag name,
         // initialize the entry to its first value.
         if( !tagCounterClass.containsKey( tagName ) )
            tagCounterClass.put( tagName, new Integer( howMany ) );

         // Else increment what's already there.
         else
            tagCounterClass.put( tagName, new Integer( ( ( Integer ) tagCounterClass.get( tagName ) ).intValue() + howMany ) );

      // If the global hash map does not yet contain an entry for the tag name,
      // initialize the entry to its first value.
      if( !tagCounterGlobal.containsKey( tagName ) )
         tagCounterGlobal.put( tagName, new Integer( howMany ) );

      // Else increment what's already there.
      else
         tagCounterGlobal.put( tagName, new Integer( ( ( Integer ) tagCounterGlobal.get( tagName ) ).intValue() + howMany ) );
   }

   /**
    * Empties the class counts tag counter.  Called at the start of each
    * new class or subclass.
    *
    * @see vn.Sweeper#startVNCLASS(Node)
    * @see vn.Sweeper#startVNSUBCLASS(Node)
    */
   static void clearClassTagCounter()
   {
      tagCounterClass.clear();
   }

   /**
    * Prints all the counts from either the class counts tag counter or the
    * final counts tag counter.  The class counts, if the appropriate flag
    * is supplied, are printed before each new class or subclass begins
    * at the closing of the FRAMES element, since that will always be the last
    * element in a VNCLASS or VNSUBCLASS element.  The final counts are printed
    * at the end of the entire program
    *
    * @param useClassCounter whether or not to print the class counts.  If set
    *        to <CODE>true</CODE> the class counts are printed, otherwise the
    *        final counts are printed.
    * @see vn.Inspector#main(String[])
    * @see vn.Sweeper#endFRAMES(Node)
    * @see vn.Inspector#printTagCount(HashMap, String)
    */
   static void printTagCounts( boolean useClassCounter )
   {
      HashMap tagCounter = ( useClassCounter ) ? tagCounterClass : tagCounterGlobal;
      int c;

      // Print title of counts section.
      if( useClassCounter )
         println( "--- Class Counts ---------" );

      else
         println( "--- Final Counts ---------" );

      // Print none if no tags were encountered and the user doesn't
      // want to see the zeros explicitly.
      if( tagCounter.size() == 0 && !flZeroCounts )
         println( "| <NONE>                 |" );

      // Else if there is at least one tag to print or the user wants
      // to see the zeros, print all the counters.
      else
      {
         printTagCount( tagCounter, "FILE" );
         printTagCount( tagCounter, "CLASS" );
         printTagCount( tagCounter, "SUBCLASS" );
         printTagCount( tagCounter, "MEMBER" );
         printTagCount( tagCounter, "THEMROLE" );
         printTagCount( tagCounter, "FRAME" );
         printTagCount( tagCounter, "EXAMPLE" );
         printTagCount( tagCounter, "SYNTAX" );
         printTagCount( tagCounter, "SEMANTIC PRED" );
         printTagCount( tagCounter, "VF-PAIR" );
      }

      println( "--------------------------" );
   }

   /**
    * Prints a tag name along with the number of times it was encountered.
    * If the count is zero, the line will only be printed if the
    * {@link vn.Inspector#flZeroCounts} flag is set.
    *
    * @param tagName the tag name whose count to print
    * @see vn.Inspector#printTagCounts(boolean)
    * @see vn.Inspector#getTagCount(HashMap, String)
    */
   private static void printTagCount( HashMap tagCounter, String tagName )
   {
      int c = getTagCount( tagCounter, tagName );

      // Print the tag name along with the count if it's not zero
      // or the user wants to see all counts including zeros.
      if( c != 0 || flZeroCounts )
      {

         // The following lines of code implement this Java 1.5 printf statement:
         //    System.out.printf( "| %-16s", tagName + ": " );
         String t = tagName + ": ";
         String sp = "";
         int spc = 16 - t.length();
         for( int s = 0; s < spc; s++ )
            sp += " ";
         print( "| " + t + sp );

         // The following lines of code implement this Java 1.5 printf statement:
         //    System.out.printf( "%6d |", c );
         sp = "";
         if( c < 100000 ) sp = " ";
         if( c < 10000 ) sp = "  ";
         if( c < 1000 ) sp = "   ";
         if( c < 100 ) sp = "    ";
         if( c < 10 ) sp = "     ";
         print( sp + c + " |" );

         println( "" );
      }
   }

   /**
    * Returns the number of times a given tag name was encountered for the
    * given counter.
    *
    * @param tagName the tag name whose count to return
    * @return the count for the given tag name (the number of times the tag name
    *         was encountered)
    * @see vn.Inspector#printTagCounts(boolean)
    * @see vn.Inspector#printTagCount(HashMap, String)
    */
   private static int getTagCount( HashMap tagCounter, String tagName )
   {

      // If the tag name does not yet have an entry in the given hash map,
      // then it has not been encountered even once.
      if( !tagCounter.containsKey( tagName ) )
         return 0;

      else
         return ( ( Integer ) tagCounter.get( tagName ) ).intValue();
   }

   ////////////////////////////
   // Command-Line Arguments //
   ////////////////////////////

   /**
    * Validates all of the command-line arguments and sets appropriate class-level variables.
    *
    * @param args the command-line arguments from {@link vn.Inspector#main(String[])}
    * @throws InvalidCommandLineArgumentException if the command-line contains invalid flags
    *         or does not contain the requisite XML input directory.
    * @throws InvalidPathException if the XML input directory does not exist or does not have
    *         the appropriate permissions.
    * @throws UserWantsHelpMessage if the user has supplied the help flag.
    * @throws UserWantsKey if the user has supplied the key flag.
    * @see vn.Inspector#main(String[])
    * @see vn.Inspector.MyFilter
    */
   private static void analyzeArguments( String args[] )
      throws InvalidCommandLineArgumentException,
             InvalidPathException,
             UserWantsHelpMessage,
             UserWantsKey
   {
      // The following loop parses the command-line paramters.
      // It sets all appropriate vo* variables based on -V operators.
      // It sets all appropriate fl* variables based on flags.
      // It sets the "only these files" string.
      // It sets the XML input directory.

      // Cycle through all tokens on the command line, indentify
      // its meaning and take the appropriate action.
      for( int a = 0; a < args.length; a++ )
      {

         // If it's a flag or an operator...
         if( args[ a ].startsWith( "-" ) )
         {

            // If the argument which is a flag or an operator only has the
            // one character (the hyphen), then throw an exception.
            if( args[ a ].length() == 1 )
               throw new InvalidCommandLineArgumentException( "Invalid option (-)." );

            // Grab the character following the hyphen.
            char key = args[ a ].charAt( 1 );

            // If the character is an operator (V or O)...
            if( ALL_OPER_CHARS.indexOf( key ) != -1 )
            {
               String buddy;

               // Decide if the operator's argument was supplied directly
               // attached to the operator (-Vab vs. -V ab).
               boolean attached = ( args[ a ].length() != 2 );

               // If the argument is attached, strip off the hyphen and operator
               // for the argument.
               if( attached )
                  buddy = args[ a ].substring( 2 );

               // If the argument is not attached, assumed the next command-line
               // argument is the operator's argument.
               else
               {

                  // Make sure there is another argument to look at.
                  if( a == args.length - 1 )
                     throw new InvalidCommandLineArgumentException( "The -" + key + " operator does not have an argument." );

                  // Grab the operator's argument.
                  buddy = args[ ++a ];

                  // Make sure that argument isn't another flag or hyphen (which
                  // would imply the operator's argument is missing).
                  if( buddy.charAt( 0 ) == '-' )
                     throw new InvalidCommandLineArgumentException( "The -" + key + " operator does not have an argument." );
               }

               // Process the argument's operator.
               switch( key )
               {
                  case 'V':      // View Options operator

                     // Since each letter in the view option operator's argument
                     // means something different, scan the argument and
                     // set the correct flag
                     for( int b = 0; b < buddy.length(); b++ )
                     {
                        char vo = buddy.charAt( b );

                        // If the current view option character isn't a valid one,
                        // throw an exception.
                        if( ALL_VIEW_OPTS.indexOf( vo ) == -1 )
                           throw new InvalidCommandLineArgumentException( "Invalid view option character (" + vo + ")." );

                        // Append this view option to a string of all supplied
                        // view options.
                        if( viewOpts == null ) viewOpts = "";
                        viewOpts += vo;

                        // Set the appropriate boolean view option flag variable.
                        switch( vo )
                        {
                           case 'f': voFileName   = true; break;
                           case 'c': voClassName  = true; break;
                           case 'n': voCount      = true; break;
                           case 'm': voMember     = true; break;
                           case 'w': voWordNet    = true; break;
                           case 't': voThemRole   = true; break;
                           case 'u': voTRSelRestr = true; break;
                           case 'r': voFrame      = true; break;
                           case 'e': voExample    = true; break;
                           case 'x': voSyntax     = true; break;
                           case 'y': voXSynRestr  = true; break;
                           case 'z': voXSelRestr  = true; break;
                           case 's': voSemantics  = true; break;
                           case 'a': voAll        = true; break;
                           case 'q': voVFPairs    = true; break;
                           case 'b': voComplete   = true; break;
                        }
                     }

                     break;

                  case 'O':      // Only These XML Files operator

                     // Initialize the string if this is the first -O operator
                     // found or add a comma otherwise.
                     if( onlyTheseFiles == null )
                        onlyTheseFiles = "";
                     else
                        onlyTheseFiles += ",";

                     // Add the operator.
                     onlyTheseFiles += buddy.toLowerCase();

                     break;

               }     // switch

            }     // if( ALL_OPER_CHARS.indexOf( key ) != -1 )

            // If the character is an not an operator, assume it's a flag...
            else

               // Cycle through all the letters in the flag since
               // you can group flags (i.e. -ciz).
               for( int c = 1; c < args[ a ].length(); c++ )
               {
                  char flag = args[ a ].charAt( c );

                  // Append this flag to a string of all supplied flags.
                  if( flags == null ) flags = "";
                  flags += flag;

                  // Set the appropriate boolean flag variable.
                  switch( flag )
                  {
                     case '?': flHelp           = true; break;
                     case 'k': flKey            = true; break;
                     case 'c': flClassH         = true; break;
                     case 'h': flNoHeader       = true; break;
                     case 'n': flNoFinalCounts  = true; break;
                     case 'm': flClassCounts    = true; break;
                     case '0': flZeroCounts     = true; break;
                     case 'w': flErrProgress    = true; break;
                     case 's': flSortMembers    = true; break;
                     case 'i': flIndent         = true; break;
                     case 'z': flNoAbsence      = true; break;
                     case 'q': flVFPairs        = true; break;
                     case 'v': flVFPairsInvert  = true; break;
                     case 'e': flSuppressEvents = true; break;
                     case 'r': flReplicate      = true; break;

                     // Catch invalid flags.
                     default:
                        throw new InvalidCommandLineArgumentException( "Invalid flag (" + flag + ")." );

                  }     // switch

               }     // for

         }     // if( args[ a ].startsWith( "-" ) )

         // Else if this argument does not have a hyphen, then
         // assume this is the XML input directory.
         else
         {

            // If the XML input directory was already supplied throw
            // an exception.
            if( vnDir != null )
               throw new InvalidCommandLineArgumentException( "XML directory already provided (What is '" + args[ a ] + "'?)" );

            // Construct a File object from the command-line argument.
            vnDir = new File( args[ a ] );
         }

      }     // for( int a = 0; a < args.length; a++ )

      // Throw an informational exception to return to main and print the usage
      // message if the appropriate flag was supplied.
      if( flHelp )
         throw new UserWantsHelpMessage();

      // Throw an informational exception to return to main and print the key
      // if the appropriate flag was supplied.
      if( flKey )
         throw new UserWantsKey();

      // If there was no XML input directory supplied, throw an exception.
      if( vnDir == null )
         throw new InvalidCommandLineArgumentException( "No XML directory specified." );

      // Make sure the XML input directory is valid.
      if( !vnDir.exists() )        throw new InvalidPathException( "XML input directory path does not exist."     );
      if( !vnDir.isDirectory() )   throw new InvalidPathException( "XML input directory path is not a directory." );
      if( !vnDir.canRead() )       throw new InvalidPathException( "XML input directory not readable."            );

      // Enforce -Va implies all view options besides -Vb and -Vq.
      if( voAll )
      {
         voFileName   = true;
         voClassName  = true;
         voCount      = true;
         voMember     = true;
         voWordNet    = true;
         voThemRole   = true;
         voTRSelRestr = true;
         voFrame      = true;
         voExample    = true;
         voSyntax     = true;
         voXSynRestr  = true;
         voXSelRestr  = true;
         voSemantics  = true;
      }

      // Enforce -c ignores -V operator.
      if( flClassH )
      {
         voFileName   = false;
         voClassName  = false;
         voCount      = false;
         voMember     = false;
         voWordNet    = false;
         voThemRole   = false;
         voTRSelRestr = false;
         voFrame      = false;
         voExample    = false;
         voSyntax     = false;
         voXSynRestr  = false;
         voXSelRestr  = false;
         voSemantics  = false;
         voAll        = false;
         voVFPairs    = false;
         voComplete   = false;
      }

      // Enforce -Vq implies -Vm, -Vr and -q.
      if( voVFPairs )
      {
         flVFPairs = true;
         voMember  = true;
         voFrame   = true;
      }

      // Enforce -q with -Vm or -Vr implies -Vq.
      if( flVFPairs && ( voMember || voFrame ) )
      {
         voVFPairs = true;
         voMember  = true;
         voFrame   = true;
      }

      // Show warning if the user wants options that aren't allowed with
      // the class hierarchy.
      if( flClassH && ( flClassCounts || flVFPairs || flVFPairsInvert ) )
      {
         eprintln( "WARNING: -m, -q, and -v options ineffective when -c supplied." );
         flClassCounts = false;
         flVFPairs = false;
         flVFPairsInvert = false;
      }

      // Show warning if the user wants to invert verb-frame pairs without
      // requesting verb-frame pair mode.
      if( flVFPairsInvert && !flVFPairs )
      {
         eprintln( "WARNING: -v option ineffective without -q or -Vq." );
         flVFPairsInvert = false;
      }

      // Show warning if the user wants member/frame counts printed without
      // printing class labels.
      if( voCount && !voClassName )
      {
         eprintln( "WARNING: -Vn option ineffective without -Vc." );
         voCount = false;
      }

      // Show warning if the user wants WordNet senses printed without
      // printing members.
      if( voWordNet && !voMember )
      {
         eprintln( "WARNING: -Vw option ineffective without -Vm." );
         voWordNet = false;
      }

      // Show warning if the user wants thematic role selectional restrictions
      // printed without printing the thematic roles.
      if( voTRSelRestr && !voThemRole )
      {
         eprintln( "WARNING: -Vu option ineffective without -Vt." );
         voTRSelRestr = false;
      }

      // Show warning if the user wants syntax restrictions printed without
      // printing the syntax.
      if( voXSynRestr && !voSyntax )
      {
         eprintln( "WARNING: -Vy option ineffective without -Vx." );
         voXSynRestr = false;
      }

      // Show warning if the user wants syntax selectional restrictions
      // printed without printing the syntax.
      if( voXSelRestr && !voSyntax )
      {
         eprintln( "WARNING: -Vz option ineffective without -Vx." );
         voXSelRestr = false;
      }

      // Grab all the XML files from the supposed XML input directory.
      xmlFiles = vnDir.listFiles( new MyFilter( "xml" ) );

      // If there are no XML files in the XML input directory, throw an exception.
      if( xmlFiles.length == 0 )
         throw new InvalidPathException( "There are no XML files in the XML input directory." );

      // If there was at least one "only-these-files" string specified,
      // break it apart and validate it.
      if( onlyTheseFiles != null )
      {

         // Break the string apart on the comma.
         allOnlyFiles = onlyTheseFiles.split( "," );

         // Make sure all elements are non-zero length strings
         // (i.e. -Ocare,,chase).
         for( int a = 0; a < allOnlyFiles.length; a++ )
            if( allOnlyFiles[ a ].equals( "" ) )
               throw new InvalidCommandLineArgumentException( "Invalid \"only-this-file\" token.  Cannot be empty." );
      }
   }

   ////////////
   // Driver //
   ////////////

   /**
    * Performs the scanning of the XML files in the XML input directory.
    * It locates the document root element (VNCLASS) in each file and requests
    * that the node be processed.  Processing of this node will recursively
    * process all nodes below it (the entire file).  If an -O operator
    * was supplied, then only those files which match that operator's argument
    * will be processed.  No events will fire for those files not processed.
    *
    * @see vn.Inspector#main(String[])
    * @see vn.Inspector#processNode(Node)
    * @see vn.Inspector#processNodeByPairs(Node, ArrayList)
    */
   private static void performInspection()
   {
      String xmlFileName = "";

      try
      {
         DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();

         // The Inspector software does not validate the VerbNet XML files.
         // It assumes that the researcher or future developer of this software
         // has downloaded the most recent version of the XML files and that
         // they have error-checked by running the UVIG against them.  The UVIG
         // not only produces the UVI but also scans the XML for errors.
         // The files available for download should be as error-free as possible
         // already.
         dbf.setValidating( false );

         // Create an XML parser.
         DocumentBuilder db = dbf.newDocumentBuilder();

         // Visit each XML file in the XML input directory and process it if
         // it's not excluded by the -O operator.
         for( int x = 0; x < xmlFiles.length; x++ )
         {
            xmlFileName = xmlFiles[ x ].getName();

            // If the -O operator was supplied, then only continue if
            // this file matches one of the "only-these-files" tokens.
            if( onlyTheseFiles != null )
            {
               boolean foundOne = false;

               // Search for a token that is the beginning of this file name.
               for( int a = 0; a < allOnlyFiles.length; a++ )
                  if( xmlFileName.toLowerCase().startsWith( allOnlyFiles[ a ].toLowerCase() ) )
                  {
                     foundOne = true;
                     break;
                  }

               // If no match was found, perform no further processing of this
               // file and continue to the next one.
               if( !foundOne )
                  continue;
            }

            // Print this file name to stderr if the appropriate flag was supplied.
            if( flErrProgress )
               eprintln( "Processing " + xmlFileName + "..." );

            // Parse the XML file into a Document object.
            Document doc = db.parse( xmlFiles[ x ] );

            // Grab the document element.
            Element mainClass = doc.getDocumentElement();

            // If the XML file is not a VerbNet XML file, print
            // an error message for this file.
            if( !mainClass.getNodeName().equals( "VNCLASS" ) )
               eprintln( "ERROR: VNCLASS element is not the document element in file \"" + xmlFileName + "\"." );

            // Else process the file...
            else
            {
               // Let the Sweeper class know which file is currently
               // being processed.
               Sweeper.setCurFile( xmlFileName );

               // If Inspector is to be run in verb-frame mode, execute
               // a process method that will keep track of the frames at
               // all levels of recursion.
               if( flVFPairs )
               {
                  ArrayList blankNodeList = new ArrayList();
                  processNodeByPairs( mainClass, blankNodeList );
               }

               // Else just process the file normally.
               else
                  processNode( mainClass );

               // Attempt to clean up now-unused memory from last file.
               System.gc();
            }
         }
      }

      // There was an error instantiating the DocumentBuilder object...
      catch( ParserConfigurationException e )
      {
         eprintln( "ERROR: Parser configuration error." );
      }

      // A file referenced by the XML files was not found...
      // (this will most likely occur if the DTD is not in the XML
      // input directory)
      catch( FileNotFoundException fnfe )
      {
         eprintln( "ERROR: " + fnfe.getMessage() + "." );
         eprintln( "   Most likely the file \"" + xmlFileName + "\" references the missing file above." );
      }

      // There was another, unexpected error...
      catch( Exception e )
      {
         eprintln( "ERROR: [" + xmlFileName + "] " + e.getMessage() + "." );
      }
   }

   ///////////////////////////////
   // Primary Recursive Methods //
   ///////////////////////////////

   /**
    * Starts by outputting the simple text you would want to output
    * upon encountering the start of the given node, then recursively prints all the
    * simple text associated with this node's children nodes, and finally outputs the
    * simple text needed for the close of the given node.  The process by which this
    * method outputs the 'start' or 'end' simple text for a given node is subtle.
    * Reflection is used.  For a node with tag name NODE, methods called
    * 'startNODE' and 'endNODE' are located in the class called 'Sweeper'.
    * If the method is found, it is executed.  If it is not found, nothing happens.
    *
    * @param n the XML node for which to generate simple-text representation
    * @see vn.Inspector#performInspection()
    * @see vn.Inspector#executeHTMLMethod(String, Node)
    */
   private static void processNode( Node n )
   {
      executeHTMLMethod( "start", n );

      // If the class hierarchy is to be printed, process no further
      // since it will have already been printed upon the above
      // call to executeHTMLMethod.
      if( flClassH )
         return;

      NodeList kids = n.getChildNodes();

      for( int k = 0; k < kids.getLength(); k++ )
         processNode( kids.item( k ) );             // Recursively call each child.

      executeHTMLMethod( "end", n );
   }

   /**
    * Starts by outputting the simple text you would want to output
    * upon encountering the start of the given node, then recursively prints all the
    * simple text associated with this node's children nodes, and finally outputs the
    * simple text needed for the close of the given node.  The process by which this
    * method outputs the 'start' or 'end' HTML for a given node is subtle.
    * Reflection is used.  For a node with tag name simple text, methods called
    * 'startNODE' and 'endNODE' are located in the class called 'Sweeper'.
    * If the method is found, it is executed.  If it is not found, nothing happens.
    * <BR><BR>
    * The only difference between this method and {@link vn.Inspector#processNode(Node)}
    * is that this method accumulates frames as it traverses down the class tree.
    * This ensures that a subclass at depth 2 has all the frames of the main class
    * (depth 0), the subclass at depth 1, and itself, the subclass at depth 2.
    * See more information at {@link vn.Sweeper#curVFFrameList}.
    *
    * @param n the XML node for which to generate simple-text representation
    * @param prevFrames all the frames accumulated since the main class of the file
    * @see vn.Inspector#performInspection()
    * @see vn.Inspector#executeHTMLMethod(String, Node)
    * @see vn.Sweeper#curVFFrameList
    */
   static void processNodeByPairs( Node n, ArrayList prevFrames )
   {
      ArrayList newFrames = prevFrames;      // New list is old list by default.
      String nodeName = n.getNodeName();

      executeHTMLMethod( "start", n );

      // If this is a class or subclass node, add the frames to the
      // growing list along this path.
      if( nodeName.equals( "VNCLASS" ) || nodeName.equals( "VNSUBCLASS" ) )
      {

         // Make a copy of the existing frames list.
         newFrames = new ArrayList( prevFrames );

         // Get a list of all the FRAME elements.
         NodeList framesElems = ( ( Element ) n ).getElementsByTagName( "FRAMES" );
         Element framesElem = ( Element ) framesElems.item( 0 );
         NodeList frameElems = framesElem.getElementsByTagName( "FRAME" );

         // Add the new frames to the copy of the list given to the method.
         for( int b = 0; b < frameElems.getLength(); b++ )
            newFrames.add( frameElems.item( b ) );

         // Pass the new list off to the Sweeper class so it has the list
         // when it's time to call the method printVerbFramePairs().
         Sweeper.setFrameList( newFrames );
      }

      NodeList kids = n.getChildNodes();

      for( int k = 0; k < kids.getLength(); k++ )
      {

         // Don't process FRAME nodes here - they will be processed separately
         // by vn.Sweeper#printVerbFramePairs().
         if( kids.item( k ).getNodeName().equalsIgnoreCase( "FRAME" ) )
            continue;

         processNodeByPairs( kids.item( k ), newFrames );             // Recursively call each child.
      }

      executeHTMLMethod( "end", n );
   }

   /**
    * Executes a method in the {@link vn.Sweeper} class based on an XML element tag name
    * (i.e.&nbsp;'VNCLASS') and a 'start' or 'end' flag.  Each of the methods in Sweeper,
    * startVNCLASS, endVNCLASS, startMEMBERS, endMEMBERS, etc., produce simple text.
    * This method just calls the right method based on the current node being
    * processed by {@link vn.Inspector#processNode(Node)} or
    * {@link vn.Inspector#processNodeByPairs(Node, ArrayList)}.
    *
    * @param which either the value 'start' or 'end', the string to prepend to the
    *        tag name when locating the method in {@link vn.Sweeper}
    * @param n the node whose tag name should be located in the Sweeper methods
    * @see vn.Inspector#processNode(Node)
    * @see vn.Inspector#processNodeByPairs(Node, ArrayList)
    */
   private static void executeHTMLMethod( String which, Node n )
   {

      // Verify flag is a valid token.
      if( !which.equals( "start" ) && !which.equals( "end" ) )
      {
         eprintln( "ERROR: Invalid \"which\" parameter.  Possible values are \"start\" and \"end\"." );
         return;
      }

      // Use the appropriate reflection methods to execute the desired method.
      try
      {
         Class sweeper = Class.forName( "vn.Sweeper" );
         Class node    = Class.forName( "org.w3c.dom.Node" );

         Class[] classes = { node };

         Method m = sweeper.getDeclaredMethod( which + n.getNodeName(), classes );

         Object[] args = { n };

         m.invoke( null, args );
      }
      catch( NoSuchMethodException nsme )
      {
         // Do nothing - this is not an error condition.  It merely means the developer has not
         // specified any action for this node at this point (i.e. 'start' or 'end').
         // Methoods with names 'start#text' also fall into this category.
      }
      catch( ClassNotFoundException cnfe )
      {
         eprintln( "ERROR: Either \"vn.Sweeper\" or \"org.w3c.dom.Node\" could not be found.  Skipping \"" +
                     which + "\" for \"" + n.getNodeName() + "\"." );
      }
      catch( SecurityException se )
      {
         eprintln( "ERROR: [Security/refl] " + se.getMessage() + "." );
      }
      catch( Exception e )
      {
         eprintln( "ERROR: [Generic/refl] " + e.getMessage() + "." );
      }
      catch( Error err )
      {
         eprintln( "ERROR: [Generic/refl-err] " + err.getMessage() + "." );
      }
   }

   //////////////////////////
   // Supplemental Classes //
   //////////////////////////

   /**
    * Exception class for identifying when the user did not supply a
    * command-line of the proper format.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    */
   private static class InvalidCommandLineArgumentException extends IllegalArgumentException
   {

      /**
       * Constructs the exception object with the given message.
       *
       * @param message the text of the exception
       */
      public InvalidCommandLineArgumentException( String message )
      {
         super( message );
      }
   }

   /**
    * Exception class for identifying when the user did not supply
    * a valid XML input directory.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    */
   private static class InvalidPathException extends IOException
   {

      /**
       * Constructs the exception object with the given message.
       *
       * @param message the text of the exception
       */
      public InvalidPathException( String message )
      {
         super( message );
      }
   }

   /**
    * Exception class for identifying when the user requests to
    * view the help/usage message for the program.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    */
   private static class UserWantsHelpMessage extends Exception
   {

      /**
       * Constructs the exception object.
       */
      public UserWantsHelpMessage()
      {
         super();
      }
   }

   /**
    * Exception class for identifying when the user requests to
    * view the key.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    */
   private static class UserWantsKey extends Exception
   {

      /**
       * Constructs the exception object.
       */
      public UserWantsKey()
      {
         super();
      }
   }

   /**
    * Decides which files to select for the {@link java.io.File#listFiles}
    * method of the {@link java.io.File} class.
    *
    * @see vn.Inspector#analyzeArguments(String[])
    */
   private static class MyFilter implements FileFilter
   {
      /**
       * The extension of the files to select.
       */
      private String ext;

      /**
       * Constructs this filter with the given extension on which to filter.
       *
       * @param newExt the extension of the files to select (i.e. "xml")
       */
      public MyFilter( String newExt )
      {
         ext = newExt;
      }

      /**
       * Returns whether or not to accept the given file based on this filter.
       *
       * @param pathName the path which should be accepted or rejected
       *        based on whether it contains the extension for this
       *        {@link vn.Inspector.MyFilter} object
       * @return <CODE>true</CODE> if the given file should be selected
       */
      public boolean accept( File pathName )
      {
         return pathName.getName().endsWith( "." + ext );
      }
   }
}
