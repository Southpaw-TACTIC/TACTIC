/* *********************************************************
 *
 * Copyright (c) 2005, Southpaw Technology
 *                     All Rights Reserved
 * 
 * PROPRIETARY INFORMATION.  This software is proprietary to
 * Southpaw Technolog, and is not to be reproduced, transmitted,
 * or disclosed in any way without written permission.
 * 
 * 
 */ 


// initialize api namspace.
// FIXME: This should not be here
spt.api = {}

//
// Utility functions for the api
//
spt.api.Utility = new Class( {
} )



// Method to get all of the input values under an element.
//
// @params:
//  element_id: can either be the element or its id.  All input values under
//      this element will be returned
//  filter: filter used to find input elements.  For example, the default
//      is .spt_input, meaning that all elements with a class of ".spt_input"
//      will be looked at for a value
//  return_array: flag to determine whether each key is an array or just
//      a single value
//  return_label: return the labels as well for select
//  kwargs - cb_boolean: force a checked checkbox to return true as value
//
// @return
//  dict: of all the name values pairs found under element_id
//
spt.api.Utility.get_input_values = function(element_id, filter, return_array, return_labels, kwargs) {

    if (filter == undefined || filter == null)
        filter = ".spt_input";

    if (return_array == undefined || return_array == null)
        return_array = true;

    if (return_labels == undefined || return_labels == null)
        return_labels = false;

    if (! kwargs) kwargs = {};

    var element = $(element_id);

    var input_list; 
    if (element) {
        input_list = $(element_id).getElements(filter);
        // include top element if it is also an input
        if (element.hasClass && element.hasClass(filter.replace("\.", "")) ) {
            input_list.push(element);
        }
    }

    else
        input_list = document.getElements(filter);

    //for multple select
    var get_multi = function (obj) { 
        var selected = [];
        var storage = [];
        while (obj.selectedIndex != -1) { 
            selected.push(obj.options[obj.selectedIndex].value); 
            storage.push(obj.selectedIndex);
            obj.options[obj.selectedIndex].selected = false; 
        } 
        //restore the state
        for (var k=0; k < storage.length; k++)
            obj.options[storage[k]].selected = true;

        return selected
    }
    var values = {};

    // list of elements that are designated as arrays
    var array_keys = {};

    for (var i = 0; i < input_list.length; i++) {
        var filter = input_list[i];
        if (filter.getAttribute("disabled") == "disabled") {
            continue;
        }

        // protect against elements with no name
        if (filter.name == undefined) {
            continue;
        }

        if (values[filter.name] == undefined) {
            values[filter.name] = [];
        }

        // return labels if asked for
        if (return_labels == true && filter.nodeName == 'SELECT') {
            if (filter.getAttribute('multiple')){
                // it can only return one really for now until we don't use Enter 
                // to accept a multi select
                label = get_multi(filter);
                label = label.join(',');
            }
            else {
                var index = filter.selectedIndex;
                if (index == -1) {
                    label = "????";
                }
                else {
                    label = filter.options[index].text;
                }
            }
            values[filter.name].push(label);
            //spt.js_log.warning("label: " + label);
        }
        else if (filter.type =='checkbox') {
            var is_multiple = filter.getAttribute("spt_is_multiple");
            if (is_multiple == "true") {
                array_keys[filter.name] = is_multiple;
            }

            if (filter.checked) {
                var value = filter.value;
                if (value == 'on' && kwargs['cb_boolean'] == true)
                    value = "true";
                if (!value) {
                    value = "true";
                }
                values[filter.name].push(value);
            }
            else {
                values[filter.name].push("");
            }
        }
        else if (filter.type =='radio') {
            if (filter.checked) {
                var value = filter.value;
                values[filter.name].push(value);
            }
        }
        else {
            var value = filter.getAttribute("spt_input_value");
            var is_multiple = filter.getAttribute("spt_is_multiple");
            if (is_multiple == "true") {
                array_keys[filter.name] = is_multiple;
            }
            
            if (value == null) {
                if (filter.getAttribute("multiple")){
                    var value_arr = get_multi(filter);
                    for (var k=0; k<value_arr.length; k++)
                        values[filter.name].push(value_arr[k]);
                }
                else {
                    value = filter.value;
                    values[filter.name].push(value);
                }
            }
            else {
                    values[filter.name].push(value);
            }

                
            
        }

    }

    // if return_array flag is false, return the first element, unless
    // it is specifically marked as an array
    if ( return_array == false ) {
        for (var i in values) {

            if (array_keys[i]) {
                continue;
            }

            var value = values[i][0];
            if (value != undefined)
                values[i] = values[i][0];
        }
    }

    return values;
}



// Method to set a number of input elements located under a top element.
// The values for thie input elements are passed in as a dictionary named
// values and will correspond to each element by a naming convention of
// the following: the key of the dictionary will correspond to an element
// containing the class "spt_<key>"
//
// @params:
//  element_id: can either be the element or its id. 
//  values: a dictionary of name/value pairs which will be used to populate
//    the input elements below the element specified by element_id
//
spt.api.Utility.set_input_values2 = function(element_id, values, filter) {
    if (filter == undefined)
        filter = ".spt_input";

    // get all of the inputs
    var element = $(element_id);
    if (!element){
        //alert(element_id + 'is null');
    	return;
    }
    var input_list = element.getElements(filter);

    for ( var i = 0; i < input_list.length; i++ ) {
        var input = input_list[i];
        var name = input.name;
        var value = values[name];
        input.value = value;
    }

    /*
    var input = input_list[0];
    if (input == null) {
        //alert('No input widgets found');
        return;
    }
    input.value = values;
    */
    return input
   
}



