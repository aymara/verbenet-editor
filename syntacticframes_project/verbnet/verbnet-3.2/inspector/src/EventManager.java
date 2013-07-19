
////////////////////////////
// The Inspector          //
// A VerbNet Viewer       //
// University of Colorado //
// Fall 2006              //
////////////////////////////

package vn;

import org.w3c.dom.*;
import java.io.*;

/**
 * This class contains the method that researchers will modify to extend the Inspector
 * to other natural language processing tasks.  This method is:<BR><BR>
 * &nbsp;&nbsp;&nbsp;&nbsp;{@link vn.EventManager#fireEvent(int, int, String, String, String, Element, Element)}<BR><BR>
 * All events that are fired during the scanning of the VerbNet XML files end here.
 * The arguments passed to this method provide the context for the location where
 * the event fired.  The information given to this method is:
 * <UL>
 *    <LI>Current file</LI>
 *    <LI>Current class or subclass</LI>
 *    <LI>Simple-text representation of XML element that the event is firing for</LI>
 *    <LI>Relevant {@link org.w3c.dom.Element} objects from the Java XML DOM that represent the XML element from the file</LI>
 * </UL>
 * Thus, the events provide two ways to view the content of the VerbNet XML files:
 * parsing the simple-text representations or examining the {@link org.w3c.dom.Element}
 * objects.
 *
 * <BR><BR>
 * The simple-text representation is text that would have printed in the Inspector's
 * normal output mode with full view options enabled (-Vab).  In other words,
 * all attributes included in each XML element is embedded in the simple-text
 * representation for that element.  The specific representation will vary, but
 * every effort will be made to make sure the representation is consistent
 * from version to version of the Inspector.  This is so researcher's parsing
 * routines will not break just because they download a new version of the
 * Inspector code.  Utilize the key option (-k) to enumerate all representations
 * used by the Inspector.
 * <BR><BR>
 * The {@link org.w3c.dom.Element} object can be accessed and traversed with these methods:
 * <UL>
 *    <LI>{@link org.w3c.dom.Element#getAttribute(String)}</LI>
 *    <LI>{@link org.w3c.dom.Element#getElementsByTagName(String)}</LI>
 *    <LI>{@link org.w3c.dom.Node#getChildNodes()}</LI>
 * </UL>
 * Events exist for the majority of elements within the XML files.
 * Events do not fire for XML elements such as <CODE>&lt;VERB/></CODE> or <CODE>&lt;ADV/></CODE>
 * as those are absorbed into the events that fire for <CODE>&lt;SYNTAX></CODE>.
 * Events do not fire for the <CODE>&lt;SEMANTICS></CODE> element as whole but rather
 * for each individual <CODE>&lt;PRED></CODE> element inside.  Finally, events fire for
 * two addition "elements" - which are not elements in the XML sense.  These are PROGRAM and FILE.
 * This allows for futher control over firing code when needed.
 * <BR><BR>
 * The event system is unaffected by the -V operator.  The -V operator just describes
 * which elements should be printed to stdout.  All events for all elements still fire.
 * In fact, the only way to prevent the events from firing for a given execution of the Inspector
 * is by using the -e option.
 * <BR><BR>
 * The event system is however affected by the -O operator.  The -O limits the XML files
 * that the Inspector scans to a subset of all the files.  If supplied, events will only
 * fire for the files scanned.  For example, if "-Och,spray" is supplied, only the
 * files spray-9.7.xml and those which begin with "ch" are scanned.  Events will only
 * fire for these files.
 * <BR><BR>
 * Finally, a few elements span just a single line in the normal output.  These "one-liners"
 * are MEMBER, THEMROLE, EXAMPLE, SYNTAX, and SEMANTIC PRED.  Both the 'start' and 'end'
 * events for these elements still fire, but they fire one right after another.
 * In other words, the 'end' event is superfluous and fires just for completeness.
 * <BR><BR>
 * For more information about extending the Inspector, refer to the
 * <A href='http://verbs.colorado.edu/verb-index/inspector/extguide.html' target='_blank'>Extension Guide</A>.
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
 * @version 1.0, 2006.10.15
 */
public class EventManager
{

