
/* TACTIC */
const useEffect = React.useEffect;
const useState = React.useState;
const useRef = React.useRef;
const useReducer = React.useReducer;
const useCallback = React.useCallback;

const Box = MaterialUI.Box;
const TextField = MaterialUI.TextField;
const Modal = MaterialUI.Modal;
const Button = MaterialUI.Button;
const IconButton = MaterialUI.IconButton;
const FormControl = MaterialUI.FormControl;
const Menu = MaterialUI.Menu;
const MenuItem = MaterialUI.MenuItem;
const Select = MaterialUI.Select;
const Chip = MaterialUI.Chip;
const Switch = MaterialUI.Switch;
const LinearProgress = MaterialUI.LinearProgress;
const Checkbox = MaterialUI.Checkbox;

const Pages = React.forwardRef((props, ref) => {

    React.useImperativeHandle( ref, () => ({
        next() {
            return next();
        },
    } ) )



    const [ignored, forceUpdate] = useReducer(x => x + 1, 0);

    const [current_page, set_current_page] = useState(0);
    const [last_page, set_last_page] = useState(0);
    const [pages, set_pages] = useState([]);
    const [pages_dict, set_pages_dict] = useState({});

    const [is_validated, set_is_validated] = useState(true);
    const [show_buttons, set_show_buttons] = useState(true);

    /*
    const [sobject, set_sobject] = useState( {
        name: "The Big Job",
        start_date: "2014-02-02",
        nationality: "Netherlands",
        is_felon: "yes",
        age: 23,
        email: "foo@foo.com",
        transaction_frequency: "monthly",
    } )
    */
    const [sobject, set_sobject] = useState( {} );


    const get_default_header = () => {
        return (
            <div style={{
                height: "50px",
                borderBottom: "solid 5px darkblue",
                fontSize: "1.2rem",
            }}
            >Page: { current_page }</div>
        )
    }
    const [header, set_header] = useState(get_default_header());
 
    const edit_ref = useRef();
    const pages_ref = useRef();


    useEffect( () => {
        init();
    }, [] )


    const Content = props.content || spt.react.SimplePages;

    const init = async () => {

        if (!pages_ref.current) {
            setTimeout( () => {
                init();
            }, 250 );
            return;
        }

        let pages = pages_ref.current.get_pages();

        // set the pages
        await set_pages(pages);

        if (pages_ref.current.get_header) {
            let header = pages_ref.current.get_header();
            set_header(header);
        }


        let pages_dict = {};
        let index = 0;
        pages.forEach( page => {
            if (page.name) {
                pages_dict[page.name] = index;
            }
            index += 1;
        } )
        set_pages_dict(pages_dict)


        let current_page = props.page || 0;
        await set_current_page(current_page);

        // init the first pages
        let first_page = pages[current_page];
        if (first_page?.onload) {
            first_page.onload();
        }

    }




    const get_current_page = () => {
        let page = pages[current_page];
        if (!page) return null;

        let el = page.widget || page;
        if (typeof(el) == "function") {
            el = page.widget()
        }

        return (
            <div>{el}</div>
        )
    }


    const prev_page = useCallback( () => {

        if (current_page == 0) return;
        if (last_page) {
            set_current_page(last_page);
        }
        else {
            set_current_page(current_page - 1);
        }
        set_last_page(0);


    }, [current_page, last_page, sobject] );


    const next_page = useCallback( async () => {

        let pages = pages_ref.current.get_pages();

        let page = pages[current_page];
        if (!page) {
            alert("Cannot find page ["+current_page+"]");
            return;
        }

        if (!validate_page()) {
            //alert("Error");
            return;
        }


        if (page.oncomplete) {
            try {
                let ret = await page.oncomplete({})
            }
            catch(e) {
                alert("ERROR creating CIF: " + e);
                return;
            }
        }

        // Go to the next page
        let next_index;
        if (page.next) {
            let next_name = page.next(sobject);
            if ( typeOf(next_name) == "number") {
                next_index = current_page + next_name;
            }
            else {
                next_index = pages_dict[next_name];
            }
            if (!next_index) {
                alert("ERROR: cannot find ["+next_name+"]");
                return;
            }
        }
        else {
            next_index = current_page + 1;
        }
        set_last_page(current_page);
        set_current_page(next_index);
        set_show_buttons(true);

        let new_page = pages[next_index];
        if (new_page?.onload) {
            new_page.onload();
        }


    }, [pages, sobject, current_page] );




    const validate_page = () => {
        let form_validated = true;

        if (edit_ref.current) {
            form_validated = edit_ref.current.validate();
        }

        let config = edit_ref.current?.get_config();
        if (config) {
            let sobject = edit_ref.current.get_sobject();
            config.forEach( item => {
                if (item.required == true) {
                    let key = item.column || item.name;
                    if (!sobject[key]) {
                        form_validated = false;
                    }
                }
            } )
        }

        //set_is_validated(form_validated);

        return form_validated


    }


    const get_buttons = () => {
        let page = pages[current_page];
        if (!page) return null;

        if (!is_validated) return null;

        return (
            <div 
                style={{
                    display: "flex", justifyContent: "space-around", gap: "30px",
                        margin: "20px 0px 20px 0px"

            }}>
                <Button variant="outlined"
                    disabled={ current_page == 0 ? true : false}
                    onClick={ e => {
                        prev_page();
                        return;
                    }}
                >Back</Button>
                <Button variant="contained"
                    onClick={ e => {
                        next_page();
                    }}
                >Next</Button>
            </div>
        )
    }



    let width = props.width || "600px";

    return (
        <div style={{
            width: width,
            background: "#FFF",
            border: "solid 1px #DDD",
            boxShadow: "0px 0px 15px rgba(0,0,0,0.1)",
            padding: "0px 15px",
            margin: "20px auto",
        }}>

            { Content &&
            <Content
                ref={pages_ref}
                edit_ref={edit_ref}
                sobject={sobject}
                set_show_buttons={set_show_buttons}
                next_page={next_page}
                current_index={current_page}
            /> }


            { header != null && header }

            <div style={{
                margin: "10px",
                height: "500px",
                maxHeight: "500px",
                minHeight: "500px",
                overflowY: "auto",

            }}>


                { get_current_page() }



            </div>

            { show_buttons && get_buttons() }

        </div>
    )

} )




spt.react.Pages = Pages;

