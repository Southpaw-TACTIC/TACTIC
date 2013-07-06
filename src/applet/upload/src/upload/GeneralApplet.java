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

import java.io.*;
import java.security.*;
import javax.swing.*;
import java.awt.*;
import java.net.*;
import javax.net.ssl.*;
import java.util.*;
import java.util.zip.*;

//import net.sf.json.*;
import com.google.gson.Gson;

public class GeneralApplet extends JApplet
{
    String my_ticket = "";
    HashMap my_download_map = new HashMap();
    StringBuffer my_log_content = new StringBuffer();
    String my_connect_error = new String();
    Hashtable my_envp = new Hashtable();

    public void init()
    {
    }

    // public functions available to javascript
    public void set_ticket(String ticket_id)
    {
        my_ticket = ticket_id;
    }    
   
    public void exec_shell(final String cmd, final boolean wait_for)
    {
        exec(cmd, null, wait_for, true);
    }
    public void exec(final String cmd)
    {
        exec(cmd, null, true, false);    
    }

    public void exec(final String cmd, final boolean wait_for)
    {
        this.exec(cmd, null, wait_for, false);
    }


    public void exec(final String cmd, final String[] envp, final boolean wait_for, final boolean is_shell)
    {
        AccessController.doPrivileged( new PrivilegedAction() {
            public Object run() {
                try {
                    System.out.println("cmd: " + cmd);
                    String tmp_cmd = cmd.replaceAll("\\\\/", "\\");

                    // handle the env
                    ArrayList envp = new ArrayList();
                    Enumeration e = my_envp.keys();
                    int count_envp = 0;
                    while( e.hasMoreElements() ) {
                        String name = (String) e.nextElement();
                        String value = (String) my_envp.get(name);
                        String expr = new String(name+"="+value);
                        envp.add(expr);
                        count_envp += 1;
                    }
                    String[] envp_array = new String[count_envp];
                    envp.toArray(envp_array);

                    // execute the external command
                    Runtime runtime = Runtime.getRuntime();
                    String[] cmd_array = new String[] {};
                    if (GeneralApplet.is_windows()) {
                        if (is_shell)
                            cmd_array = new String[] { "cmd.exe", "/c", tmp_cmd }; 
                        else
                            cmd_array = new String[] { tmp_cmd }; 
                    }
                    else {
                        //String[] args = tmp_cmd.split(" ");
                        //cmd_array = args;
                        if (is_shell)
                            cmd_array = new String[] { "bash", "-c", tmp_cmd }; 
                        else
                            cmd_array = new String[] { tmp_cmd }; 
                    }
                    /* 
                    else
                        cmd_array = new String[] { "/usr/bin/open", tmp_cmd }; 
                    */
                    if (envp_array.length == 0) {
                        envp_array = null;
                    }
                    Process process = runtime.exec(cmd_array, envp_array);
                    if (wait_for == true) {
                        process.waitFor();
                    }
                }
                catch (Exception e) {
                    System.out.println("Error executing ..");
                    System.out.println(e.getMessage());
                }
                return null;
            }
        } );
        System.runFinalization();
        System.gc();
    }


    public void download(String url, String to_path)
    {
        download(url, to_path, false);
    }

    public void download(String url, String to_path, boolean skip_if_exists)
    {
        final String f_url = url;
        final String f_to_path = to_path;
        final boolean f_skip_if_exists = skip_if_exists;

        AccessController.doPrivileged( new PrivilegedAction() {
            public Object run() {
                Download download = new Download(f_skip_if_exists);
                System.out.println("source: " + f_url); 
                int read = download.do_download( f_url, f_to_path);
                System.out.println( "downloaded: " + read);
                return null;
            }
        });
    }

    public void download_thread(String url, String to_path)
    {
        download_thread(url, to_path, false);
    }
    
    public void download_thread(String url, String to_path, boolean skip_if_exists)
    {
        final String f_url = url;
        final String f_to_path = to_path;
        final boolean f_skip_if_exists = skip_if_exists;

        AccessController.doPrivileged( new PrivilegedAction() {
            public Object run() {
                DownloadThread download = new DownloadThread(f_skip_if_exists, 
                    f_url, f_to_path);
                System.out.println("source: " + f_url); 
                
                download.start();
                my_download_map.put(f_url, download);
                return null;
            }
        });
    }

