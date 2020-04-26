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
import java.util.*;
import java.net.*;
import javax.net.ssl.*;
import java.lang.*;
import java.nio.channels.*;

public class Upload
{
    public static final int my_chunk_size = 25*1024*1024;
    public static final int my_buffer_size = 524288;

    URL my_to_url;
    String my_from_path;
    String my_to_filename;
    String my_ticket;
    String my_subdir;

    BufferedInputStream my_file_in;
    byte[] my_buffer = new byte[my_buffer_size];
    int my_total_read = 0;


    public Upload( URL url, String from_path )
    {
        my_to_url = url;
        my_from_path = from_path;
        my_subdir = null;

    }

    public void set_ticket(String ticket_id)
    {
        my_ticket = ticket_id;
    }    


    public void set_subdir(String subdir)
    {
        my_subdir = subdir;
    }


    public String get_to_filename()
    {
        return my_to_filename;
    }


    public String get_from_path()
    {
        return my_from_path;
    }
   
   

    public void do_copy() throws IOException
    {
        // get the file stream
        File in = new File(my_from_path);
       
        File out = new File(my_to_url.getFile());
        File parent = out.getParentFile();
        if ( parent != null && !parent.exists() )
             parent.mkdirs();

        FileChannel sourceChannel = new
             FileInputStream(in).getChannel();
        FileChannel destinationChannel = new
             FileOutputStream(out).getChannel();
        sourceChannel.transferTo(0, sourceChannel.size(), destinationChannel);
        // or
        //  destinationChannel.transferFrom(sourceChannel, 0, sourceChannel.size());
        my_to_filename = out.getName();
        sourceChannel.close();
        destinationChannel.close();
        System.out.println("copied: " + my_to_filename);
        
    }

    

    public void do_upload()
        throws IOException
    {
      
        // get the file stream
        File file = new File(my_from_path);
        FileInputStream fin = new FileInputStream(file);
        my_file_in = new BufferedInputStream( fin );

        long file_size = file.length();

        System.out.println("Uploading: " + my_from_path);

        String action = null;
        while ( true )
        {
            // determine if this is going to be the last chunk
            boolean last_chunk = false;
            if ( my_total_read >= (file_size-my_chunk_size) )
            {
                
                //System.out.println("total_read: " + my_total_read );
                //System.out.println("file_size: " + file_size );
                //System.out.println("Last Chunk!!!");
                

                last_chunk = true;

                // if this is the first chunk, then create and analyze
                // otherwise append and analyze
                if (my_total_read == 0)
                    action = "create";
                else
                    action = "append";
            }
            else
            {
                // determine the action
                if ( my_total_read == 0 )
                    action = "create";
                else if ( my_total_read >= 0 )
                    action = "append";
            }

            int read = upload_chunk(action);
            if ( read < my_chunk_size )
                break;

        }
        System.out.println("Upload finished.");
        my_file_in.close();
    
    }
    


    String BOUNDARY = "----------ThIs_Is_tHe_bouNdaRY_---$---";


    private int upload_chunk( String action )
        throws IOException
    {
        HttpURLConnection conn = (HttpURLConnection) my_to_url.openConnection();
        try
        {
            String agent = "Tactic Client";
            String type = "multipart/form-data; charset=utf-8; boundary=" + BOUNDARY;
            //String type = "application/x-www-form-urlencoded";

            conn.setRequestMethod( "POST" );
            conn.setRequestProperty( "User-Agent", agent );
            conn.setRequestProperty( "Content-Type", type );
            //conn.setRequestProperty( "Connection", "close" );
            //conn.setRequestProperty( "Content-Length", encodedData.length() );
          

            conn.setDoOutput(true);
            conn.setDoInput(true);
            conn.setUseCaches(true);
            //System.setProperty("http.keepAlive", "false");

        }
        catch (IllegalStateException e)
        {
            System.out.println("This is a strange exception that shouldn't "
                    + "happen");
            e.printStackTrace();
            throw e;
        }
        catch (IOException e)
        {
            e.printStackTrace();
            throw e;
        }
        conn.connect();
        // handle the output stream
        OutputStream cout = conn.getOutputStream();
       
        int chunk_read = 0;
        try 
        {
            chunk_read = handle_output(cout, action);
        }
        finally
        {
            cout.close();
        }
        // get response
        // about 2Mb a second when tested locally
        InputStream in_stream = conn.getInputStream();
        BufferedReader rin = new BufferedReader(
            new InputStreamReader( in_stream )
        );

        String ret_val = "";
     
        while ( (ret_val = rin.readLine()) != null )
        {
            if ( ret_val.startsWith("upload=") )
            {
                int idx = ret_val.indexOf("=");
                String from_path = ret_val.substring(idx+1);
                Upload sub_upload = new Upload(my_to_url, from_path);
                sub_upload.do_upload();

            }
            else if ( ret_val.startsWith("file_name=") )
            {
                int idx = ret_val.indexOf("=");
                my_to_filename = ret_val.substring(idx+1);
            }
        }

        rin.close();
        conn.disconnect();
        //cout.close();
        return chunk_read;


    }


