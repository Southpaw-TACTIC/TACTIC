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

import java.net.*;
import java.io.*;

class CommandPort
{
    public Socket my_socket;
    public PrintWriter my_out;
    public BufferedReader my_in;
    public String my_connect_exception = "";

    public boolean connect(String server, int port) {
        try {
            my_socket = new Socket(server, port);
            my_out = new PrintWriter(my_socket.getOutputStream(), 
                     true);
            my_in = new BufferedReader(new InputStreamReader(
                    my_socket.getInputStream()));

        } catch (UnknownHostException e) {
            System.out.println("Unknown host: " + server);
            return false;
        } catch  (IOException e) {
            String msg = "Cannot connect to port: " + server + ":" + port  + ".";
            System.out.println(msg);
            my_connect_exception = msg;
            return false;
        }

        return true;
    }

    public String do_cmd(String cmd) {
        String ret_val = "";
        StringBuffer rtn = new StringBuffer();
        
        try {
            if (my_out == null)
            {
                return ret_val;
            }
            my_out.println(cmd);
            //System.out.println("CMD: " + cmd);
            my_in.mark(1);
            int read = my_in.read();
            my_in.reset();
            
            while (read != 0 && ret_val != null) {
                
                if (!ret_val.equals("")) {
                    rtn.append("\n");
                }
                
                ret_val = my_in.readLine();
                rtn.append(ret_val);
                
                if (ret_val == null){
                    break;
                }
                my_in.mark(1);
                read = my_in.read();
                my_in.reset();
            }

        } catch  (IOException e) {
            System.out.println("Can't read");
        }
        return rtn.toString();
    }


    public void close() {
       try {
         if (my_socket == null)
             return;
         my_socket.close();
       } catch  (IOException e) {
         System.out.println("Can't close");
       }

    }

    public String get_exception() {
        return my_connect_exception;
    }

    public static void main(String[] args) {
        System.out.println("Command Port starting");
        // for Maya
        CommandPort tt = new CommandPort();
        tt.connect("localhost", 4444);
        tt.do_cmd("torus");
        
        
        tt = new CommandPort();
        tt.connect("localhost", 13005);
        

        String rtn = tt.do_cmd("echo $PATH");
        System.out.println("Rtn 1 " + rtn);
        
        tt = new CommandPort();
        tt.connect("localhost", 13005);
        
        rtn = tt.do_cmd("opcf obj; opadd -n null hello");
        System.out.println("Rtn 2 " + rtn);

        tt = new CommandPort();
        tt.connect("localhost", 13005);
        // Running 'set' freezes
        if (args.length == 1 && args[0].equals("3")) {
        rtn = tt.do_cmd("set -g ticket='adg'; echo $ticket");
        //rtn = tt.do_cmd("echo $ticket");
        System.out.println("Rtn 3 " + rtn);
        }

        tt = new CommandPort();
        tt.connect("localhost", 13005);
        // setting the path /obj will freeze also
        if (args.length == 1 && args[0].equals("4")) {
        rtn = tt.do_cmd("opcomment /obj/hello");
        System.out.println("Rtn 4 " + rtn);
        }
        tt.close();
        System.out.println("Command Port finished");

    }

}