// This is a deprecated implementation of this function.  It is only used
// spt.dg_table.select_cell_for_edit_cbk.
spt.api.Utility.set_input_values = function(element_id, values, filter) {
    if (filter == undefined)
        filter = ".spt_input";

    // get all of the inputs
    var element = $(element_id);
    if (!element){
        //alert(element_id + 'is null');
    	return;
    }
    var input_list = element.getElements(filter);
    var input = input_list[0];
    if (input == null) {
        //alert('No input widgets found');
        return;
    }
    input.value = values;
    return input
   
}





// Method to clear all the input element located under a top element
//
//  @params
//  element_id: can either be the element or its id.  All input values under
//      this element will be returned
//  filter: filter used to find input elements.  For example, the default
//      is .spt_input, meaning that all elements with a class of ".spt_input"
//      will be looked at for a value
//
spt.api.Utility.clear_inputs = function(element_id, filter) {
    if (filter == undefined)
        filter = ".spt_input";

    var input_list = $(element_id).getElements(filter);
    for (var i = 0; i < input_list.length; i++) {
        var filter = input_list[i];
        if (filter.type =='checkbox') {
            filter.checked = false;
        }
        else if (filter.type =='hidden') {
            continue;  
        }
        else {
            filter.value = '';
        }

    }
}


// Method gather all of the inputs with a specific name. This is meant to
// replace the traditional document.form.elements['xxx'].
//
// @params
//  element_id: can either be the element or its id.  All input values under
//      this element will be returned
//  name: name of the input to search for
//  filter: filter used to find input elements.  For example, the default
//      is .spt_input, meaning that all elements with a class of ".spt_input"
//      will be looked at for a value
//
// @return:
// inputs: a list of input elements
//
spt.api.Utility.get_inputs = function(element_id, name, filter) {
    if (filter == undefined)
        filter = ".spt_input";

    // todo: this is a little heavy to search linearly
    var input_list = $(element_id).getElements(filter);
    var list = [];
    for (var i = 0; i < input_list.length; i++) {
        var input = input_list[i];
        var input_name = input.getAttribute("name");
        if (input_name == name) {
            list.push(input);
        }
    }
    return list;
}


// Get a single element of a specific name
//
spt.api.Utility.get_input = function(element_id, name, filter) {
    var list = spt.api.Utility.get_inputs(element_id, name, filter);
    if (list.length == 0) {
        return null;
    }
    else {
        return list[0];
    }
    
}

//
// Display functions
//

// Method to toggle the display of any element
// 
// @params
// element_id: the id of the element who display is to be toggled
//
spt.api.Utility.toggle_display = function(element_id)
{

    var element = $(element_id);
    if (element == null) {
        return;
    }

    if ( element.style.display == "none" )
        set_display_on(element_id);
    else
        set_display_off(element_id);
}



// Method to explicitly set the display
//
spt.api.Utility.set_display_on = function(element_id)
{
    for (var i=0; i < arguments.length; i++)
    {
        var element_id = arguments[i]
        var element = document.getElementById( element_id )
        if (!element)
        {
            // Commenting this out until Event container can remove listeners
            //alert("Element id: " + element_id)
            continue
        }
        
        // check that the element has a display defined
        if ( element && element.style.display == "" )
            alert( "Element ["+element_id+"] has undefined display" )

        
        if ( spt.browser.is_IE() == true ) {
            element.style.display = "block"
        }
        else {
            if ( element instanceof HTMLDivElement )
                element.style.display = "block"
            else if ( element instanceof HTMLTableSectionElement )
                element.style.display = "table-row-group"
            else if ( element instanceof HTMLTableRowElement )
                element.style.display = "table-row"
            else if ( element instanceof HTMLTableCellElement )
                element.style.display = "table-cell"
            else if (element instanceof HTMLSpanElement )
                element.style.display = "inline"
            else 
                element.style.display = "block"
            $( element_id ).setStyle('opacity',1) 
        }
    }
}



// Method to explicitly set the display
// 
spt.api.Utility.set_display_off = function(element_id)
{
    for (var i=0; i < arguments.length; i++)
    {
        var element_id = arguments[i]
        var element = document.getElementById( element_id )
        if (!element)
            continue
        // check that the element has a display defined, don't bother with IE
        if ( element.style.display == "" && !spt.browser.is_IE())
            alert( "Element ["+element_id+"] has undefined display" )

        element.style.display = "none"
    }
}
// save WidgetSettings for mostly inputs
spt.api.Utility.save_widget_setting = function(key, data)
{
    var options = {'data': data, 'key': key};
    var values = {};
    var server = new TacticServerStub.get();
    var class_name = "pyasm.web.WidgetSettingSaveCbk";
    server.execute_cmd(class_name, options, values);
}

// remap some functions
toggle_display = function(element_id) {
    spt.api.Utility.toggle_display(element_id)
}
set_display_on = function(element_id) {
    spt.api.Utility.set_display_on(element_id)
}
set_display_off = function(element_id) {
    spt.api.Utility.set_display_off(element_id)
}