    int handle_output_old(OutputStream cout, String action) throws IOException
    {
        PrintWriter pout = new PrintWriter(cout);


        pout.println("action="+action);
        pout.println("file="+my_from_path);
        pout.println("ticket="+my_ticket);
        pout.println("EOF");
        pout.flush();


        int chunk_read = 0;
        int read;
        while ( (read = my_file_in.read(my_buffer)) != -1 )
        {
            cout.write(my_buffer, 0, read);
            cout.flush();

            chunk_read += read;
            my_total_read += read;

            if ( chunk_read >= my_chunk_size )
                break;
        }

        return chunk_read;

    }


    String CRLF = "\r\n";
    void ln(PrintWriter pout, String str)
    {
        pout.write(str + CRLF);
    }

    public String escape_unicode(String input) {
        StringBuilder retStr = new StringBuilder();
        for (int i=0; i<input.length(); i++) {
            int cp = Character.codePointAt(input, i);
            int charCount = Character.charCount(cp);
            if (charCount > 1) {
                i += charCount - 1; // 2.
                if (i >= input.length()) {
                throw new IllegalArgumentException("Incomplete file name encountered.");
                }
            }

            if (cp < 128) {
                retStr.appendCodePoint(cp);
            } else {
                retStr.append(String.format("\\u%x", cp));
            }
          }
        return retStr.toString();
      
    }
    

    int handle_output(OutputStream cout, String action) throws IOException
    {
        PrintWriter pout = new PrintWriter(cout);

        HashMap map = new HashMap();
        map.put("ajax", "true");
        map.put("action", action);
        map.put("ticket", my_ticket);
        map.put("login_ticket", my_ticket);
        if (my_subdir != null) {
            map.put("subdir", my_subdir);
        }

        Set keys = map.keySet();
        for (Iterator i = keys.iterator(); i.hasNext(); )
        {
            String key = (String) i.next();
            String value = (String) map.get(key);

            pout.write("--" + BOUNDARY + CRLF);
            pout.write("Content-Disposition: form-data; name=\""+key+"\"" + CRLF);
            pout.write( CRLF );
            pout.write(value + CRLF);
        }

        // support only on file (or part of a file)
        //for (key, filename, value) in files:
        String key = "file";
        pout.write("--" + BOUNDARY + CRLF);
        my_from_path = escape_unicode(my_from_path);
        

        pout.write("Content-Disposition: form-data; name=\""+key+"\"; filename=\""+my_from_path+"\"" +CRLF);
        pout.write(CRLF);
        pout.flush();

        // add the fbuffer
        int chunk_read = 0;
        int read;
        while ( (read = my_file_in.read(my_buffer)) != -1 )
        {
            cout.write(my_buffer, 0, read);

            chunk_read += read;
            my_total_read += read;

            if ( chunk_read >= my_chunk_size )
                break;
        }
        cout.flush();

        pout.write(CRLF);
        pout.write("--" + BOUNDARY + "--" + CRLF);
        pout.write(CRLF);
        pout.flush();
        
        if (pout != null) pout.close();


        return chunk_read;
    }

 


}



