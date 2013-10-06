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
import java.net.*;
import javax.net.ssl.*;
import java.lang.*;



public class Download
{
    boolean my_skip_if_exists = false;
    public int my_read_total = 0;
    public int my_file_size = 0;
    public String my_download_exception = "";
    public static final int my_buffer_size = 524288;
    public boolean my_download_finished = false;
    
    public Download()
    {
    }
    
    public Download(boolean skip_if_exists)
    {
        my_skip_if_exists = skip_if_exists;
    }   

    public int get_file_size(String url_path)
    {
        if (my_file_size > 0)
            return my_file_size;
    
        try
        {
            URL url = new URL(url_path);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            // only interested in the length of the resource
            conn.setRequestMethod("HEAD");
            my_file_size = conn.getContentLength();
           
            //System.out.println("File size of " + url_path +  "\n [" + my_file_size + "]"); 
            
            conn.disconnect();
        }
        catch (Exception e)
        {
            e.printStackTrace();
            System.out.println(e);
        }
        return my_file_size;
    }

    public int get_read_total()
    {
        return my_read_total;
    }

    public String get_exception()
    {
        return my_download_exception;
    } 
    
    public boolean get_finished_status()
    {
        return my_download_finished;
    }
        
    public int do_download( String url_path, String to_path )
    {
        int total_read = 0;

        try
        {
            // make sure the to_path exists by creating the dirs
            File file = new File(to_path);
            if (my_skip_if_exists && file.exists())
            {
                my_download_finished = true;
                return total_read;
            }
            
            File parent = file.getParentFile();
            if ( parent != null && !parent.exists() )
                parent.mkdirs();

            URL url = new URL(url_path);
            /*
            String decodedURL = URLDecoder.decode(url_path, "UTF-8");
            URL url = new URL(decodedURL);
            URI uri = new URI(url.getProtocol(), url.getUserInfo(), url.getHost(), url.getPort(), url.getPath(), url.getQuery(), url.getRef()); 
            url = uri.toURL(); 
            */
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
           
            BufferedInputStream in =
                new BufferedInputStream(conn.getInputStream());
            
            FileOutputStream fout = new FileOutputStream(to_path);
            BufferedOutputStream out =
                new BufferedOutputStream( fout );


            byte[] buffer = new byte[my_buffer_size];
            int read;
            int counter = 0;
            while ( (read = in.read(buffer)) != -1 )
            {
                counter++;
                out.write(buffer, 0, read);
                total_read += read;
                my_read_total = total_read;
                if (counter % 50 == 0)
                    System.out.println("buffer total read so far: " + my_read_total );
            }
            
            out.close();
            conn.disconnect();
            my_download_finished = true;
        }
        
        catch (Exception e)
        {
            e.printStackTrace();
            System.out.println(e);
            my_download_exception = e.toString();
        }
        
        return total_read;

    }





    public static void main( String args[] )
    {
        String url = "http://remkon.dyndns.org/pictures/rm1.jpg";
        String to_path = "tt.jpg";

        Download download = new Download();
        int read = download.do_download( url, to_path );
        System.out.println( "read: "+read);

        
    }


}