   /////////////////////////////////////////////////////////////////////////////
   // Researcher Fields - Can add needed class-level fields that will support //
   // fireEvent code right here.  This is important because if you want to    //
   // write your code in this class instead of an external class via method   //
   // calls, then you will need a mechanism to save information between calls //
   // of fireEvent.  The simple solution is to use static variables and       //
   // classes.  So for example, if you are extracting all verbs which         //
   // participate in frames that have an adverb one method is to run          //
   //   java vn.Inspector xml/ -q                                             //
   // and set the below example variable, verb, to the verb in the vf-pair    //
   // label when fireEvent calls on 'start' VF-PAIR and then when the 'start' //
   // SYNTAX event fires, the variable verb is waiting to be used however if  //
   // the syntax matches the rule.  One can utilize a static initializer      //
   // block to execute code even before the 'start' event for PROGRAM.        //
   /////////////////////////////////////////////////////////////////////////////

   //private static String verb;   // Example

   // Static initializer block can be used for any required initialization code.
   //static
   //{
   //   verb = "";
   //}

   ///////////////////////////////////////////////
   // Researcher Method - Extend Inspector Here //
   ///////////////////////////////////////////////

   // NOTE: If you are inserting code into the below method, feel free to delete
   // the Javadoc documentation from this method and this class so it is not
   // an encumbrance.