    /* get file size */
    public int get_file_size(String url)
    {
        final String f_url = url;
        final Integer f_size = (Integer) AccessController.doPrivileged( new PrivilegedAction() {
            public Object run() {
                DownloadThread download =
                    (DownloadThread) my_download_map.get(f_url);
                if (download == null)
                    return new Integer(0);
                int size = download.get_file_size(f_url);
                return new Integer(size);
            }    
        });
        return f_size.intValue();   
    }
    
    /* Get a completion percentage of the threaded downloads */
    public int get_download_progress(String url)
    {
        final String f_url = url;
        final DownloadThread download = (DownloadThread) my_download_map.get(f_url);
        final Integer f_completion = (Integer) AccessController.doPrivileged( new PrivilegedAction() {
        public Object run() {
        if (download == null)
        {
            System.out.println("Not init");
            return new Integer(0);
        }
        int completion = download.get_completion();
            return new Integer(completion);
         }
        });
        return f_completion.intValue();
    }

    /* Get the exception messages for the threaded downloads */
    public String get_download_error(String url)
    {
        DownloadThread download = (DownloadThread) my_download_map.get(url);
        return download.get_error_message();
        
    }

    /*
    public String do_upload(String url, String from_path)
    {
        return do_upload(url, from_path, null);
    }
    */


    public String do_upload(String url, String from_path, String subdir) throws IOException
    {
        final URL f_url;
        try {
            f_url = new URL(url);
        }
        catch ( MalformedURLException e ) {
            System.out.println(e);
            return null;
        }

        final String f_from_path = from_path;
        final String[] f_to_filename = new String[1];
        final String f_subdir = subdir;

        try {
        AccessController.doPrivileged( new PrivilegedExceptionAction() {
            public Object run() throws IOException{

                try {

                    Upload upload = new Upload( f_url, f_from_path);
                    upload.set_ticket(my_ticket);
                    upload.set_subdir(f_subdir);
                    
                    if (f_url.toString().startsWith("http:"))
                        upload.do_upload();
                    else if (f_url.toString().startsWith("https:"))
                        upload.do_upload();
                    else if (f_url.toString().startsWith("file:"))
                        upload.do_copy();
        
                    f_to_filename[0] = upload.get_to_filename();
                }
                catch ( IOException e ) {
                    System.out.println(e);
                    throw e;
                }
                return null;
            }
        });
        } catch (PrivilegedActionException e) {
             throw new IOException(e.getException().getMessage());
        }
        return f_to_filename[0];
    }



    private long get_dir_size(File dir) {
        long size = 0;
        if (dir.isFile()) {
            size = dir.length();
        } else {
            File[] subFiles = dir.listFiles();

            for (File file : subFiles) {
                if (file.isFile()) {
                    size += file.length();
                } else {
                    size += this.get_dir_size(file);
                }

            }
        }

        return size;
    }


    public long get_size(final String path)
    {
        final Long ret_val = (Long) AccessController.doPrivileged( new PrivilegedAction() {
            public Object run() {
                long size = 0;
                try {
                    File file = new File(path);

                    if (file.isDirectory() ) {
                        size = get_dir_size(file);
                    }
                    else {
                        size = file.length();
                    }
                }
                catch (Exception e) {
                    System.out.println(e.getMessage());
                }
                return new Long(size);
            }
        } );

        return ret_val.longValue();   
       
    }



    public boolean exists(final String path)
    {
        final boolean[] ret_val = new boolean[1];

        AccessController.doPrivileged( new PrivilegedAction() {
            public Object run() {
                try {
                    File file = new File(path);
                    ret_val[0] = file.exists();
                }
                catch (Exception e) {
                    System.out.println(e.getMessage());
                }
                return null;
            }
        } );

        return ret_val[0];
       
    }




