/* *********************************************************
 *
 * Copyright (c) 2005, Southpaw Technology
 *                     All Rights Reserved
 * 
 * PROPRIETARY INFORMATION.  This software is proprietary to
 * Southpaw Technology, and is not to be reproduced, transmitted,
 * or disclosed in any way without written permission.
 * 
 */ 


package upload;

import java.io.*;
import java.lang.*;

public class DownloadThread extends Thread 
{
     public boolean my_skip_if_exists = false;
     public String my_url_path = "";
     public String my_to_path = "";
     public Download my_download = null;
     public int my_file_size = 0;
     private static int EXCEPTION_CODE = -10;
     
     public DownloadThread(boolean skip_if_exists, String url_path, String to_path) 
     {
         my_skip_if_exists = skip_if_exists; 
         my_url_path = url_path;
         my_to_path = to_path;
     }

     public String get_error_message()
     {
         String msg = "";
         if (my_download != null)
             msg = my_download.get_exception();
         return msg;
     }
     
     public int get_completion()
     {
         // if download in null, then it hasn't started yet
         if (my_download == null)
            return 0;

         if (!this.get_error_message().equals(""))
             return EXCEPTION_CODE;

        
         if (my_download.get_finished_status())
             return 100;

         // wait a few seconds if the file size cannot be determined yet
         int x = 0;
         if (my_file_size <= 0)
             my_file_size = this.get_file_size(my_url_path); 
         
         int completion = 0;
         try
         {
             
             while (x < 3 && my_file_size <= 0)       
             {     
                x = x + 1; 
                System.out.println("Finding file size (Trial #" + x); 
                Thread.sleep(1000); 
                my_file_size = this.get_file_size(my_url_path); 
                
             }
             if (my_file_size > 0)
             {
                completion = (int) ((float) my_download.get_read_total()
                         / (float) my_file_size * 100);
             }
         }   
         catch (Exception e)
         {
             System.out.println("Error getting the file size");
             completion = -1;
         }
         return completion;
     }

     public int get_file_size(String url_path)
     {
         if (my_download == null)
         {
             System.out.println("download not initialized yet!");
             return 0;
         }

         return my_download.get_file_size(url_path);
     }
     
     public void run() 
     {
         my_download = new Download(my_skip_if_exists); 
         my_download.do_download(my_url_path, my_to_path);
     }
}