   /**
    * Executes custom code specific to each type of element as they are encountered in
    * the VerbNet XML files.  This method is made specifically for researchers hoping
    * to either extend the Inspector into a custom VerbNet application or embed
    * VerbNet in an existing application.  A researcher would download all the Inspector
    * files, add custom methods either in this class or an external class, and modify
    * this method to call those methods at the appropriate times during XML processing.
    * <BR><BR>
    * There are 11 "elements" for which events fire.  The word <I>element</I> in this case is
    * not exactly synonymous with <I>XML elements</I>, since PROGRAM and FILE are also
    * considered elements with respect to Inspector events.  The elements are:
    * PROGRAM, FILE, CLASS, SUBCLASS, MEMBER, THEMROLE, FRAME, EXAMPLE, SYNTAX, SEMANTIC PRED,
    * and VF-PAIR.  There are two events that fire for each element: 'start' and 'end'.  The
    * 'start' event fires when the element is entered and the 'end' event
    * fires when the element is exited.
    * <BR><BR>
    * When the class hierarchy is requested (with -c option), the only elements for which
    * events fire are PROGRAM, CLASS, and SUBCLASS).
    * <BR><BR>The 'start' event for PROGRAM fires if there were no problems with the command
    * line arguments and if neither -? nor -k was specified.  This event fires
    * before the header is printed (if not suppressed).  The 'end' event for PROGRAM fires if and only if the
    * 'start' event fired.  This event fires after the final counts have been printed (if not suppressed).
    * <BR><BR>
    * Six of the elements have 'start' events that fire before all the children
    * elements contained within them and 'end' events that fire after all of their
    * children's events have completed.  They are: PROGRAM, FILE, CLASS, SUBCLASS, FRAME, and VF-PAIR.
    * <BR><BR>
    * Five of the elements are considered "one-liners".  They span exactly one line in the
    * normal output.  Their 'end' events fire immediately after their 'start' events.  These 'end' events
    * only fire for completeness.  They are: MEMBER, THEMROLE, EXAMPLE, SYNTAX, and SEMANTIC PRED.
    * <BR><BR>
    * Both the simple-text representation and the XML {@link org.w3c.dom.Element} object is supplied
    * so as to give the researcher flexibility in how they access the VerbNet data.
    * The <CODE>text</CODE> argument (a string) can be parsed or the {@link org.w3c.dom.Element} object can
    * be traversed.  If using the latter, refer to the following methods:
    * <UL>
    *    <LI>{@link org.w3c.dom.Element#getAttribute(String)}</LI>
    *    <LI>{@link org.w3c.dom.Element#getElementsByTagName(String)}</LI>
    *    <LI>{@link org.w3c.dom.Node#getChildNodes()}</LI>
    * </UL>
    * The <CODE>text</CODE> argument for all 'end' events is the same as the
    * <CODE>text</CODE> argument for the corresponding 'start' events.  This is so when
    * an 'end' event fires, one can easily identify the specific element to which
    * the event corresponds.  This argument does not include leading spaces regardless of -i
    * operator.
    * <BR><BR>
    * For debugging purposes, all events in the system can be suppressed for a single
    * execution of the Inspector using the -e option.  If this option is used, the Inspector
    * acts merely as a VerbNet viewer for that exection.  This is so a researcher does
    * not have to write any short-circuit code if they don't want to fire their events
    * temporarily.  He or she can just supply an extra option on the command line.
    * <BR><BR>
    * If you are integrating the Inspector into an existing application (as opposed to using
    * it as a stand-alone application) and you desire to utilize the VerbNet viewer
    * aspect of the Inspector <I>and</I> you don't want it to send its output (normal
    * or class hierarchy) to stdout, you can redirect this output to an external file
    * temporarily during the execution of the Inspector.  In the 'start' event for
    * PROGRAM, you can insert this line:
    * <PRE>    try
    *    {
    *       System.setOut( new PrintStream( "file.txt" ) );
    *    }
    *    catch( Exception e )
    *    {
    *       e.printStackTrace();
    *    }</PRE>
    * You can reset the {@link java.lang.System} class's stdout writer to the original
    * stream in the 'end' event for PROGRAM with:
    * <PRE>    System.setOut( originalStdOut );</PRE>
    * The variable {@link vn.EventManager#originalStdOut} is a pre-defined class
    * variable that is ready for use.
    *
    * @param type the type of element to which this event corresponds
    *        ({@link vn.EventManager#EVENT_PROGRAM}, {@link vn.EventManager#EVENT_FILE}, etc.)
    * @param startOrEnd whether this event is for the beginning of the
    *        element or the end of the element
    *        ({@link vn.EventManager#EVENT_START} or {@link vn.EventManager#EVENT_END})
    * @param curFile the name of the file currently being processed (i.e. approve-77.xml).  This argument is
    *        <CODE>null</CODE> for the PROGRAM element.
    * @param curClass the name of the class or subclass currently being processed (i.e. devour-39.4-1).
    *        This argument is <CODE>null</CODE> for the PROGRAM and FILE elements.
    * @param text the simple-text representation of the element to which this
    *        event corresponds.  This text is equivalent to the text that would be
    *        printed for this element had it been printed by the Inspector under the
    *        view options -Vab (full output).  For the PROGRAM element, this argument is
    *        equal to the concatenation of all the command line elements with spaces.
    * @param n the XML node corresponding to the element being visited.  This argument is
    *        <CODE>null</CODE> for the PROGRAM and FILE elements.  For verb-frame pairs,
    *        this is the XML node corresponding to the MEMBER element in the verb-frame
    *        pair.
    * @param nExtra the XML node corresponding to the FRAME element in the verb-frame
    *        pair being visited.  This argument is <CODE>null</CODE> for all other elements.
    */
   static void fireEvent( int type, int startOrEnd, String curFile, String curClass,
                          String text, Element n, Element nExtra )
   {
      switch( type )
      {

         // Text parameter for 'start' and 'end' events for program is the original
         // command line without the java command and class name used to execute the
         // program (just the program options).  These are separated by spaces.
         case EVENT_PROGRAM:

            // 'Start' event for program fires if there were no problems with the command
            // line arguments and if neither -? nor -k was specified.  This event fires
            // before the header is printed.
            if( startOrEnd == EVENT_START )
            {
               /******************************************************************
                *** Insert your code here for: BEGINNING OF PROGRAM            ***
                *** Remember: curFile, curClass, text, and n are available     ***
                ******************************************************************/
            }

            // 'End' event for program fires if and only if the 'start' event fired.
            // This event fires after the final counts have been printed.
            else
            {
               /******************************************************************
                *** Insert your code here for: END OF PROGRAM                  ***
                *** Remember: curFile, curClass, text, and n are available     ***
                ******************************************************************/
            }
            break;

         case EVENT_FILE:

            if( startOrEnd == EVENT_START )
            {
               /******************************************************************
                *** Insert your code here for: BEGINNING OF FILE               ***
                *** Remember: curFile, curClass, text, and n are available     ***
                ******************************************************************/
            }

            // 'End' event for file fires after all the events for the main class
            // in the file have fired.
            else
            {
               /******************************************************************
                *** Insert your code here for: END OF FILE                     ***
                *** Remember: curFile, curClass, text, and n are available     ***
                ******************************************************************/
            }
            break;

         case EVENT_CLASS:

            if( startOrEnd == EVENT_START )
            {
               /******************************************************************
                *** Insert your code here for: BEGINNING OF MAIN CLASS         ***
                *** Remember: curFile, curClass, text, and n are available     ***
                ******************************************************************/
            }

            // 'End' event for class fires after events for the class's
            // members, thematic roles, frames, verb-frame pairs (if applicable),
            // and subclasses have all fired.
            else
            {
               /******************************************************************
                *** Insert your code here for: END OF MAIN CLASS               ***
                *** Remember: curFile, curClass, text, and n are available     ***
                ******************************************************************/
            }
            break;

         case EVENT_SUBCLASS:

            if( startOrEnd == EVENT_START )
            {
               /******************************************************************
                *** Insert your code here for: BEGINNING OF SUBCLASS           ***
                *** Remember: curFile, curClass, text, and n are available     ***
                ******************************************************************/
            }

            // 'End' event for subclass fires after events for the subclass's
            // members, thematic roles, frames, verb-frame pairs (if applicable),
            // and subclasses have all fired.
            else
            {
               /******************************************************************
                *** Insert your code here for: END OF SUBCLASS                 ***
                *** Remember: curFile, curClass, text, and n are available     ***
                ******************************************************************/
            }
            break;

         case EVENT_MEMBER:

            if( startOrEnd == EVENT_START )
            {
               /******************************************************************
                *** Insert your code here for: BEGINNING OF MEMBER             ***
                *** Remember: curFile, curClass, text, and n are available     ***
                ******************************************************************/
            }

            // 'End' event for member fires immediately after 'start' event.  Only
            // fires at all for completeness.
            else
            {
               /******************************************************************
                *** Insert your code here for: END OF MEMBER                   ***
                *** Remember: curFile, curClass, text, and n are available     ***
                ******************************************************************/
            }
            break;

         case EVENT_THEMROLE:

            if( startOrEnd == EVENT_START )
            {
               /******************************************************************
                *** Insert your code here for: BEGINNING OF THEMATIC ROLE      ***
                *** Remember: curFile, curClass, text, and n are available     ***
                ******************************************************************/
            }

            // 'End' event for thematic role fires immediately after 'start' event.
            // Only fires at all for completeness.
            else
            {
               /******************************************************************
                *** Insert your code here for: END OF THEMATIC ROLE            ***
                *** Remember: curFile, curClass, text, and n are available     ***
                ******************************************************************/
            }
            break;

         case EVENT_FRAME:

            if( startOrEnd == EVENT_START )
            {
               /******************************************************************
                *** Insert your code here for: BEGINNING OF FRAME              ***
                *** Remember: curFile, curClass, text, and n are available     ***
                ******************************************************************/
            }

            // 'End' event for frame fires after events for the frame's
            // examples, syntax, and semantic predicates have fired.
            else
            {
               /******************************************************************
                *** Insert your code here for: END OF FRAME                    ***
                *** Remember: curFile, curClass, text, and n are available     ***
                ******************************************************************/
            }
            break;

         // Almost 100% of frames have exactly 1 example.  A few have 2 or 3 examples.
         case EVENT_EXAMPLE:

            if( startOrEnd == EVENT_START )
            {
               /******************************************************************
                *** Insert your code here for: BEGINNING OF EXAMPLE            ***
                *** Remember: curFile, curClass, text, and n are available     ***
                ******************************************************************/
            }

            // 'End' event for example fires immediately after 'start' event.  Only
            // fires at all for completeness.
            else
            {
               /******************************************************************
                *** Insert your code here for: END OF EXAMPLE                  ***
                *** Remember: curFile, curClass, text, and n are available     ***
                ******************************************************************/
            }
            break;

         case EVENT_SYNTAX:

            if( startOrEnd == EVENT_START )
            {
               /******************************************************************
                *** Insert your code here for: BEGINNING OF SYNTAX             ***
                *** Remember: curFile, curClass, text, and n are available     ***
                ******************************************************************/
            }

            // 'End' event for syntax fires immediately after 'start' event.  Only
            // fires at all for completeness.
            else
            {
               /******************************************************************
                *** Insert your code here for: END OF SYNTAX                   ***
                *** Remember: curFile, curClass, text, and n are available     ***
                ******************************************************************/
            }
            break;

         // Events do not fire for the SEMANTICS section as a whole, only
         // for individual predicates.
         case EVENT_SEMANTIC_PRED:

            if( startOrEnd == EVENT_START )
            {
               /******************************************************************
                *** Insert your code here for: BEGINNING OF SEMANTIC PRED      ***
                *** Remember: curFile, curClass, text, and n are available     ***
                ******************************************************************/
            }

            // 'End' event for semantic predicate fires immediately after 'start'
            // event.  Only fires at all for completeness.
            else
            {
               /******************************************************************
                *** Insert your code here for: END OF SEMANTIC PRED            ***
                *** Remember: curFile, curClass, text, and n are available     ***
                ******************************************************************/
            }
            break;

         // Events do not fire for individual members or frames when running
         // in verb-frame pair mode.
         case EVENT_VF_PAIR:

            if( startOrEnd == EVENT_START )
            {
               /******************************************************************
                *** Insert your code here for: BEGINNING OF VERB-FRAME PAIR    ***
                *** Remember: curFile, curClass, text, n, and nExtra           ***
                *** are available                                              ***
                ******************************************************************/
            }

            // 'End' event for verb-frame pair fires after events for the verb-frame
            // pair's examples, syntax, and semantic predicates have fired.
            else
            {
               /******************************************************************
                *** Insert your code here for: END OF VERB-FRAME PAIR          ***
                *** Remember: curFile, curClass, text, n, and nExtra           ***
                *** are available                                              ***
                ******************************************************************/
            }
            break;

         // This event fires when the FRAMES element closes in the XML file (a.k.a.
         // when the </FRAMES> closing tag  is reached).  Although this is not
         // synonymous with the end of a class, as each class contains subclasses
         // inside it, it does basically represent the end
         // of the content area for a class (members, thematic roles, and frames).
         // Another way to conceptualize this is that this event fires right
         // before the beginning of each new class and subclass, and once at the end
         // of the scanning.  This event is necessary if you want to create
         // a hierarchically-correct output.  The 'text' parameter is a zero-length
         // string and the 'n' parameter represents the FRAMES element.
         case EVENT_END_FRAMES:

            // Only an 'end' event is fired for this event.
            if( startOrEnd == EVENT_END )
            {
               /******************************************************************
                *** Insert your code here for: END OF FRAMES ELEMENT           ***
                *** Remember: curFile, curClass, and n are available           ***
                ******************************************************************/
            }
            break;
      }
   }

