2010-12-08

Example: completion_expression_wdg
------------------------------------

This widget is inserted into the Widget Config as a config for a CustomLayoutWdg.  It use Python MAKO to build a completion bar from the results provided by the expression option.

Options
------------------------------------

thickness: The thickness of the bar in pixels
bar_color: The color of the bar ie '#FFFFFF' or 'blue'
expression:  The expression to evaluate for the row.  This expression needs to return a float number from 0-1 ie "0.4"

    example expression
    ------------------       
   
    @COUNT(di/shot.sthpw/task['status', 'waiting'])*1.0 / @COUNT(di/shot.sthpw/task)



Setup
------------------------------------

In the example_element_definition.txt there is an example XML snippet that can be used to paste into the XML window mode when creating a new column.

In the completion_expression_wdg.txt file is the xml code needed in the widget config.  In the TACTIC interface navigate to the Widget config and insert a new entry with the following:

category: CustomLayoutWdg
search_type: CustomLayoutWdg
view: completion_expression_wdg
config: [contents of completion_expression_wdg.txt]
