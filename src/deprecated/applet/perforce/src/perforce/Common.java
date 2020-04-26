/* *********************************************
 *
 * Copyright (c) 2005, Southpaw Technology
 *                     All Rights Reserved
 *
 * PROPRIETARY INFORMATION.  This software is proprietary to
 * Southpaw Technology, and is not to be reproduced, transmitted,
 * or disclosed in any way without written permission.
 *
 *
 *
 */


package perforce;

import java.io.*;
import java.util.*;
import java.lang.*;


/* class that abstracts out perforce commands */
public class Common
{
    public static String[] execute(String cmd, String input)
    {
        System.out.println( "--> " + cmd );

        ArrayList output = new ArrayList();

        Runtime runtime = Runtime.getRuntime();
        try {
            Process process = runtime.exec(cmd);
            if (input != null)
            {
                OutputStream os = process.getOutputStream();
                OutputStreamWriter osr = new OutputStreamWriter(os);
                BufferedWriter bw = new BufferedWriter(osr);
                bw.write(input);
                bw.close();
            }
            InputStream is = process.getInputStream();
            InputStreamReader isr = new InputStreamReader(is);
            BufferedReader br = new BufferedReader(isr);

            String line;
            while (  (line = br.readLine() ) != null ) {
                output.add(line);
            }
            
        } catch (Exception ex) {
            System.out.println(ex);
        }

        String output_array[] = new String[output.size()];
        output.toArray(output_array);
        return output_array;
    }        



    public static byte[] execute2(String cmd, String input)
    {
        System.out.println( "--> " + cmd );

        ArrayList output = new ArrayList();

        Runtime runtime = Runtime.getRuntime();
        try {
            Process process = runtime.exec(cmd);
            if (input != null)
            {
                OutputStream os = process.getOutputStream();
                OutputStreamWriter osr = new OutputStreamWriter(os);
                BufferedWriter bw = new BufferedWriter(osr);
                bw.write(input);
                bw.close();
            }
            InputStream is = process.getInputStream();
            DataInputStream ds = new DataInputStream(is);

            byte[] buf = new byte[1];
            while ( ds.read(buf,0,1) > -1 ) {
                output.add( new Byte(buf[0]) );
            }
            
        } catch (Exception ex) {
            System.out.println(ex);
        }

        byte[] output_array = new byte[output.size()];
        for ( int i = 0; i < output.size(); i++) {
            Byte bt = (Byte) output.get(i);
            output_array[i] = bt.byteValue();
        }

        return output_array;
    }        




    public static String hexify(byte[] data) {
        StringBuffer sb = new StringBuffer();
        for (int i = 0; i < data.length; i++) {
            int integer = ((int) data[i]) & 0xFF;
            String hex = Integer.toHexString(integer);
            // make sure there are 2 digits
            if (integer < 16) {
                hex = "0"+hex;
            }
            sb.append(hex);
        }
        return sb.toString();
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

}