   ////////////
   // Fields //
   ////////////

   /**
    * Identifies that the event firing corresponds to the beginning of the element in question.
    *
    * @see vn.EventManager#fireEvent(int, int, String, String, String, Element, Element)
    */
   static final int EVENT_START = 0;

   /**
    * Identifies that the event firing corresponds to the end of the element in question.
    *
    * @see vn.EventManager#fireEvent(int, int, String, String, String, Element, Element)
    */
   static final int EVENT_END = 1;

   /**
    * Identifies that the event is for the entire program.
    *
    * @see vn.EventManager#fireEvent(int, int, String, String, String, Element, Element)
    */
   static final int EVENT_PROGRAM = 0;

   /**
    * Identifies that the event is for a single XML file.
    *
    * @see vn.EventManager#fireEvent(int, int, String, String, String, Element, Element)
    */
   static final int EVENT_FILE = 1;

   /**
    * Identifies that the event is for a main class.
    *
    * @see vn.EventManager#fireEvent(int, int, String, String, String, Element, Element)
    */
   static final int EVENT_CLASS = 2;

   /**
    * Identifies that the event is for a subclass.
    *
    * @see vn.EventManager#fireEvent(int, int, String, String, String, Element, Element)
    */
   static final int EVENT_SUBCLASS = 3;