    public boolean is_dir(final String path)
    {
        final boolean[] ret_val = new boolean[1];

        AccessController.doPrivileged( new PrivilegedAction() {
            public Object run() {
                try {
                    File file = new File(path);
                    ret_val[0] = file.isDirectory();
                }
                catch (Exception e) {
                    System.out.println(e.getMessage());
                }
                return null;
            }
        } );

        return ret_val[0];
       
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



    public String[] list_dir(final String path)
    {
        final boolean[] ret_val = new boolean[1];

        String[] files = (String[]) AccessController.doPrivileged( new PrivilegedAction() {
            public Object run() {
                String[] files_array = null;
                try {
                    File file = new File(path);
                    if (file.isFile()) {
                        System.out.println("Path ["+path+"] is a file");
                    }
                    else {
                        File[] files = file.listFiles();
                        ArrayList file_paths = new ArrayList();
                        for (int i = 0; i < files.length; i++) {
                            file_paths.add(files[i].getAbsolutePath() );
                        }
                        files_array = new String[files.length];
                        file_paths.toArray(files_array);
                    }

                }
                catch (Exception e) {
                    System.out.println(e.getMessage());
                }
                return files_array;
            }
        } );

        if (files == null) {
            files = new String[0];
        }

        return files;
       
    }


    public String[] list_recursive_dir(final String path, final int max_depth) {
        String[] files = (String[]) AccessController.doPrivileged( new PrivilegedAction() {
            public Object run() {
                ArrayList file_paths = new ArrayList();

                int depth = 0;
                _list_recursive_dir(path, file_paths, depth, max_depth);

                String[] file_array = new String[file_paths.size()];

                file_paths.toArray(file_array);
                return file_array;
            }
        } );

        return files;
    }

    private void _list_recursive_dir(String path, ArrayList file_paths, int depth, int max_depth) {

        String[] file_array = list_dir(path);

        for (int i = 0; i < file_array.length; i++) {
            String file_path = file_array[i];
            file_paths.add( file_path );
            //System.out.println(file_path);
            File file = new File(file_path);

            if ( file.isDirectory() ) {
                if (max_depth != -1 && depth == max_depth) {
                    continue;
                }
                _list_recursive_dir(file_path, file_paths, depth+1, max_depth);
            }
        }
    }






    // Taken from:
    // http://www.anyexample.com/programming/java/java_simple_class_to_compute_md5_hash.xml
    private static String convertToHex(byte[] data) { 
        StringBuffer buf = new StringBuffer();
        for (int i = 0; i < data.length; i++) { 
            int halfbyte = (data[i] >>> 4) & 0x0F;
            int two_halfs = 0;
            do { 
                if ((0 <= halfbyte) && (halfbyte <= 9)) 
                    buf.append((char) ('0' + halfbyte));
                else 
                    buf.append((char) ('a' + (halfbyte - 10)));
                halfbyte = data[i] & 0x0F;
            } while(two_halfs++ < 1);
        } 
        return buf.toString();
    }


    public String get_md5(final String path)
    {
        final String[] hash = new String[1];
        AccessController.doPrivileged( new PrivilegedAction() {
            public Object run() {

                int count;
                byte[] buffer = new byte[1024*64];
                try {
                    
                    InputStream fin = new BufferedInputStream( new FileInputStream(path) );
                    //InputStream fin = new FileInputStream(path);
                    MessageDigest digest = java.security.MessageDigest.getInstance("MD5");
                    do {
                        count = fin.read(buffer);
                        if (count > 0) {
                            digest.update(buffer, 0, count);
                        }
                    } while (count != -1);


                    fin.close();
                    hash[0] = convertToHex( digest.digest() );

                }
                catch (Exception e) {
                    System.out.println("Error: " + e.getMessage());
                }

                return null;
            }
        });

        return hash[0];

    }



    public String get_path_info(final String path)
    {
        final String[] hash = new String[1];

        AccessController.doPrivileged( new PrivilegedAction() {
            public Object run() {
                File file = new File(path);
                if (! file.exists() ) {
                    return null;
                }

                HashMap data = new HashMap();
                long length = file.length();
                long lastModified = file.lastModified();

                data.put("size", length);
                data.put("mtime", lastModified);
                data.put("path", path);

                Gson gson = new Gson();
                String json = gson.toJson(data);
                hash[0] = json;
                return null;
            }
        });


        return hash[0];

    }





    public void create_file(String path, String document)
    {
        final String f_path = path;
        final String f_document = document;
        AccessController.doPrivileged( new PrivilegedAction() {
            public Object run() {
                try {
                     File file = new File(f_path);
                     File parent = file.getParentFile();
                     if ( parent != null && !parent.exists() )
                        parent.mkdirs();

                    FileWriter writer = new FileWriter(f_path);
                    writer.write(f_document);
                    writer.close();
                }
                catch (Exception e) {
                    System.out.println(e.getMessage());
                }
                return null;

            }
        });

    }

    /* Find a file and return the input stream */    
    private FileInputStream find_file(String document)
    {
        try
        {
            FileInputStream fstream = new 
                FileInputStream(document);
            return fstream;
        }
        catch( FileNotFoundException e)
        {
            return null;
        }
        
    }    

        
    /* returns true if param <data> are read in the file */
    public boolean find_in_file(String document, String data)
    {
        final String f_document = document;
        //final int f_max_wait_time = max_wait_time;
        final String f_data = data;
        my_log_content = new StringBuffer();
        
        Boolean content = (Boolean)AccessController.doPrivileged( new PrivilegedAction() {
        
            public Object run() {
                Boolean data_read = null;
                try
                {
                    // Open the file that is the first 
                    // command line parameter
                      
                    //int cycle = f_max_wait_time/1000;
                    
                    //int i = 0;
                    FileInputStream fstream = find_file(f_document);
                    while (fstream == null)
                    {   
                        Thread.sleep(1000);
                        //i++;
                        fstream = find_file(f_document);
                    }
                    /*
                    if (fstream == null)
                        System.out.println("Max publish wait time [" + f_max_wait_time 
                           + "] exceeded.\n"
                           + " Try adjusting the max time in the Prefs Bar");
                    */
                    // Convert our input stream to a DataInputStream
                    
                    BufferedReader d = new
                       BufferedReader(new InputStreamReader(fstream));
                    // Continue to read lines while 
                    // there are still some left to read
                    String line = "";   
                      
                    while ((line = d.readLine()) != null && data_read == null)
                    {
                        // Print file line to screen
                        System.out.println("read_file: " + line);
                        my_log_content.append(line);
                        
                        if (line.equals("false"))
                        {
                            data_read = Boolean.FALSE;
                        }
                        
                        if (line.indexOf(f_data) > 0)
                        {
                            data_read = Boolean.TRUE;
                        }
                        
                    }
                    d.close();
                    
                    
                } 
                catch (Exception e)
                {
                    System.err.println("File input error");
                }
                if (data_read == null)
                    data_read = Boolean.FALSE;
                return data_read; 
             }
        });
        
        return content.booleanValue();
    }


    
    /* This can be called after read_file() */
    public String read_file(String document)
    {
        final String f_document = document;
        my_log_content = new StringBuffer();
        
        String content = (String)AccessController.doPrivileged( new PrivilegedAction() {

        public Object run() {
                try
                {
                 
                    FileInputStream fstream = find_file(f_document);
                    while (fstream == null)
                    {   
                        Thread.sleep(1000);
                        fstream = find_file(f_document);
                    }
                
                    // Convert our input stream to a DataInputStream
                    
                    BufferedReader d = new
                       BufferedReader(new InputStreamReader(fstream));
                    // Continue to read lines while 
                    // there are still some left to read
                    String line = "";   
                      
                    while ((line = d.readLine()) != null )
                    {
                        my_log_content.append(line);
                        my_log_content.append('\n');
                    }

                    fstream.close();
                }
                catch (Exception e)
                {
                    System.err.println("File input error");
                }
                return my_log_content.toString();
             }
        });
        
        return content;
    }

    /* remove a file */
    public void remove_file(String path)
    {
        final String f_path = path;
        AccessController.doPrivileged( new PrivilegedAction() {
            public Object run() {
                try {
                     File file = new File(f_path);
                     file.delete(); 
                }
                catch (Exception e) {
                    System.out.println(e.getMessage());
                }
                return null;

            }
        });

    }


    /* copy a file */
    public void copy_file(String from_path, String to_path) throws IOException{
        final int BUFF_SIZE = 819200;
        final byte[] buffer = new byte[BUFF_SIZE];
        copy_file(from_path, to_path, buffer);
    }

    public void copy_file(String from_path, String to_path, final byte[] buffer) throws IOException
    {
        final String f_path = from_path;
        final String t_path = to_path;
        try {
        AccessController.doPrivileged( new PrivilegedExceptionAction() {
            public Object run() throws IOException{
                try {
                    File from_file = new File(f_path);
                    File to_file = new File(t_path);
                   
                    // create the directory if it exists
                    File parent = to_file.getParentFile();
                    if ( parent.exists() == false )
                        parent.mkdirs();

                    // use a buffered copy
                    
                    InputStream in = null;
                    OutputStream out = null; 
                    try {
                        InputStream inFile = new FileInputStream(from_file);
                        in = new BufferedInputStream(inFile);
                        OutputStream outFile = new FileOutputStream(to_file);
                        out = new BufferedOutputStream(outFile);
                        int i = 0;
                        while( (i=in.read(buffer) )!=-1 )
                        {
                            out.write(buffer, 0, i);
                        }
                    } finally {
                        if (in != null) {
                            in.close();
                        }
                        if (out != null) {
                            out.close();
                        }
                    }
                    
                    /*
                    FileInputStream fin  = new FileInputStream(from_file);
                    FileOutputStream fout = new FileOutputStream(to_file);
                    // copy file
                    byte[] buffer = new byte[8192];
                    int i = 0;
                    while( (i=fin.read(buffer) )!=-1 )
                    {
                        fout.write(buffer, 0, i);
                    }
                    fin.close();
                    fout.close();
                    */

                }
                catch (IOException e) {
                    System.out.println("Error: " + e.getMessage());
                    throw e;
                }
                return null;

            }
        });
        }  catch (PrivilegedActionException e) {
            throw new IOException(e.getException().getMessage());
        }


    }

    public void copytree(final String src_path_str, final String dst_path_str) throws IOException
    {
        final File src_path = new File(src_path_str);
        final File dst_path = new File(dst_path_str);
        try {
        AccessController.doPrivileged( new PrivilegedExceptionAction() {
            public Object run() throws IOException{
                
                if (src_path.isDirectory()) {
                    if (!dst_path.exists()) {
                        dst_path.mkdir();
                    }

                    String[] children = src_path.list();
                    
                    for (int i=0; i<children.length; i++) {
                        String child = children[i];
                        copytree(
                            new File(src_path_str, child).getAbsolutePath(),
                            new File(dst_path_str, child).getAbsolutePath()
                        );
                    }
                }
                else {
                        copy_file(src_path_str, dst_path_str);

                }
                
                return null;
            }
        });
        } catch (PrivilegedActionException e) {
            throw new IOException(e.getException().getMessage());
        }
    }


    public void rmtree(final String path_str)
    {
        final File path = new File(path_str);
        AccessController.doPrivileged( new PrivilegedAction() {
            public Object run() {
                if (path.isDirectory()) {
                    
                    String[] children = path.list();
                    for (int i=0; i<children.length; i++) {
                        String child = children[i];
                        rmtree( new File(path_str, child).getAbsolutePath());
                    }
                    remove_file(path_str);


                }
                else {
                    remove_file(path_str);
                }
                return null;
            }
        });
    }




   
    /* move a file */
    public void move_file(String from_path, String to_path)
    {
        final String f_path = from_path;
        final String t_path = to_path;
        AccessController.doPrivileged( new PrivilegedAction() {
            public Object run() {
                try {
                    File from_file = new File(f_path);
                    File to_file = new File(t_path);
                    boolean success = from_file.renameTo(to_file);
                    // Does not work on cross file system
                    if (!success) {
                        copytree(f_path, t_path);
                        rmtree(f_path);
                    }
                        


                }
                catch (Exception e) {
                    System.out.println(e.getMessage());
                }
                return null;

            }
        });

    }
 

    /* Open an explorer in windows or finder in mac*/
    public void open_folder(String path)
    {
        if (GeneralApplet.is_windows())
            this.exec_shell("explorer file://" + path, false );
        else // assuming Mac OS X
            this.exec("/usr/bin/open " + path, false);
    }
    
    /**
     * Try to determine whether this application is running under Windows
     * or some other platform by examing the "os.name" property.
     *
     * @return true if this application is running under a Windows OS
     */
    // Used to identify the windows platform.
    private static final String WIN_ID = "Windows";
    
    public static boolean is_windows()
    {
        String os = System.getProperty("os.name");
        if ( os != null && os.startsWith(WIN_ID))
            return true;
        else
            return false;
    }


    /* issue a command over a socket port */
    public String[] command_port(String url, int port, String cmd)
    {
        final String f_cmd = cmd;
        final int f_port = port;
        final String f_url = url;

        final String[] f_ret_value = new String[2];

        AccessController.doPrivileged( new PrivilegedAction() {
            public Object run() {
                try {
                    CommandPort cmd_port = new CommandPort();
                    boolean is_connected = cmd_port.connect(f_url, f_port);
                    String ret_val = cmd_port.do_cmd(f_cmd);
                    f_ret_value[0] = ret_val;
                    cmd_port.close();
                    if (cmd_port.get_exception() != "")
                        my_connect_error = cmd_port.get_exception();
                    f_ret_value[1] = my_connect_error;
                }
                catch (Exception e) {
                    System.out.println(e.getMessage());
                }
                return null;

            }
        });

        return f_ret_value;
    }
    
    /* get connect error for the Command Port */
    public String get_connect_error()
    {
        return my_connect_error;
    }


     /* open a file browser */
    @SuppressWarnings("unchecked")
    public String[] open_file_browser(final String cur_dir_str)
    {
       
        final File[][] f_files = new File[1][];
        try {
        SwingUtilities.invokeAndWait(new Runnable() {
        @Override
        public void run() {
        
            AccessController.doPrivileged( new PrivilegedAction() {
            public Object run() {
                try {

                    JFrame.setDefaultLookAndFeelDecorated( true );
                    UIManager.setLookAndFeel(
                        UIManager.getSystemLookAndFeelClassName());
                    Container content_pane = getContentPane();


                    // instantiate the file browser
                    final JFileChooser file_chooser = new JFileChooser();
                    file_chooser.setFileSelectionMode(JFileChooser.FILES_AND_DIRECTORIES);
                    file_chooser.setMultiSelectionEnabled(true);
                    file_chooser.setDialogTitle("Select Files");

                    if (cur_dir_str != null) {
                        final File cur_dir = new File(cur_dir_str);
                        file_chooser.setCurrentDirectory(cur_dir);
                    }


                    file_chooser.showOpenDialog(content_pane);
                    f_files[0] = file_chooser.getSelectedFiles();
                }
                catch (Exception e) {
                    System.out.println(e.getMessage());
                }
                return null;

            }
        });

        }
    });
    } catch (Exception e1) {
      e1.printStackTrace();
    }
        

        final String[] f_ret_value = new String[f_files[0].length];
        for (int i=0; i < f_files[0].length; i++) {
            String path = f_files[0][i].getAbsolutePath();
            System.out.println(path);
            f_ret_value[i] = path;
        }
        return f_ret_value;
    }



    public String getenv(final String name)
    {
        final String value = (String) AccessController.doPrivileged( new PrivilegedAction()
        {
            public Object run() {
                String value = "";
                try {
                    value = System.getenv(name);
                    if (value == null) {
                        value = "";
                    }
                }
                catch (Exception e) {
                    System.out.println(e.getMessage());
                }
                return value;

            }
        });

        return value;
    }


    public String getenvp(final String name)
    {
        return (String) my_envp.get(name);
    }


    public void setenvp(final String name, final String value)
    {
        my_envp.put((String) name, (String) value);
    }


    // Read infile that is in base 64 notation and create the outfile of it decoded.
    //
    // @param:
    //  infile  - path to the input file that has been encoded in base 64 notation
    //  outfile - path to where the output file will be created, decoded
    //
    // @return:
    //  none
    //
    // @examples:
    //
    //  Decode the infile named "encoded.txt" from base 64 notation to "decoded.jpg":
    //
    //      var applet = spt.Applet.get();
    //      applet.decodeFileToFile("C:/temp/encoded.txt", "C:/temp/decoded.jpg");
    //
    public void decodeFileToFile(final String infile, final String outfile)
    {
        AccessController.doPrivileged( new PrivilegedAction() {
            public Object run() {
                try {
                    Base64.decodeFileToFile(infile, outfile);
                }
                catch (Exception e) {
                    System.out.println("Error: " + e.getMessage());
                }
                return null;
            }
        });
    }


    // Read the input string and return the string decoded from base 64 notation.
    //
    // @param:
    //  input_str  - the input string to be decoded
    //
    // @return:
    //  the decoded string
    //
    // @examples:
    //
    //  Decode the input string from base 64 notation:
    //
    //      var applet = spt.Applet.get();
    //      var my_decoded_str = applet.decodeString(my_encoded_str);
    //
    public String decodeString(final String input_str)
    {
        final String in_str = input_str;

        final String ret_val = (String) AccessController.doPrivileged( new PrivilegedAction() {
            String decoded_str = "";
            public Object run() {
                try {
                    byte[] decoded_byte_array = Base64.decode( in_str );
                    decoded_str = new String(decoded_byte_array);
                }
                catch (Exception e) {
                    System.out.println("Error: " + e.getMessage());
                }
                return decoded_str;
            }
        });
        return ret_val;
    }


    // Read infile and create the outfile of it encoded in base 64 notation.
    //
    // @param:
    //  infile  - path to the input file that we wish to be encoded
    //  outfile - path to where the output file will be created, encoded
    //
    // @return:
    //  none
    //
    // @examples:
    //
    //  Encode the infile named "original.jpg" to base 64 notation to "output.txt":
    //
    //      var applet = spt.Applet.get();
    //      applet.encodeFileToFile("C:/temp/original.jpg", "C:/temp/encoded.txt");
    //
    public void encodeFileToFile(final String infile, final String outfile)
    {
        AccessController.doPrivileged( new PrivilegedAction() {
            public Object run() {
                try {
                    Base64.encodeFileToFile(infile, outfile);
                }
                catch (Exception e) {
                    System.out.println("Error: " + e.getMessage());
                }
                return null;
            }
        });
    }


    // Read the input string and return the string encoded in base64 notation.
    //
    // @param:
    //  input_str  - the input string to be encoded
    //
    // @return:
    //  the encoded string
    //
    // @examples:
    //
    //  Encode the input string from "Hello World!" to base 64 notation:
    //
    //      var applet = spt.Applet.get();
    //      var my_encoded_str = applet.encodeString("Hello World!");
    //
    public String encodeString(final String input_str)
    {
        final String in_str = input_str;

        final String ret_val = (String) AccessController.doPrivileged( new PrivilegedAction() {
            String encoded_str = "";
            public Object run() {
                try {
                    encoded_str = Base64.encodeBytes( in_str.getBytes() );
                }
                catch (Exception e) {
                    System.out.println("Error: " + e.getMessage());
                }
                return encoded_str;
            }
        });
        return ret_val;
    }   




    // opens a file with it's associated application
    //
    public void open_file(final String path)
    {
        final String ret_val = (String) AccessController.doPrivileged( new PrivilegedAction() {

            public Object run() {
                try {
                    Desktop desktop = null;
                    if (Desktop.isDesktopSupported()) {
                        desktop = Desktop.getDesktop();
                    }
                    File file = new File(path);
                    desktop.open(file);
                }
                catch(Exception e) {
                    e.printStackTrace();
                }
                return "";
            }

        } );

    }


    // open a url in the browser of choice
    public void open_url(final String url)
    {
        final String ret_val = (String) AccessController.doPrivileged( new PrivilegedAction() {

            public Object run() {
                try {
                    Desktop desktop = null;
                    if (Desktop.isDesktopSupported()) {
                        desktop = Desktop.getDesktop();
                    }
                    URI uri = new URI(url);
                    desktop.browse(uri);
                }
                catch(Exception e) {
                    e.printStackTrace();
                }
                return "";
            }

        } );

    }



    // unzip a file
    //
    public void unzip_file(final String path, final String to_dir)
    {
        final String ret_val = (String) AccessController.doPrivileged( new PrivilegedAction() {

            final int BUFFER = 2048;

            public Object run() {
                try {
                    BufferedOutputStream dest = null;
                    FileInputStream fis = new FileInputStream(path);
                    ZipInputStream zis = new ZipInputStream(new BufferedInputStream(fis));
                    ZipEntry entry;
                    while((entry = zis.getNextEntry()) != null) {
                        int count;
                        byte data[] = new byte[BUFFER];
                        // write the files to the disk
                        String filename = entry.getName();
                        String to_path = to_dir + "/" + filename;
                        File to_file = new File(to_path);
                        File parent_dir = to_file.getParentFile();
                        if (!parent_dir.exists()) {
                            String parent_path = parent_dir.getAbsolutePath();
                            String parent_path2 = parent_path.replace("\\","/");
                            makedirs(parent_path2);
                        }

                        if (to_path.endsWith("/")) {
                            makedirs(to_path);
                        }
                        else {
                            //System.out.println("Extracting: " + to_path );
                            FileOutputStream fos = new FileOutputStream(to_path);
                            dest = new BufferedOutputStream(fos, BUFFER);
                            while ((count = zis.read(data, 0, BUFFER)) != -1) {
                               dest.write(data, 0, count);
                            }
                            dest.flush();
                            dest.close();
                        }
                    }
                    zis.close();
                } catch(Exception e) {
                    e.printStackTrace();
                }
                return "";
            }

        } );

    }


}
