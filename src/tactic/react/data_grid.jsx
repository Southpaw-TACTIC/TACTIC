/*
import { useState } from "react";
import { useEffect } from "react";
import { useReducer } from 'react';
import { useRef } from 'react';
*/
let useEffect = React.useEffect;
let useState = React.useState;



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
        export_csv() {
            export_csv();
        }
    }))

    const [loading, set_loading] = useState(true);
    const [api, set_api] = useState(null);

    const [grid_name, set_grid_name] = useState(null);
    const [grid_options, set_grid_options] = useState(null);

    const [onselect, set_onselect] = useState(null);

    const [data, set_data] = useState([]);




    const add_filter = filter => {
        grid_options.api.setQuickFilter(filter);
    }



    const get_filter = (column) => {
        let api = grid_options.api;

        // Get a reference to the filter instance
        const filterInstance = api.getFilterInstance(column);
        let model = filterInstance.getModel();
        return model;
    }


    const set_filter = (column, options) => {

        let api = grid_options.api;

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
        grid_options.api.selectAll();
    }

    const unselect_all = () => {
        grid_options.api.deselectAll();
    }

    const get_selected_nodes = () => {
        return grid_options.api.getSelectedNodes();
    }
    const get_selected_rows = () => {
        return grid_options.api.getSelectedRows();
    }

    const get_filtered_nodes = () => {
        let all_nodes = [];
        grid_options.api.forEachNodeAfterFilter((rowNode) => all_nodes.push(rowNode));
        return all_nodes;
    }

    const get_filtered_rows = () => {
        let all_rows = [];
        grid_options.api.forEachNodeAfterFilter((rowNode) => all_rows.push(rowNode.data));
        return all_rows;
    }

    const get_columns = () => {
        let columns = [];
        grid_options.columnApi.getAllGridColumns().forEach(item => {
            let column = item.colId;
            columns.push(column);
        } )
        return columns;
    }

    const export_csv = () => {
        let params = {
            processCellCallback: (cell) => {
                return cell.value;
            }
        };
        grid_options.api.exportDataAsCsv(params);
    }

    const redrawRows = (nodes) => {
        setTimeout( () => {
            grid_options.api.redrawRows({
                nodes: nodes,
                force: true,
                suppressFlash: true
            });
        }, 0 );
    }

    const refresh_cells = (nodes) => {
        setTimeout( () => {
            //grid_options.api.redrawRows({
            grid_options.api.refreshCells({
                nodes: nodes,
                force: true,
                suppressFlash: true
            });
        }, 0 );
    }


    // Function to demonstrate calling grid's API
    const deselect = () => {
        grid_options.api.deselectAll()
    }



    const on_selection_changed = () => {
        let api = grid_options.api;

        let selectedRows = api.getSelectedRows();
        let selectedNodes = api.getSelectedNodes();

        let onselect = props.onselect;
        if (!onselect) return;

        onselect(selectedRows, selectedNodes);
    }



    const clear_filters = () => {
        let api = grid_options.api;
        api.setFilterModel(null);
    }




    // TEST TEST
    const _show_total = (params) => {
        if (!props.show_total && !props.get_total_data) return;

        let pinned;
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
            params.columnApi.getAllGridColumns().forEach(item => {
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


        // Grid Options are properties passed to the grid
        const gridOptions = {

          // each entry here represents one column
          columnDefs: props.column_defs,

          // default col def properties get applied to all columns
          defaultColDef: {sortable: true, filter: true},

          rowSelection: 'multiple', // allow rows to be selected
          animateRows: true, // have rows animate to new positions when sorted

          //paginationAutoPageSize: true,
          pagination: props.auto_height ? false : true,

          //overlayNoRowsTemplate: "Whatever",

          onGridReady: on_grid_ready,
          onFilterChanged: on_filter_changed,
          onCellClicked: on_cell_clicked,

          singleClickEdit: props.single_click == true ? true : false,
          suppressClickEdit: props.suppress_click == true ? true : false,
          suppressRowClickSelection: true,

          // while this is the behvaior we want, it does not behave well with selects
          //stopEditingWhenCellsLoseFocus: true,
        
          headerHeight: "25px",
          groupHeaderHeight: "20px"

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
        let grid = new agGrid.Grid(eGridDiv, grid_options);


        // Stop editing when click on anything
        eGridDiv.addEventListener( "blur", e => {
            grid_options.api.stopEditing();
        } )
 

        if (props.column_defs) {
            grid_options.api.setColumnDefs(props.column_defs);
        }


        if (props.data != data) {
            grid_options.api.setRowData(props.data);
            set_data(props.data);
        }

        if (props.get_row_style) {
            grid_options["getRowStyle"] = props.get_row_style;
        }



    }, [grid_name, grid_options] );



    useEffect( () => {

        if (!grid_options) {
            return;
        }


        if (props.column_defs) {
            grid_options.api.setColumnDefs(props.column_defs);
        }
        //this might not be neseccary
        if (props.get_row_style) {
            grid_options["getRowStyle"] = props.get_row_style;
        }


        if (props.data) {
            grid_options.api.setRowData(props.data);
        }


    }, [props] )




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


        params.columnApi.getAllGridColumns().forEach(item => {
            //result[item.colId] = null;
        });
        return calculatePinnedBottomData(result, params);
    }


    function calculatePinnedBottomData(target, params){
        let columnsWithAggregation = ['days', 'rate', 'booking_days', 'budget', 'booking_budget', 'actual_days', 'actual_cost']
        columnsWithAggregation.forEach(element => {
            params.api.forEachNodeAfterFilter((rowNode) => {
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
        params.columnApi.getAllGridColumns().forEach(item => {
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

            params.api.forEachNodeAfterFilter((rowNode) => {
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






    return (
    <>
        <div style={{boxSizing: "border-box", margin: "10px 0px 0px 0px", width: "100%"}}>
            { grid_name &&
            <div id={grid_name} className="ag-theme-alpine"
                style={{
                    display: loading ? "none": "",
                    width: "100%",
                    height: props.auto_height ? "" : "calc(100vh - 250px)",
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



