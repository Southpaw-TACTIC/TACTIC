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
import java.util.*;

import java.awt.*;
import javax.swing.*;
import javax.swing.table.*;
import java.awt.event.*;
import java.net.*;



public class GuiCreator
{

    final Container my_content_pane;
    final DefaultTableModel my_file_table_model = new DefaultTableModel();


    String my_server_url = "http://www.sthpw.com/sthpw/upload_server.pl";
    String my_ticket = "";
    ArrayList my_uploads = new ArrayList();


    public GuiCreator( Container content_pane )
    {
        my_content_pane = content_pane;
    }


    public void set_server_url(String url)
    {
        my_server_url = url;
    }

    public void set_ticket(String ticket_id)
    {
        my_ticket = ticket_id;
    }    

    public ArrayList get_uploads()
    {
        return my_uploads;
    }

    public void create_gui()
    {
        my_content_pane.setBackground( Color.WHITE );

        // set the layout for this frame
        my_content_pane.setLayout(
            new BoxLayout(my_content_pane, BoxLayout.X_AXIS)
        );

        // create the left panel
        JPanel left_panel = new JPanel( new BorderLayout() );
        left_panel.setBackground( Color.WHITE );
        left_panel.setBorder(
            BorderFactory.createTitledBorder(
                BorderFactory.createTitledBorder("File List")
            )
        );

        //my_file_table_model = new DefaultTableModel();
        //final JTable file_table = new JTable(my_file_table_model);
        final JTable file_table = new DroppableTable();
        file_table.setModel( my_file_table_model );
        my_file_table_model.addColumn("Files");

        file_table.setRowSelectionAllowed(true);
        file_table.setShowVerticalLines(false);
        file_table.setAutoResizeMode( JTable.AUTO_RESIZE_ALL_COLUMNS );
        file_table.setDragEnabled(true);


        ScrollPane scroll_pane = new ScrollPane();
        scroll_pane.add(file_table);
        scroll_pane.setWheelScrollingEnabled(true);
        scroll_pane.doLayout();

        left_panel.add(scroll_pane);



        // add the right panel
        JPanel right_panel = new JPanel( new BorderLayout() );
        right_panel.setBackground( Color.WHITE );
        right_panel.setBorder(
            BorderFactory.createCompoundBorder(
                BorderFactory.createTitledBorder("Actions"),
                BorderFactory.createEmptyBorder(2,2,2,2)
            )
        );
        right_panel.setLayout( new BoxLayout(right_panel,BoxLayout.Y_AXIS) );




        // add buttons to the right panel
        JButton add_button = new JButton("Add Files");
        add_button.addActionListener( new ActionListener() {
            public void actionPerformed( ActionEvent e ) {
                open_file_chooser();
            }
        } );


        JButton remove_button = new JButton("Remove Selected");
        remove_button.addActionListener( new ActionListener() {
            public void actionPerformed( ActionEvent e ) {

                // remove rows backwards by index
                int[] selected_rows = file_table.getSelectedRows();
                for ( int i = selected_rows.length - 1; i >= 0; i-- )
                {
                    my_file_table_model.removeRow(selected_rows[i]);
                }
            }
        } );



        JButton upload_button = new JButton("Upload All");
        upload_button.addActionListener( new ActionListener() {
            public void actionPerformed( ActionEvent e ) {
                do_upload();
            }
        } );


        right_panel.add(add_button);
        right_panel.add(Box.createVerticalStrut(5));
        right_panel.add(remove_button);
        right_panel.add(Box.createVerticalStrut(5));
        right_panel.add(upload_button);


        my_content_pane.add(left_panel, BorderLayout.NORTH);
        my_content_pane.add(right_panel, BorderLayout.NORTH);

    }




    final public void open_file_chooser()
    {

        // instantiate the file browser
        final JFileChooser file_chooser = new JFileChooser();
        file_chooser.setFileSelectionMode(JFileChooser.FILES_AND_DIRECTORIES);
        file_chooser.setMultiSelectionEnabled(true);
        file_chooser.setDialogTitle("Select Files To Upload");


        int return_val = file_chooser.showOpenDialog(my_content_pane);
        if( return_val == JFileChooser.APPROVE_OPTION) {

            File[] selected_files = file_chooser.getSelectedFiles();

            // add them to the table list
            for ( int i = 0; i < selected_files.length; i++ )
            {
                boolean is_new_file = true;

                // make sure no duplicates are added
                for (int j = 0; j < my_file_table_model.getRowCount(); j++)
                {
                    File file = (File) my_file_table_model.getValueAt(j,0);

                    if ( file.getAbsolutePath().equals(
                            selected_files[i].getAbsolutePath() ) )
                    {
                        is_new_file = false;
                        break;
                    }
                }

                if ( is_new_file == false )
                    continue;



                my_file_table_model.addRow(
                    new Object[] { selected_files[i] }
                );

            }

            // unselect all of the files
            file_chooser.setSelectedFile( null );

        }

    }

    public void execute() throws IOException
    {
        if (my_server_url.startsWith("http://"))
              do_upload();
        else if (my_server_url.startsWith("file://"))   
              do_upload(true);
    }
    
    final public void do_upload()
    {
        do_upload(false);
    }    

    final public void do_upload(boolean copy_mode)
    {
        String from_path = "";

        try {
            URL url = new URL(my_server_url);
            // upload every file in list
            for (int j = 0; j < my_file_table_model.getRowCount(); j++)
            {
                File file = (File) my_file_table_model.getValueAt(j,0);
                from_path = file.getAbsolutePath();

                if (copy_mode)
                    url =  new URL(my_server_url + "/" +file.getName());

                Upload upload = new Upload( url, from_path);
                upload.set_ticket(my_ticket);

                if (copy_mode)
                    upload.do_copy();
                else
                    upload.do_upload();
                // store the upload object
                my_uploads.add(upload);
            }

            // remove all of the rows
            int row_count = my_file_table_model.getRowCount();
            for ( int i = row_count - 1; i >= 0; i-- )
            {
                my_file_table_model.removeRow(i);
            }


        }
        catch (IOException ex)
        {
            System.out.println( "Error: " + ex.getMessage() );
            System.out.println( "Failed to upload ["+from_path+"]" );
        }
    }



}



