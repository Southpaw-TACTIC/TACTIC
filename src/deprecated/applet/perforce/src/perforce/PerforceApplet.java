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



package perforce;

import java.io.*;
import java.util.*;
import java.security.*;
import javax.swing.*;


public class PerforceApplet extends JApplet
{
    String my_ticket = "";

    public void init()
    {
    }

    // public functions available to javascript
    public void set_ticket(String ticket_id)
    {
        my_ticket = ticket_id;
    }    


    public void exec(final String cmd)
    {
        exec(cmd, true);    
    }


    public void exec(final String cmd, final boolean wait_for)
    {
        AccessController.doPrivileged( new PrivilegedAction() {
            public Object run() {
                try {
                    System.out.println("cmd: " + cmd);
                    String tmp_cmd = cmd.replaceAll("\\\\/", "\\");

                    Runtime runtime = Runtime.getRuntime();
                    Process process = runtime.exec( new String[] { "cmd.exe", "/c", tmp_cmd } );
                    if (wait_for == true)
                        process.waitFor();
                }
                catch (Exception e) {
                    System.out.println(e.getMessage());
                }
                return null;
            }
        } );
        System.runFinalization();
        System.gc();
    }



    // Execute a perforce command
    public String perforce(final String cmd)
    {
        final StringBuffer hex_data = new StringBuffer();
        AccessController.doPrivileged( new PrivilegedAction() {
            public Object run() {
                try {
                    Perforce perforce = new Perforce();
                    byte[] data = perforce.execute2( " -G " + cmd);
                    hex_data.append( Common.hexify(data) );
                }
                catch (Exception e) {
                    System.out.println(e.getMessage());
                }
                return null;
            }
        } );


        return hex_data.toString();
    }



    public String get_files(final String path)
    {
        final ArrayList file_paths = new ArrayList();
        AccessController.doPrivileged( new PrivilegedAction() {
            public Object run() {
                try {
                    _get_files(path, file_paths);
                }
                catch (Exception e) {
                    System.out.println(e.getMessage());
                }
                return null;
            }
        } );


        String[] paths = new String[file_paths.size()];
        file_paths.toArray(paths);
        return join(paths, "|");
       
    }

    private void _get_files(String file_path, ArrayList file_paths)
    {
        try {
            File file = new File(file_path);
            File[] tmp_files = file.listFiles();
            for (int i = 0; i < tmp_files.length; i++ )
            {
                String absolute_path = tmp_files[i].getAbsolutePath();
                if ( tmp_files[i].isDirectory() == true ) {
                    _get_files(absolute_path, file_paths);
                }
                else {
                    file_paths.add(absolute_path);
                }
            }
        }
        catch (Exception e) {
            System.out.println(e.getMessage());
        }
    }


    public String commit(final String[] paths, final String comment, final String root)
    {
        String ret_val = (String)AccessController.doPrivileged( new PrivilegedAction() {
            public Object run() {
                try {
                    Perforce perforce = new Perforce();
                    return perforce.commit(paths, comment, root);
                }
                catch (Exception e) {
                    System.out.println(e.getMessage());
                }
                return null;
            }
        } );
        return ret_val;
    }



    public void makedirs(final String path)
    {
        AccessController.doPrivileged( new PrivilegedAction() {
            public Object run() {
                try {
                    File file = new File(path);
                    if ( file.exists() == false )
                        file.mkdirs();
                }
                catch (Exception e) {
                    System.out.println(e.getMessage());
                }
                return null;
            }
        } );
       
    }



    private String join(String[] a, String separator) {
        StringBuffer result = new StringBuffer();
        if (a.length > 0) {
            result.append(a[0]);
            for (int i=1; i<a.length; i++) {
                result.append(separator);
                result.append(a[i]);
            }
        }
        return result.toString();
    }



    // Perforce commands
    public String get_repo(final String path, final boolean synced)
    {
        final ArrayList file_paths = new ArrayList();
        AccessController.doPrivileged( new PrivilegedAction() {
            public Object run() {
                try {
                    Perforce perforce = new Perforce();
                    String[] files = perforce.get_repo(path, synced);
                    for (int i = 0; i < files.length; i++) {
                        file_paths.add(files[i]);
                    }
                }
                catch (Exception e) {
                    System.out.println(e.getMessage());
                }
                return null;
            }
        } );


        String[] paths = new String[file_paths.size()];
        file_paths.toArray(paths);
        return join(paths, "|");
    }



    public String get_checkout(final String path)
    {
        final ArrayList file_paths = new ArrayList();
        AccessController.doPrivileged( new PrivilegedAction() {
            public Object run() {
                try {
                    Perforce perforce = new Perforce();
                    String[] files = perforce.get_checkout(path);
                    for (int i = 0; i < files.length; i++) {
                        file_paths.add(files[i]);
                    }
                }
                catch (Exception e) {
                    System.out.println(e.getMessage());
                }
                return null;
            }
        } );
        String[] paths = new String[file_paths.size()];
        file_paths.toArray(paths);
        return join(paths, "|");
    }


    public String add_checkin_path(final String path)
    {
        String ret_val = (String)AccessController.doPrivileged( new PrivilegedAction() {
            public Object run() {
                Perforce perforce = new Perforce();
                return perforce.checkin(path);
            }
        } );
        return ret_val;
    }

    public String add_checkout_path(final String path)
    {
        String ret_val = (String)AccessController.doPrivileged( 
            new PrivilegedAction() {
            public Object run() {
                Perforce perforce = new Perforce();
                return perforce.edit(path);
            }
        } );

        return ret_val;
    }

    public String revert(final String path)
    {
        String ret_val = (String)AccessController.doPrivileged( 
            new PrivilegedAction() {
            public Object run() {
                Perforce perforce = new Perforce();
                return perforce.revert(path);
            }
        } );

        return ret_val;
    }

    public String sync(final String path)
    {
        String ret_val = (String)AccessController.doPrivileged( 
            new PrivilegedAction() {
            public Object run() {
                Perforce perforce = new Perforce();
                return perforce.sync(path);
            }
        } );

        return ret_val;
    }
    
    /* get the client's root directory */
    public String get_root()
    {
        String ret_val = (String)AccessController.doPrivileged( 
            new PrivilegedAction() {
            public Object run() {
                Perforce perforce = new Perforce();
                return perforce.get_root();
            }
        } );

        return ret_val;
    }
        

   

}


