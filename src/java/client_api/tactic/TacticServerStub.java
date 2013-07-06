// -----------------------------------------------------------------------------
//
//  Copyright (c) 2012, Southpaw Technology Inc., All Rights Reserved
//
//  PROPRIETARY INFORMATION.  This software is proprietary to
//  Southpaw Technology Inc., and is not to be reproduced, transmitted,
//  or disclosed in any way without written permission.
//
// -----------------------------------------------------------------------------
//
//

package tactic;

import java.util.*;
import java.io.*;

import java.util.logging.Level;
import java.util.logging.Logger;

import jep.Jep;
import jep.JepException;

import org.codehaus.jackson.map.ObjectMapper;

class TacticException extends Exception {
}
 
 
public class TacticServerStub {
    private Map<Long,Jep> jep_instances = new HashMap<Long,Jep>();
    private ObjectMapper mapper;
    private String protocol;

    public TacticServerStub(String project_code) {
        //init();
        set_project(project_code);
    }

    public TacticServerStub() {
        //init();
    }


    private Jep get_jep() {
        Thread thread = Thread.currentThread();
        Long thread_id = (Long) thread.getId();

        Jep jep = (Jep) jep_instances.get(thread_id);
        if (jep == null) {
            try {
                jep = new Jep();
                init(jep);
                jep_instances.put(thread_id, jep);

            } catch (JepException ex) {
                Logger.getLogger(TacticServerStub.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
        return jep;
    }


    private void init(Jep jep) {
        try {

            // load dependent dlls
            /*
            File dll;
            dll = new File("dll/jep.dll");
            System.out.println(dll.getAbsolutePath());
            System.load(dll.getAbsolutePath());
            dll = new File("dll/msvcr71.dll");
            System.out.println(dll.getAbsolutePath());
            System.load(dll.getAbsolutePath());
            */


            //protocol = "xmlrpc";
            protocol = "local";
            jep.set("protocol", protocol);
            // put in some dummy values
            jep.set("function", "foo");
            jep.set("kwargs", "{}");


            // read ini initializer
            InputStream is = getClass().getResourceAsStream("/tactic/jep_init.py");
            byte[] bytes = new byte[is.available()];
            is.read(bytes);
            String content = new String(bytes);
            // create a temp file because jep does not seem to read
            // in a multi-line string properly
            //jep.eval(content);
            File tmp_file = File.createTempFile("tactic","jep_init.py");
            tmp_file.deleteOnExit();
            FileWriter os = new FileWriter(tmp_file);
            os.write(content);
            os.close();
            String path = tmp_file.getAbsolutePath();
            jep.runScript(path);

        } catch (JepException ex) {
            Logger.getLogger(TacticServerStub.class.getName()).log(Level.SEVERE, null, ex);
        } catch (IOException ex) {
            Logger.getLogger(TacticServerStub.class.getName()).log(Level.SEVERE, null, ex);
        }

        mapper = new ObjectMapper();
    }


    public Long get_thread_id() {
        Thread thread = Thread.currentThread();
        Long thread_id = (Long) thread.getId();
        return thread_id;
    }


    private String execute(String function, Map kwargs) {
        Jep jep = get_jep();

        try {
            jep.set("function", function);


            // convert kwargs to a json string
            if (kwargs == null) {
                jep.set("kwargs", "{}");
            }
            else {
                Writer kwargs_writer = new StringWriter();
                mapper.writeValue(kwargs_writer, kwargs);
                String kwargs_json = kwargs_writer.toString();
                jep.set("kwargs", kwargs_json);
            }

            // execute the python script



            //jep.runScript("./delegator.py");
            jep.eval("delegate()");


            String ret_val = (String) jep.getValue("ret_val");
            return ret_val;
        } catch (jep.JepException e) {
            System.out.println("Error getting value from Jep");
            System.out.println(e);
        } catch (IOException e) {
            System.out.println("Error getting value from Jep");
            System.out.println(e);
        }
        return null;
    }


    private String get_string_return(String ret_val) {
        if (ret_val == null) {
            ret_val = "";
        }
        else {
            try {
                ret_val = mapper.readValue(ret_val, String.class);
            } catch( IOException e) {
                System.out.println(e);
            }
        }
        return ret_val;
    }


    private ArrayList get_array_return(String ret_str) {
        try {
            ArrayList<Map> ret_val = mapper.readValue(ret_str, ArrayList.class);
            return ret_val;

        } catch (IOException e) {

            System.out.println("Error:");
            System.out.println(e);
            return new ArrayList();
        }
    }


    private Map get_map_return(String ret_str) {
        try {
            Map<String,Object> ret_val = mapper.readValue(ret_str, HashMap.class);
            return ret_val;
        } catch (IOException e) {
            System.out.println("Error:");
            System.out.println(e);
            return new HashMap();
        }
    }


    //
    // Misc functions
    //
    public void set_project(String project_code) {
        if (protocol == "local") {
            try {
                Jep jep = get_jep();
                jep.eval("from pyasm.biz import Project");
                jep.eval("Project.set_project(\""+project_code+"\")");

            } catch (JepException ex) {
                Logger.getLogger(TacticServerStub.class.getName()).log(Level.SEVERE, null, ex);
            }

        }

        Map kwargs = new HashMap<String,Object>();
        kwargs.put("project_code", project_code);
        execute("set_project", kwargs);
    }



    //
    // Version methods
    //

    public String get_server_version() {
        String ret_val = execute("get_server_version", null);
        return get_string_return(ret_val);
    }


    public String get_server_api_version() {
        String ret_val = execute("get_server_api_version", null);
        return get_string_return(ret_val);
    }



    //
    // Simple Ping Test
    //
    public String ping(Map ticket, Map foofoo) {
        String ret_val = execute("ping", null);
        return get_string_return(ret_val);
    }

 
    public String ping() {
        String ret_val = execute("ping", null);
        return get_string_return(ret_val);
    }

    public Map test_database_connection() {
        String ret_val = execute("test_database_connection", null);
        return get_map_return(ret_val);
    }


    public Map get_connection_info() {
        String ret_val = execute("get_connection_info", null);
        return get_map_return(ret_val);
    }


    /*
     * Logging methods
     */
    public String log() {
        String ret_val = execute("log", null);
        return ret_val;
    }





    /*
     * Transaction Methods
     */
    public String start() {
        Map kwargs = new HashMap<String,Object>();
        return start(kwargs);
    }
    public String start(Map kwargs) {
        String ret_val = execute("start", kwargs);
        return ret_val;
    }

   
    public String finish() {
        Map kwargs = new HashMap<String,Object>();
        return finish(kwargs);
    }
    public String finish(Map kwargs) {
        String ret_val = execute("finish", kwargs);
        return ret_val;
    }

 
    public String abort() {
        Map kwargs = new HashMap<String,Object>();
        String ret_val = execute("abort", kwargs);
        return ret_val;
    }


    public String undo() {
        Map kwargs = new HashMap<String,Object>();
        return undo(kwargs);
    }
    public String undo(Map kwargs) {
        String ret_val = execute("undo", kwargs);
        return ret_val;
    }



    public String redo() {
        Map kwargs = new HashMap<String,Object>();
        return redo(kwargs);
    }
    public String redo(Map kwargs) {
        String ret_val = execute("redo", kwargs);
        return ret_val;
    }




    //
    // Database methods
    //
    public ArrayList query(String search_type) {
        Map kwargs = new HashMap<String,Object>();
        return query(search_type, kwargs);
    }

    public ArrayList query(String search_type, Map kwargs) {
        kwargs.put("search_type", search_type);
        String ret_str = execute("query", kwargs);
        return get_array_return(ret_str);
    }




    public Map insert(String search_key, Map data) {
        Map kwargs = new HashMap<String,Object>();
        return insert(search_key, data, kwargs);
    }

    public Map insert(Map sobject, Map data) {
        Map kwargs = new HashMap<String,Object>();
        return insert(sobject, data, kwargs);
    }

    public Map insert(Map sobject, Map data, Map kwargs) {
        String search_key = (String) sobject.get("__search_key__");
        return insert(search_key, data, kwargs);
    }

    public Map insert(String search_type, Map data, Map kwargs) {
        kwargs.put("search_type", search_type);
        kwargs.put("data", data);
        String ret_str = execute("insert", kwargs);
        return get_map_return(ret_str);
    }




    public Map update(String search_key, Map update_data) {
        Map kwargs = new HashMap<String,Object>();
        return update(search_key, update_data, kwargs);
    }

    public Map update(Map sobject, Map update_data) {
        Map kwargs = new HashMap<String,Object>();
        return update(sobject, update_data, kwargs);
    }

    public Map update(Map sobject, Map update_data, Map kwargs) {
        String search_key = (String) sobject.get("__search_key__");
        return update(search_key, update_data, kwargs);
    }

    public Map update(String search_key, Map update_data, Map kwargs) {
        kwargs.put("search_key", search_key);
        kwargs.put("data", update_data);
        String ret_str = execute("update", kwargs);
        return get_map_return(ret_str);
    }



    /*
     * Expression method
     */
    public ArrayList<Map> eval(String expression) {
        Map kwargs = new HashMap<String,Object>();
        return eval(expression, kwargs);
    }

    public ArrayList<Map> eval(String expression, Map kwargs) {
        kwargs.put("expression", expression);
        String ret_str = execute("eval", kwargs);
        return get_array_return(ret_str);
    }

    /*
     * SObject methods
     */

    public Map retire_sobject(String search_key) {
        Map kwargs = new HashMap<String,Object>();
        return retire_sobject(search_key, kwargs);
    }

    public Map retire_sobject(String search_key, Map kwargs) {
        kwargs.put("search_key", search_key);
        String ret_str = execute("retire_sobject", kwargs);
        return get_map_return(ret_str);
    }


    public Map reactivate_sobject(String search_key) {
        Map kwargs = new HashMap<String,Object>();
        return reactivate_sobject(search_key, kwargs);
    }

    public Map reactivate_sobject(String search_key, Map kwargs) {
        kwargs.put("search_key", search_key);
        String ret_str = execute("reactivate_sobject", kwargs);
        return get_map_return(ret_str);
    }




    public Map delete_sobject(String search_key) {
        Map kwargs = new HashMap<String,Object>();
        return delete_sobject(search_key, kwargs);
    }

    public Map delete_sobject(String search_key, Map kwargs) {
        kwargs.put("search_key", search_key);
        String ret_str = execute("delete_sobject", kwargs);
        return get_map_return(ret_str);
    }




    public Map clone_sobject(String search_key, Map data) {
        Map kwargs = new HashMap<String,Object>();
        return clone_sobject(search_key, kwargs);
    }
 

    public Map clone_sobject(String search_key, Map data, Map kwargs) {
        kwargs.put("search_key", search_key);
        kwargs.put("data", data);
        String ret_str = execute("clone_sobject", kwargs);
        return get_map_return(ret_str);
    }


    /*
     * Check-in/Check-out methods
     */
    public void upload_file(String file_path) {
        upload_file(file_path, null);
    }

    public void upload_file(String file_path, String ticket) {
        Map kwargs = new HashMap<String,Object>();
        kwargs.put("path", file_path);
        if (ticket != null) {
            kwargs.put("ticket", ticket);
        }
        execute("upload_file", kwargs);
    }


    public void upload_directory(String dir_path) {
        upload_directory(dir_path, null);
    }

    public void upload_directory(String dir_path, String ticket) {
        Map kwargs = new HashMap<String,Object>();
        kwargs.put("path", dir_path);
        if (ticket != null) {
            kwargs.put("ticket", ticket);
        }
        execute("upload_directory", kwargs);
    }



    public Map create_snapshot(String search_key, String context) {
        Map kwargs = new HashMap<String,Object>();
        return create_snapshot(search_key, context, kwargs);
    }

    public Map create_snapshot(String search_key, String context, Map kwargs) {
        kwargs.put("search_key", search_key);
        kwargs.put("context", context);
        String ret_str = execute("create_snapshot", kwargs);
        return get_map_return(ret_str);
    } 

 


    public Map simple_checkin(String search_key, String context, String file_path) {
        Map kwargs = new HashMap<String,Object>();
        return simple_checkin(search_key, context, file_path, kwargs);
    }


    public Map simple_checkin(String search_key, String context, String file_path, Map kwargs) {
        kwargs.put("search_key", search_key);
        kwargs.put("context", context);
        kwargs.put("file_path", file_path);

        String ret_str = execute("simple_checkin", kwargs);
        return get_map_return(ret_str);
    }




    public Map group_checkin(String search_key, String context, String file_path, String file_range) {
        Map kwargs = new HashMap<String,Object>();
        return group_checkin(search_key, context, file_path, file_range, kwargs);
    }
    public Map group_checkin(String search_key, String context, String file_path, String file_range, Map kwargs) {
        kwargs.put("search_key", search_key);
        kwargs.put("context", context);
        kwargs.put("file_path", file_path);
        kwargs.put("file_range", file_range);

        String ret_str = execute("group_checkin", kwargs);
        return get_map_return(ret_str);
    }



    public Map directory_checkin(String search_key, String context, String dir) {
        Map kwargs = new HashMap<String,Object>();
        return directory_checkin(search_key, context, dir, kwargs);
    }

    public Map directory_checkin(String search_key, String context, String dir, Map kwargs) {
        kwargs.put("search_key", search_key);
        kwargs.put("context", context);
        kwargs.put("dir", dir);

        String ret_str = execute("directory_checkin", kwargs);
        return get_map_return(ret_str);
    }



    public Map add_dependency(String snapshot_code, String file_path, Map kwargs) {
        kwargs.put("snapshot_code", snapshot_code);
        kwargs.put("file_path", file_path);

        String ret_str = execute("add_dependency", kwargs);
        return get_map_return(ret_str);
    }


}


