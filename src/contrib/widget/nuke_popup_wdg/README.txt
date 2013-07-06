HOW TO INSTALL NUKE INTEGRATION



Step 1)  init.py - goes in    xp:   c:/documents and settings/<user>/.nuke
                              win7: c:/users/<user>/.nuke


------------------------------------------------------------------

Step 2)  nuke_wdg_panel - goes in widget config as

            I.  category: CustomLayoutWdg
            II. search_type: CustomLayoutWdg
            III.view: nuke_wdg
            IV. config: <contents of nuke_wdg_panel.txt> (Copy and paste)
      
            - Only the files content is used and not the file itself.

------------------------------------------------------------------

Step 3)  nuke_wdg_button - goes in definition for search type used above

            I.  Go to Manage Search Type View
            II. Choose the Search Type eg. prod/shot
            III.Select New Widget Column from the Action drop down list
            IV. Mode = XML
            V.  Copy and paste the contents from the nuke_wdg_button.txt file into the Config XML Definition
            VI. Uncheck the Create required column
            VII.Click Add/exit

             - Only the files content is used and not the file itself.

------------------------------------------------------------------

Step 4)  The nuke logo gets placed in the TACTIC server's assets dir under

            /assets/sthpw/widget/nuke_wdg/

            *create the directory if it doesn't exist

------------------------------------------------------------------


Step 5)  The tactic_nuke_server script is placed in the nukescripts folder:

             <nuke_install_directory>/plugins/nukescripts  

------------------------------------------------------------------


Step 6)  Insert the directory path of Nuke6*.exe into the Environment Variables within the Windows System Properties

             *In the Zip file there is a systemPath_ScreenShot file(jpeg) example of this.

                      eg. c:\Program Files\Nuke6.0v2\;

