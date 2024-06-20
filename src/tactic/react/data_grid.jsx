/*
import { useState } from "react";
import { useEffect } from "react";
import { useReducer } from 'react';
import { useRef } from 'react';
*/
let useEffect = React.useEffect;
let useState = React.useState;

const Common = spt.react.Common;

//const DataGrid = (props) => {
const DataGrid = React.forwardRef( (props, ref) => {

    React.useImperativeHandle( ref, () => ({
        add_filter(filter) {
            add_filter(filter);
        },
        select_all() {
            select_all();
        },
        unselect_all() {
            unselect_all();
        },
        get_selected_nodes() {
            return get_selected_nodes();
        },
        get_selected_rows() {
            return get_selected_rows();
        },

        get_filtered_nodes() {
            return get_filtered_nodes();
        },
        get_filtered_rows() {
            return get_filtered_rows();
        },
        get_columns() {
            return get_columns();
        },
        refresh_cells(nodes) {
            refresh_cells(nodes);
        },

        add_filter(filter) {
            add_filter();
        },
        get_filter(column) {
            return get_filter(column);
        },


        set_filter(column, options) {
            set_filter(column, options);
        },

        clear_filters() {
            clear_filters();
        },
        clear_sort() {
            clear_sort();
        },

        export_csv(params) {
            export_csv(params);
        },
        set_data(data) {
            set_data(data);
        },
        get_data() {
            return data;
        },

        show_total() {
            _show_total({
                api: api
            });
        }



    }))

    const [loading, set_loading] = useState(true);
    const [api, set_api] = useState(null);

    const [grid_name, set_grid_name] = useState(null);
    const [grid_options, set_grid_options] = useState(null);

    const [onselect, set_onselect] = useState(null);

    const [data, set_data] = useState([]);




    const add_filter = filter => {
        api.setQuickFilter(filter);
    }



    const get_filter = (column) => {
        // Get a reference to the filter instance
        const filterInstance = api.getFilterInstance(column);
        let model = filterInstance.getModel();
        return model;
    }


    const set_filter = (column, options) => {

        // Get a reference to the filter instance
        const filterInstance = api.getFilterInstance(column);

        if (options.conditions) {
            // Assume it is a full model
            filterInstance.setModel(options);
            return;
        }

        if (typeof options == "string") {
            options = {
                filter: options
            }
        }

        if (!options.filterType) {
            options.filterType = "text"
        }

        if (!options.type) {
            options.type = "startsWith"
        }

        // Set the filter model
        /*
            filterType: 'text',
            type: 'startsWith',
            filter: 'Animator',
        */
        filterInstance.setModel(options);

        // Tell grid to run filter operation again
        api.onFilterChanged();
    }


    const select_all = () => {
        api.selectAll();
    }

    const unselect_all = () => {
        api.deselectAll();
    }

    const get_selected_nodes = () => {
        return api.getSelectedNodes();
    }
    const get_selected_rows = () => {
        return api.getSelectedRows();
    }

    const get_filtered_nodes = () => {
        let all_nodes = [];
        api?.forEachNodeAfterFilter((rowNode) => all_nodes.push(rowNode));
        return all_nodes;
    }

    const get_filtered_rows = () => {
        let all_rows = [];
        api?.forEachNodeAfterFilter((rowNode) => all_rows.push(rowNode.data));
        return all_rows;
    }

    const get_columns = () => {
        let columns = [];
        //grid_options.columnApi.getAllGridColumns().forEach(item => {
        api.getAllGridColumns().forEach(item => {
            let column = item.colId;
            columns.push(column);
        } )
        return columns;
    }


    const export_csv = (params) => {

        if (!params) {
            params = {};
        }

        if (!params.processHeaderCallback) {
            params.processHeaderCallback = (cell) => {
                let column = cell.column.colId;
                try {
                    let parts = column.split("-");
                    if (parts.length != 3) {
                        throw("Not a date");
                    }
                    let date = Date.parse(column);
                    return column;
                }
                catch(e) {
                    // return display name
                    return cell.columnApi.getDisplayNameForColumn(cell.column, null);
                }
            }
        }

        api.exportDataAsCsv(params);
    }



    const redrawRows = (nodes) => {
        setTimeout( () => {
            api.redrawRows({
                nodes: nodes,
                force: true,
                suppressFlash: true
            });
        }, 0 );
    }

    const refresh_cells = (nodes) => {
        setTimeout( () => {
            //api.redrawRows({
            api.refreshCells({
                nodes: nodes,
                force: true,
                suppressFlash: true
            });
        }, 0 );
    }


    // Function to demonstrate calling grid's API
    const deselect = () => {
        api.deselectAll()
    }



    const on_selection_changed = (e) => {

        let selectedRows = e.api.getSelectedRows();
        let selectedNodes = e.api.getSelectedNodes();

        let onselect = props.onselect;
        if (!onselect) return;

        onselect(selectedRows, selectedNodes);
    }



    const clear_filters = () => {
        return api.setFilterModel(null);
    }


    const clear_sort = () => {
        //let column_api = grid_options.columnApi;
        return api.applyColumnState( {
            defaultState: { sort: null }
        } )

    }





    // TEST TEST
    const _show_total = (params) => {
        if (!props.show_total && !props.get_total_data) return;

        if (!params.api) return;


        let pinned;
        // These should be removed
        if  (props.show_total == "cost") {
            setTimeout( () => {
                pinned = generate_pinned_data(params)
                params.api.setPinnedTopRowData( [pinned]  );
            }, 0 )
        }
        else if (props.show_total == "role") {
            setTimeout( () => {
                pinned = generate_pinned_data2(params)
                params.api.setPinnedTopRowData( [pinned]  );
            } )
        }
        else if (props.show_total == "work_hour") {
            setTimeout( () => {
                pinned = generate_pinned_data2(params)
                params.api.setPinnedTopRowData( [pinned]  );
            } )
        }


        else if (props.get_total_data) {

            let columns = [];
            params.api.getAllGridColumns().forEach(item => {
                let column = item.colId;
                let parts = column.split("-");
                if (parts.length == 3) {
                    columns.push(column);
                }
            });


            // need a set timeout here so that it calculates later
            setTimeout( () => {
                pinned = props.get_total_data(params, columns);

                if (pinned) {
                    if (Array.isArray(pinned) ) {
                        params.api.setPinnedTopRowData( pinned  );
                    }
                    else {
                        params.api.setPinnedTopRowData( [pinned]  );
                    }
                }
                else {
                    alert("ERROR: pinned data is undefined")
                }
            }, 0 )
        }

    }

    const on_grid_ready = (params) => { _show_total(params); }
    const on_filter_changed = (params) => { _show_total(params); }
    const on_cell_clicked = (params) => { _show_total(params); }






    useEffect( () => {
        let random = Math.floor( Math.random()*100000000 );
        let grid_name = props.name + random;
        set_grid_name(grid_name);

        let pagination = true;
        let pagination_size = props.pagination_size || 10000;
        if (props.pagination != null) {
            pagination = props.pagination;
        }
        else {
            pagination: props.auto_height ? false : true;
        }


        // Grid Options are properties passed to the grid
        const gridOptions = {

          // each entry here represents one column
          columnDefs: props.column_defs,

          // default col def properties get applied to all columns
          defaultColDef: {
              sortable: true,
              filter: true,
              filterParams: {
                  "maxNumConditions": 10,
                  "numAlwaysVisibleConditions": 2,
              }
          },

          rowSelection: props.row_selection || 'multiple', // allow rows to be selected
          animateRows: true, // have rows animate to new positions when sorted

          //paginationAutoPageSize: true,
          pagination: pagination,
          paginationPageSize: pagination_size,
          //pagination: props.auto_height ? false : false,


          onGridReady: on_grid_ready,
          onFilterChanged: on_filter_changed,
          onCellClicked: on_cell_clicked,

          singleClickEdit: props.single_click == true ? true : false,
          suppressClickEdit: props.suppress_click == true ? true : false,
          suppressRowClickSelection: true,

          suppressDragLeaveHidesColumns: true,
          onColumnVisible: e => {
              //console.log("e: ", e)
          },


          getRowStyle: get_row_style,
          getRowHeight: get_row_height,





          // while this is the behvaior we want, it does not behave well with selects
          stopEditingWhenCellsLoseFocus: props.click_off == true ? true : false,
        
          groupHeaderHeight: 20,

          //overlayNoRowsTemplate: "...",

        };

        if (props.enable_undo || props.on_undo) {
            gridOptions.undoRedoCellEditing = true;
            gridOptions.undoRedoCellEditingLimit = 20;
            gridOptions.onUndoStarted = props.on_undo;
            gridOptions.onRedoStarted = props.on_redo;
        }

       
        if (props.on_cell_key_down ) {
            gridOptions.onCellKeyDown = props.on_cell_key_down;
        }


        // Set the height
        let row_height = 25;
        if (props.row_height) {
            row_height = props.row_height;
        }
        gridOptions["rowHeight"] = row_height;


        if (props.auto_height) {
            gridOptions["domLayout"] = "autoHeight";

        }
        else {
            gridOptions["domLayout"] = "normal";
        }


        if (props.components) {
             gridOptions["components"] = props.components;
             //gridOptions["frameworkComponents"] = props.components;
        }

        if (props.filter) {
            gridOptions["isExternalFilterPresent"] = () => {return true};
            gridOptions["doesExternalFilterPass"] = props.filter;
            gridOptions.cacheQuickFilter = false;
        }

        if (props.show_full_header) {
            if (props.header_height) {
                gridOptions["headerHeight"] = props.header_height;
            }
            gridOptions["defaultColDef"] = {
                "wrapHeaderText": true,
                "autoHeaderHeight": true,
                filterParams: {
                    "maxNumConditions": 10,
                }

            }
        }
        else {
            gridOptions["headerHeight"] = props.header_height || 25;
        }


        // Add grouping
        add_grouping(gridOptions);

        if (props.on_column_moved) {
            gridOptions.onColumnMoved = props.on_column_moved;
        }



        set_grid_options(gridOptions);
        set_api( gridOptions.api );


        set_loading(false);

    }, [] );


    useEffect( () => {
        if (!grid_options) return;
        if (!grid_name) return;


        grid_options.onSelectionChanged = on_selection_changed;

        // get div to host the grid
        const eGridDiv = document.getElementById(grid_name);
        // new grid instance, passing in the hosting DIV and Grid Options
        //let grid = new agGrid.Grid(eGridDiv, grid_options);
        let api = agGrid.createGrid(eGridDiv, grid_options);
        set_api(api);


        // Stop editing when click on anything
        eGridDiv.addEventListener( "blur", e => {
            api.stopEditing();
        } )
 

        if (props.column_defs) {
            //api.setColumnDefs(props.column_defs);
            api.setGridOption("columnDefs", props.column_defs);

            /*
            // Custom comparator that sorts header rows separately
            function customComparator(valueA, valueB, nodeA, nodeB) {
              if (nodeA.data.__type__ == "group" && !nodeB.data.__type__ == "group") {
                return -1; // Always sort header rows first
              } else if (!nodeA.data.__type__ == "group" && nodeB.data.__type__ == "group") {
                return 1; // Always sort non-header rows last
              } else {
                // Normal comparison logic
                if (valueA < valueB) {
                  return -1;
                } else if (valueA > valueB) {
                  return 1;
                } else {
                  return 0;
                }
              }
            }

            let group_column = "department";
            let definition = props.column_defs[group_column];
            console.log("props: ", props.column_defs);
            if (definition) {
                definition.comparator = customComparator;
            }
            */

        }


        if (props.data != data) {
            let data = props.data;
            api.setRowData(data);
            set_data(data);
        }

    }, [grid_name, grid_options] );



    const get_row_style = params => {

        let css = {};
        if (props.get_row_style) {
            css = props.get_row_style(params) || {};
        }

        if (params.data.__type__ == "group") {
            css["background"] = params.data.__background__ || "#CCC";
            css["color"] = params.data.__color__ || "#000";
        }

        if (params.data.__isVisible__ == false) {
            css["display"] = "none";
        }
        else {
            css["display"] = "";
        }

        return css;
    }

    const get_row_height = params => {
        if (params.data.__isVisible__ == false) {
            return 0;
        }

    }


    const add_grouping = (grid_options) => {

        // Event listener for when the filter is changed
        //grid_options.onFilterChanged = event => {
        //};

        /*
        grid_options.isExternalFilterPresent = () => {
            return true;
        };
        grid_options.doesExternalFilterPass = node => {
            if (node.data.__type__ == "group") return true;
        }
        */


        // Event listener for when the sort order is changed
        grid_options.onSortChanged = event => {
            var rowData = [];

            // remove all groups
            event.api.forEachNode(function(node) {
                if (node.data.__type__ == 'group') {
                    return;
                }
                rowData.push(node.data);
            });


            //let columnState = grid_options.columnApi.getColumnState();
            let columnState = event.api.getColumnState();
            let sortedColumns = columnState.filter(column => column.sort !== null);
            if (sortedColumns.length == 0) {
                if (grid_options.group_by != "") {
                    // group all the data
                    rowData = group_data(rowData, grid_options.group_by);

                }
            }

            set_data(rowData);
            //event.api.setRowData(rowData);
            event.api.setGridOption('rowData', rowData)
            event.api.redrawRows();

        };

    }



    useEffect( () => {

        if (!grid_options) {
            return;
        }
        if (!api) return;


        if (props.column_defs) {
            //api.setColumnDefs(props.column_defs);
            api.setGridOption("columnDefs", props.column_defs);
        }



        if (props.data) {
            let data = props.data;
            if (props.group_by) {
                //data = group_data(data, props.group_by)
                grid_options["group_by"] = props.group_by;

                // Find the sorted column(s)
                //let columnState = grid_options.columnApi.getColumnState();
                let columnState = api.columnModel.getColumnState();
                let sortedColumns = columnState.filter(column => column.sort !== null);
                if (sortedColumns.length > 0) {
                    // let event handle the grouping
                    clear_filters();
                    clear_sort();
                    let options = {
                        order_list: props.order_list,
                        sort_column: sortedColumns[0].colId,
                    }
                    data = group_data(data, props.group_by, options);
                    api.setRowData(data);
 
                }
                else {
                    let options = {
                        order_list: props.order_list
                    }
                    data = group_data(data, props.group_by, options);
                    api.setRowData(data);
                }
            }
            else {
                grid_options["group_by"] = "";
                api.setRowData(data);
            }
        }


    }, [props, api] )





    //
    // Group Data
    //
    const group_data = (items, group_by, options) => {

        if (!options) options = {};

        // Add groups
        let last_group_value = null;

        //clear_filters();
        //clear_sort();

        let sort_column = null;
        if (options.sort_column) {
            sort_column = options.sort_column;
        }

        let order_list = null;
        if (options.order_list) {
            ///order_list = ["Roto", "Match Move", "Modeling", "Animation", "FX", "Lighting", "Compositing"]
            order_list = options.order_list;
        }

        items = [...items];

        if (!order_list) {
            items.sort((a, b) => a[group_by]?.localeCompare(b[group_by]));
        }
        else {

            items.sort((a, b) => {
                let a_value = a[group_by];
                let b_value = b[group_by];
                if (!a_value || a_value == "") {
                    a_value = "ZZZ";
                }
                if (!b_value || b_value == "") {
                    b_value = "ZZZ";
                }


                // If the group values are the same, then sort by the sort column if it exists
                if (a_value == b_value) {
                    if (sort_column) {
                        if (typeOf(a[sort_column]) == "string") {
                            return a[sort_column]?.localeCompare(b[sort_column]);
                        }
                        else {
                            return a[sort_column] - b[sort_column];
                        }
                      
                    }
                }
 
   
              
                let a_index = order_list.indexOf(a_value);
                let b_index = order_list.indexOf(b_value);
   
   
                // If both values are found in the 'order_list', sort by their index
                if (a_index !== -1 && b_index !== -1) {
                    return a_index - b_index;
                }
   
                // If both are not found, then sort by their value
                if (a_index == -1 && b_index == -1) {
                    return a_value.localeCompare(b_value);
                }
   
                if (a_index == -1) {
                    return 1;
                }
                if (b_index == -1) {
                    return -1;
                }
            });
        }


        let group_data = [];
        items.forEach( item => {
            let group_value = item[group_by];
            if (group_value != last_group_value) {
                let group_item = {
                    name: group_value,
                    column: group_by,
                    __type__: "group",
                    __background__: "#CCC",
                    __color__: "#000",
                }
                group_data.push(group_item)
            }
            group_data.push(item);
            last_group_value = group_value;
        } )


        return group_data;
    }

    // TODO
    const collapse_data = (data, collapse_by) => {
    }








    // TEST TEST TEST TEST - DEPRECATED

    function generate_pinned_data(params) {
        // generate a row-data with null values
        let result2 = {};
        let result = {
                "code": "TOTAL",
                "job_code": "Whatever",
                "login_group": "TOTAL",
                "group_name": "TOTAL",
                "role": "TOTAL",
                //"login": "TOTAL",
                "rate": 0,
                "days": 0,
                "booking_days": 0,
                "actual_days": 0,
                "budget": 0,
                "booking_budget": 0,
                "actual_budget": 0,
        }


        //params.columnApi.getAllGridColumns().forEach(item => {
        api.getAllGridColumns().forEach(item => {
            //result[item.colId] = null;
        });
        return calculatePinnedBottomData(result, params);
    }


    function calculatePinnedBottomData(target, params){
        let columnsWithAggregation = ['days', 'rate', 'booking_days', 'budget', 'booking_budget', 'actual_days', 'actual_cost']
        columnsWithAggregation.forEach(element => {
            params.api?.forEachNodeAfterFilter((rowNode) => {
                if (rowNode.data[element])
                    target[element] += Number(rowNode.data[element].toFixed(2));
            });
        })
        return target;
    }




    function generate_pinned_data2(params) {
        // generate a row-data with null values
        let result = {
            code: "TOTAL",
            initials: "TOTAL",
            groups: "TOTAL",
            work_hours: {}, // for work hours
        }

        let columns = [];
        //params.columnApi.getAllGridColumns().forEach(item => {
        api.getAllGridColumns().forEach(item => {
            //result[item.colId] = null;
            let column = item.colId;
            let parts = column.split("-");
            if (parts.length == 3) {
                columns.push(column);
            }
        });
        return calculatePinnedBottomData2(result, columns, params);
    }


    function calculatePinnedBottomData2(target, columns, params){
        let columnsWithAggregation = columns;
        columnsWithAggregation.forEach(element => {

            let total = 0;
            let count = 0;

            params.api?.forEachNodeAfterFilter((rowNode) => {
                let data = rowNode.data[element];
                if (!data && element != "budget") {
                    data = rowNode.data.work_hours[element];
                }
                if (data) {
                    let value = data[0].straight_time || 0;
                    //console.log(value);
                    if (value) {
                        try {
                            total += parseFloat(value);
                            count += 1;
                        } catch(e) {
                            console.log("WARNING: " + e);
                        }
                    }
                    //console.log("value: " + value , " == ", total);
                }
            });

            if (element == "budget") {
                target[element] = total;
            }
            else {
                target[element] = {
                    days: total,
                    type: "total",
                };

                // for work hours
                target["work_hours"][element] = [ {
                        straight_time: total,
                        type: "total"
                } ]
            }
        })


        return target;
    }



    const get_height = () => {
        //return props.auto_height ? "" : "calc(100vh - 250px)";

        if (props.auto_height) return "";

        let height = props.height;
        if (height) {
            return height;
        }
        else {
            return "calc(100vh - 250px)";
        }
    }





    return (
    <>
        <div style={{
            boxSizing: "border-box",
            margin: "10px 0px 0px 0px",
            width: "100%"
        }}>
            { grid_name &&
            <div id={grid_name} className="ag-theme-alpine"
                style={{
                    display: loading ? "none": "",
                    width: "100%",
                    height: get_height(),
                }}
            ></div>
            }
        </div>
    </>
    )

} );



//export { DataGrid };

// Store these
spt.react.DataGrid = DataGrid;