   /**
    * Identifies that the event is for a single member (verb).
    *
    * @see vn.EventManager#fireEvent(int, int, String, String, String, Element, Element)
    */
   static final int EVENT_MEMBER = 4;

   /**
    * Identifies that the event is for a thematic role.
    *
    * @see vn.EventManager#fireEvent(int, int, String, String, String, Element, Element)
    */
   static final int EVENT_THEMROLE = 5;

   /**
    * Identifies that the event is for a frame.
    *
    * @see vn.EventManager#fireEvent(int, int, String, String, String, Element, Element)
    */
   static final int EVENT_FRAME = 6;

   /**
    * Identifies that the event is for an example.
    *
    * @see vn.EventManager#fireEvent(int, int, String, String, String, Element, Element)
    */
   static final int EVENT_EXAMPLE = 7;

   /**
    * Identifies that the event is for syntax.
    *
    * @see vn.EventManager#fireEvent(int, int, String, String, String, Element, Element)
    */
   static final int EVENT_SYNTAX = 8;

   /**
    * Identifies that the event is for a single semantic predicate.  There are no
    * events that fire for the SEMANTICS element as a whole, only one for each
    * semantic predicate.
    *
    * @see vn.EventManager#fireEvent(int, int, String, String, String, Element, Element)
    */
   static final int EVENT_SEMANTIC_PRED = 9;

