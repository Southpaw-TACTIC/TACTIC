/* *********************************************************
 *
 * Copyright (c) 2005, Southpaw Technology
 *                     All Rights Reserved
 * 
 * PROPRIETARY INFORMATION.  This software is proprietary to
 * Southpaw Technology, and is not to be reproduced, transmitted,
 * or disclosed in any way without written permission.
 * 
 * AUTHOR:
 *     Remko Noteboom
 * 
 */ 


package upload;

import java.io.*;
import java.util.*;
import java.awt.*;
import javax.swing.*;
import java.security.*;


public class UploadApplet extends JApplet
{

    GuiCreator my_gui;


    public void init()
    {
        try {
            javax.swing.SwingUtilities.invokeAndWait(
                new Runnable() {
                    public void run() {
                        create_gui();
                    }
                }
            );
        }
        catch (Exception e)
        {
            e.printStackTrace();
        }

    }


    private void create_gui()
    {
        Container content_pane = getContentPane();

        my_gui = new GuiCreator(content_pane);
        my_gui.create_gui();
    }





    // public functions available to javascript
    public void set_server_url(String url)
    {
        my_gui.set_server_url(url);
    }

    public void set_ticket(String ticket_id)
    {
        my_gui.set_ticket(ticket_id);
    }
    

        
    public void do_upload()
    {
        AccessController.doPrivileged( new PrivilegedAction() {
            public Object run() {
                try
                {
                    my_gui.execute();
                }
                catch (IOException e)
                {
                }
                return null;
            }
        });
    }
   

    public String get_uploaded_files()
    {
       ArrayList uploads = my_gui.get_uploads();

       if ( uploads.size() != 0 )
       {
           // add initial entry
           Upload upload = (Upload) uploads.get(0);
           String file_names = upload.get_to_filename();
            
            for ( int i = 1; i < uploads.size(); i++ )
            {
                upload = (Upload) uploads.get(i);
                file_names = file_names + "|" + upload.get_to_filename();
            }
            System.out.println("size: " + uploads.size());
            System.out.println("file_names: " + file_names);
            return file_names;
       }
       else
           return "";
    }


}



