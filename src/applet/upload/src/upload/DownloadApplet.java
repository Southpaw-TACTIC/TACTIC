/* *********************************************************
 *
 * Copyright (c) 2005, Southpaw Technology
 *                     All Rights Reserved
 * 
 * PROPRIETARY INFORMATION.  This software is proprietary to
 * Southpaw Technology, and is not to be reproduced, transmitted,
 * or disclosed in any way without written permission.
 * 
 * 
 */ 



package upload;


import java.util.*;
import java.awt.*;
import javax.swing.*;
import java.security.*;


public class DownloadApplet extends JApplet
{

    private Download my_download;


    public void init()
    {
        System.out.println("Now Starting Applet");
    }


    public void test()
    {
        System.out.println("Testing ...");
    }


    // public functions available to javascript

    public void do_download(String url, String to_path)
    {
        final String f_url = url;
        final String f_to_path = to_path;


        AccessController.doPrivileged( new PrivilegedAction() {
            public Object run() {

                my_download = new Download();

                int read = my_download.do_download( f_url, f_to_path );
                System.out.println( "downloaded: "+read);

                return null;
            }
        });
    }



}