   /**
    * Identifies that the event is for a verb-frame pair.
    *
    * @see vn.EventManager#fireEvent(int, int, String, String, String, Element, Element)
    */
   static final int EVENT_VF_PAIR = 10;

   /**
    * Identifies the moment right before another class begins.  This is synonymous with
    * &lt;/FRAMES> but not synonymous with end of class.  So a special event is needed.
    * This event only has an 'end' event.
    *
    * @see vn.EventManager#fireEvent(int, int, String, String, String, Element, Element)
    */
   static final int EVENT_END_FRAMES = 11;

   /**
    * The original stdout stream reference from the {@link java.lang.System} class.
    * This is saved in the static initializer for this class and exists just in case
    * the stdout stream is reset to a custom file in the
    * {@link vn.EventManager#fireEvent(int, int, String, String, String, Element, Element)}.
    * A researcher can use this reference to reset the {@link java.lang.System} class's stdout
    * stream back to the original stream whenever desired.
    *
    * @see java.lang.System#out
    * @see java.lang.System#setOut(PrintStream)
    */
   private static PrintStream originalStdOut;

   /**
    * Save the original stdout stream reference in case it is reset to a
    * custom file in the fireEvent method.
    */
   static
   {
      originalStdOut = System.out;
   }

   /////////////////
   // Constructor //
   /////////////////

   /**
    * This constructor is private because the class is not intended to ever
    * be instantiated.  The Inspector is a very procedural process and
    * thus all the members are static.
    */
   private EventManager() {}

   /////////////////////////////////////////////////////
   // Inspector Implementation Method - Do Not Modify //
   /////////////////////////////////////////////////////

   /**
    * Fires an event if events are enabled for this execution of the Inspector.
    * This method exists only to implement the "suppress all events" option (-e)
    * of the Inspector.  Events are enabled by default.  This option must be
    * supplied to prevent them from firing.  If the events are not being
    * suppressed, this method simply hands the arguments given to it to the
    * real <CODE>fireEvent</CODE> method.  It also makes a quick conversion between
    * {@link org.w3c.dom.Node}s and {@link org.w3c.dom.Element}s for code simplification
    * purposes only.  Do not modify this method.
    *
    * @param type the type of element to which this event corresponds
    *        ({@link vn.EventManager#EVENT_PROGRAM}, {@link vn.EventManager#EVENT_FILE}, etc.)
    * @param startOrEnd whether this event is for the beginning of the
    *        element or the end of the element
    *        ({@link vn.EventManager#EVENT_START} or {@link vn.EventManager#EVENT_END})
    * @param curFile the name of the file currently being processed (i.e. approve-77.xml).  This argument is
    *        <CODE>null</CODE> for the PROGRAM element.
    * @param curClass the name of the class or subclass currently being processed (i.e. devour-39.4-1).
    *        This argument is <CODE>null</CODE> for the PROGRAM and FILE elements.
    * @param text the simple-text representation of the element to which this
    *        event corresponds.  This text is equivalent to the text that would be
    *        printed for this element had it been printed by the Inspector under the
    *        view options -Vab (full output).  For the PROGRAM element, this argument is
    *        equal to the concatenation of all the command line elements with spaces.
    * @param n the XML node corresponding to the element being visited.  This argument is
    *        <CODE>null</CODE> for the PROGRAM and FILE elements.  For verb-frame pairs,
    *        this is the XML node corresponding to the MEMBER element in the verb-frame
    *        pair.
    * @param nExtra the XML node corresponding to the FRAME element in the verb-frame
    *        pair being visited.  This argument is <CODE>null</CODE> for all other elements.
    * @see vn.EventManager#fireEvent(int, int, String, String, String, Element, Element)
    * @see vn.Inspector#flSuppressEvents
    */
   static void fireEventMaybe( int type, int startOrEnd, String curFile, String curClass,
                               String text, Node n, Node nExtra )
   {
      if( !Inspector.flSuppressEvents )
         fireEvent( type, startOrEnd, curFile, curClass, text, ( Element ) n, ( Element ) nExtra );
   }
}
