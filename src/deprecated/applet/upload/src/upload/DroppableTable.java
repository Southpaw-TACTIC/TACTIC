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
import javax.swing.event.*;

import java.awt.dnd.*;
import java.awt.datatransfer.*;

import java.net.URL;


public class DroppableTable extends JTable implements DropTargetListener
{
    DropTarget dropTarget = new DropTarget (this, this);

    public DroppableTable()
    {
        setModel( new DefaultTableModel() );
    }

    public void dragEnter (DropTargetDragEvent dropTargetDragEvent)
    {
        dropTargetDragEvent.acceptDrag (DnDConstants.ACTION_COPY_OR_MOVE);
    }

    public void dragExit (DropTargetEvent dropTargetEvent) {}
    public void dragOver (DropTargetDragEvent dropTargetDragEvent) {}
    public void dropActionChanged (DropTargetDragEvent dropTargetDragEvent){}

    public synchronized void drop (DropTargetDropEvent dropTargetDropEvent)
    {
        try
        {
            Transferable tr = dropTargetDropEvent.getTransferable();
            if (tr.isDataFlavorSupported(DataFlavor.stringFlavor)) {
                dropTargetDropEvent.acceptDrop(
                        DnDConstants.ACTION_COPY_OR_MOVE);

                DefaultTableModel tableModel = (DefaultTableModel) getModel();

                String files_str = (String)
                    tr.getTransferData(DataFlavor.stringFlavor);
                String[] files = files_str.split("\r\n");

                for ( int i = 0; i < files.length; i++ )
                {
                    if ( files[i].startsWith("file://") )
                    {
                        String path = files[i];
                        System.out.println(path + ": " + path.length() );
                        path = path.replaceFirst("file://", "");
                        path = path.replaceAll("%20", " ");

                        File file = new File(path);
                        if ( file.exists() == true )
                        {
                            tableModel.addRow( new Object[] {file} );
                        }
                    }
                }

                dropTargetDropEvent.getDropTargetContext().dropComplete(true);
            }
            else if (tr.isDataFlavorSupported(DataFlavor.javaFileListFlavor)) {
                dropTargetDropEvent.acceptDrop(
                        DnDConstants.ACTION_COPY_OR_MOVE);

                java.util.List files_list = (java.util.List)
                    tr.getTransferData(DataFlavor.javaFileListFlavor);

                DefaultTableModel tableModel = (DefaultTableModel) getModel();

                for ( Iterator it = files_list.iterator(); it.hasNext();)
                {
                    File file = (File) it.next();
                    System.out.println("file: " + file.getPath());
                    if ( file.exists() )
                        tableModel.addRow( new Object[] {file} );
                }

 
            }
            else {
                System.err.println ("Rejected");
                dropTargetDropEvent.rejectDrop();
            }
        }
        catch (Exception e) {
            dropTargetDropEvent.rejectDrop();
            e.printStackTrace();
            System.err.println(e);
            
        }
    }

}


