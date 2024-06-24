const useEffect = React.useEffect;
const useState = React.useState;
const useRef = React.useRef;

const Common = spt.react.Common;
const SelectEditor = spt.react.SelectEditor;
const InputEditor = spt.react.InputEditor;
const SimpleCellRenderer = spt.react.SimpleCellRenderer;
const PreviewCellRenderer = spt.react.PreviewCellRenderer;


// default save implementation
const on_cell_value_changed = params => {

    let table_ref = params.table_ref;
    let data = params.data;
    let column = params.column.colId;

    //console.log("params: ", params);
    data[column] = params.newValue;

    table_ref.current.save(data, column);
}




const Config = (config, options) => {

    let cell_value_changed = options.cell_value_changed;

    if (!cell_value_changed) {
        cell_value_changed = on_cell_value_changed;
    }

    let table_ref = options.table_ref;


    // use these definition types as a starting point
    let definition_types = {
        simple: {
            minWidth: 150,
            resizable: true,
            onCellValueChanged: cell_value_changed,
            cellRenderer: SimpleCellRenderer,
        },
        preview: {
            width: 60,
            resizable: true,
            cellRenderer: PreviewCellRenderer,
        },
        select: {
            minWidth: 150,
            editable: true,
            resizable: true,
            onCellValueChanged: cell_value_changed,
            cellEditor: SelectEditor,
            cellRenderer: SimpleCellRenderer,
        }
    }



    // convert to config_def data
    let config_defs = {};
    config.forEach(config_item => {

        let element_type = config_item.type;
        let definition_type = element_type;
        if (element_type == "number") {
            definition_type = "simple";
        }
        else if (element_type == "color") {
            definition_type = "simple";
        }
        else if (element_type == "date") {
            definition_type = "simple";
        }
        else if (element_type == "email") {
            definition_type = "simple";
        }
        else if (element_type == "phone_number") {
            definition_type = "simple";
        }
        else if (element_type == "text") {
            definition_type = "simple";
        }
        else if (!element_type) {
            definition_type = "simple";
        }



        let name = config_item.name;
        let title = config_item.title;
        let pinned = config_item.pinned;
        let width = config_item.width;
        let flex = config_item.flex;

        if (!name) {
            throw("No name provided in config")
        }

        let config_def = {...definition_types[definition_type]};
        config_defs[name] = config_def;

        config_def["resizable"] = true;


        let required = config_item.required;
        config_def["required"] = required;


        let group = config_item.group;
        if (group) {
            config_def["group"] = group;
        }


        if (config_item.filterable == false) {
            config_def["filter"] = null;
        }

        config_def["field"] = name;
        if (title) {
            config_def["headerName"] = title;
        }
        else {
            config_def["headerName"] = Common.capitalize(name);
        }

        if (pinned) {
            config_def["pinned"] = pinned;
        }

        if (width) {
            config_def["width"] = width;
            config_def["minWidth"] = width;
        }
        if (flex) {
            config_def["flex"] = flex;
        }




        if (element_type == "select") {
            let mode = config_item.mode;

            let labels = config_item.labels;
            let values = config_item.values || [];
            let helpers = config_item.helpers || [];
            if (!labels) {
                labels = values;
            }

            if (typeof(labels) == "string" ) {
                labels = labels.split(",")
            }
            if (typeof(values) == "string" ) {
                values = values.split(",")
            }
            if (typeof(helpers) == "string" ) {
                helpers = helpers.split(",")
            }


            let params = {
                table_ref: table_ref,
                labels: labels,
                values: values,
                helpers: helpers,
            }

            if (options.renderer_params) {
                params = {...params, ...options.renderer_params}
            }


            // applies to buttons or checkboxes
            let layout = config_item.layout;
            if (layout) {
                config_def.layout = layout;
            }


            config_def.cellEditorParams = params;
            config_def.cellRendererParams = params;

            config_def.editable = true;
            config_def.mode = mode;

            config_def.onCellValueChanged = e => {
                let p = {...e, ...params}
                return cell_value_changed(p);
            }

        }
        else {
            let format = config_item.format;
            if (element_type == "number") {
                format = "number";
            }
            else if (element_type == "color") {
                format = "color";
            }
            else if (element_type == "date") {
                format = "date";

                config_def.valueGetter = params => {
                    let column = params.column.colId;
                    let value = params.data[column];
                    if (value) {
                        try {
                            let date = Date.parse(value);
                            let day = date.getDate() + "";
                            let month = (date.getMonth() + 1) + "";
                            let year = date.getFullYear() + "";
                            value = year + "-" + month.padStart(2, "0") + "-" + day.padStart(2, "0");
                        }
                        catch(e) {
                            value = null;
                        }
                    }
                    return value;
                }
            }


            let params = {
                table_ref: table_ref,
                mode: format,
            }

            if (options.renderer_params) {
                params = {...params, ...options.renderer_params}
            }

            let helper = config_item.helper;
            if (helper) {
                config_def.helper = helper;
            }

            let error = config_item.error;
            if (error) {
                config_def.error = error;
            }

            // number of rows in the input
            let rows = config_item.rows;
            if (rows) {
                config_def.rows = rows;
            }


            let editable = config_item.editable;
            if (editable == false || editable == "false") {
                config_def.editable = false;
            }
            else {
                config_def.editable = true;
                if (format) {
                    if (format == "number") {
                        // for some reason, number doesn't work
                        config_def.cellDataType = false;
                    }
                    else {
                        config_def.cellDataType = format;
                    }
                }
                config_def.cellEditor = InputEditor;
                config_def.cellEditorParams = params;
                config_def.onCellValueChanged = e => {
                    let p = {...e, ...params}
                    return cell_value_changed(p);
                }
            }
            config_def.cellRendererParams = params;


        }



        // handle the display
        let cell_renderer = config_item.renderer;
        if (cell_renderer) {
            try {
                // see if there is a component defined for this
                config_def.cellRenderer = eval(cell_renderer) || cell_renderer;
            }
            catch(e) {
                // otherwise it is accessed through a named string
                config_def.renderer = cell_renderer;
            }
        }

        config_def.autoHeight = true;

    } );


    return config_defs;

}


// Store this
spt.react.Config = Config;




