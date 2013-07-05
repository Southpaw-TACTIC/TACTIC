The following is a simple popup widget setup to insert work hours for a particular task and parent.

note *This requires adding a new column "task_code" to the work_hour table in your project



Inserting the Button
------------------------------------------

1. Right clicking the table header in a task view and choose "create new column".
2. Switch the mode in the popup to XML
3. Set the element name to "work_hours_insert"
4. Paste the contents of the file "work_hours_insert_button.txt"
5. Save




Inserting the widget config
------------------------------------------
1. Open up the Widget config in the sidebar under Project Settings.
2. Create a new entry with the following properties
    Category: CustomLayoutWdg
    Search Type: CustomLayoutWdg
    view: work_hours_insert_wdg
    config: [contents of work_hours_insert_wdg.txt]
3. Save
