
//////////////////////////////
// The Inspector            //
// Mock Application         //
// University of Colorado   //
// Fall 2006                //
//////////////////////////////

package vn;

import org.w3c.dom.*;
import java.io.*;
import java.util.*;        // Added to support ArrayList used in custom code.

/**
 * This class implements the mock application.  When extending the Inspector
 * one does not need to change the files Inspector.java or Sweeper.java.
 * One only needs to change this file, EventManager.java.  The goal of the
 * mock application is to demonstrate what elements of Java code should go where
 * when modifying this file.  This mock application
 * is small and attempts to find a mapping between VerbNet and an invented
 * toy lexicon called TOYLEX. This lexicon is enumerated here:
 *
 * <TABLE style='border:1px #000000 solid' cellpadding=4 align='center'>
 *    <TR><TD colspan=2 align='center'>TOYLEX</TD></TR>
 *    <TR><TD><U>Verb</U></TD><TD><U>Semantics</U></TD></TR>
 *    <TR><TD><B>run</B></TD><TD>horizontal movement</TD></TR>
 *    <TR><TD><B>walk</B></TD><TD>horizontal movement</TD></TR>
 *    <TR><TD><B>jump</B></TD><TD>vertical movement</TD></TR>
 *    <TR><TD><B>spring</B></TD><TD>vertical movement</TD></TR>
 *    <TR><TD><B>push</B></TD><TD>move by force</TD></TR>
 *    <TR><TD><B>shove</B></TD><TD>move by force</TD></TR>
 * </TABLE>
 * <BR>
 * This stand-alone application is invoked with <PRE>   java vn.Inspector xml/ -q</PRE>
 * The verb-frame pairs option (-q) is used to implement this application.  This option
 * displays a verb-frame pair for each frame that a verb can participate in.  There
 * are close to 30,000 such pairs.  One can imagine other ways to implement the same
 * mock application, without using verb-frame pairs as well, since this event interface
 * is as generic as possible.
 * <BR><BR>
 * The output of this program is essentially the mapping between VerbNet and TOYLEX.  A single
 * line of text is printed for each VerbNet-TOYLEX match.  The matches are determined
 * by seeing if various rules apply to pairs of VerbNet and TOYLEX data.
 *
 * @see vn.EventManager#fireEvent(int, int, String, String, String, Element, Element)
 *
 * @author Derek Trumbo
 * @version 1.0, 2006.10.18
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

   /**
    * A temporary variable to store the verb of a verb-frame pair when its
    * 'start' event is fired until it can be used when the 'start' event for
    * syntax is fired.
    */
   private static String verb;

   /**
    * Holds all the lexical entries for our TOYLEX lexicon.
    * See the static initializer for more information.
    */
   private static ArrayList myLexicon = new ArrayList();

   /**
    * Represents a single lexical entry in our TOYLEX lexicon.
    * Each entry just has a verb and some arbitrarily chosen phrases
    * to represent some semantics for the verb.
    */
   private static class MyLexiconEntry
   {
      /** Verb of the entry. */
      private String verb;

      /** Semantics of the entry. */
      private String semantics;

      /**
       * Constructor to initialize the entry.
       */
      public MyLexiconEntry( String v, String s )
      {
         verb = v;
         semantics = s;
      }
   }

   // Static initializer block can be used for any required initialization code.
   // Initializes the TOYLEX lexicon.  This builds the database of knowledge for
   // our lexicon, that will be used when mapping between VerbNet and TOYLEX.
   static
   {
      myLexicon.add( new MyLexiconEntry( "run", "horizontal movement" ) );
      myLexicon.add( new MyLexiconEntry( "walk", "horizontal movement" ) );
      myLexicon.add( new MyLexiconEntry( "jump", "vertical movement" ) );
      myLexicon.add( new MyLexiconEntry( "spring", "vertical movement" ) );
      myLexicon.add( new MyLexiconEntry( "push", "move by force" ) );
      myLexicon.add( new MyLexiconEntry( "shove", "move by force" ) );
   }

   ///////////////////////////////////////////////
   // Researcher Method - Extend Inspector Here //
   ///////////////////////////////////////////////

   /**
    * Captures events from the Inspector scanning system and looks for possible mappings
    * (matches) between the VerbNet data and TOYLEX.  The only events this method
    * needs to act on to make this happen (at least for our toy lexicon) is 'start'
    * verb-frame pair and 'start' semantics predicate.  Just like the 'start' events
    * for frames, the 'start' events for verb-frame pairs fire before the events for the
    * examples, syntax, and semantic predicates that are contained within.
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

               // Show an error message and stop the program if the mock-application
               // is not running in verb-frame pair mode.
               if( !Inspector.flVFPairs )
               {
                  System.err.println( "ERROR: The mock application must run in verb-frame " +
                     "pair mode.  Use -q or -Vq." );

                  System.exit( 0 );
               }
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

               // Now that both the verb and semantic predicate is available (the
               // verb was saved when the 'start' verb-frame event fired).  We can
               // compare this verb-frame pair to our toy lexicon, TOYLEX, by applying
               // one or more rules to decide if there is a match between the VerbNet
               // representation and our lexicon's representation.

               // Scan through all entries in TOYLEX, looking for a match beween
               // it and this VerbNet verb-frame pair.
               for( int v = 0; v < myLexicon.size(); v++ )
               {
                  MyLexiconEntry e = ( MyLexiconEntry ) myLexicon.get( v );

                  // If the verb of this verb-frame pair matches a verb in the
                  // TOYLEX lexicon (just match up the lemmas first).
                  if( verb.equals( e.verb ) )
                  {

                     // Grab the name of this predicate.
                     String predName = n.getAttribute( "value" );

                     // Apply a couple of rules to decide if there is a match between
                     // VerbNet and TOYLEX.  If VerbNet has the predicate 'motion'
                     // and the TOYLEX semantics for this entry has the token
                     // 'movement' within or if VerbNet has the predicate 'exert_force'
                     // and the TOYLEX semantics for this entry has the token
                     // 'force' then effect the match.
                     if( predName.equals( "motion" ) && e.semantics.indexOf( "movement" ) != -1 ||
                         predName.equals( "exert_force" ) && e.semantics.indexOf( "force" ) != -1 )

                        // Print some details of the match.
                        System.out.println( "- Match: " + verb +
                                            " (VN Class: " + curClass +
                                            ", TOYLEX Sem: " + e.semantics +
                                            ", VN Sem Pred: " + text  + ")" );
                     break;
                  }
               }
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

               // Store the verb of this verb-frame pair into a temporary variable
               // so it will be available when the 'start' event for each
               // semantic predicate is fired.  The 'start' event for each
               // verb-frame pair is fired immediately before the examples,
               // syntax, and semantic predicates are encountered.  If there's
               // ever confusion as to the order of firing, just use the Inspector
               // as a viewer to help visualize:  java vn.Inspector xml/ -Vabq -e

               verb = n.getAttribute( "name" );
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
