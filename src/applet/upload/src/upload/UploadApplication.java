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

import java.awt.*;
import javax.swing.*;
import javax.swing.table.*;
import java.awt.event.*;


public class UploadApplication
{

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
        JFrame.setDefaultLookAndFeelDecorated( false );
        JFrame frame = new JFrame("Upload");
        frame.setDefaultCloseOperation( JFrame.EXIT_ON_CLOSE );

        final Container content_pane = frame.getContentPane();

        GuiCreator gui = new GuiCreator( content_pane );
        gui.create_gui();


        frame.pack();
        frame.setVisible(true);
    }



    public static void main( String args[] )
    {
        UploadApplication app = new UploadApplication();
        app.init();
    }


}



