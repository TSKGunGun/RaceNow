var activeRow = -1;
var select_entId = -1;
var resultTable = document.querySelector("#result_data");
var num_selector = document.querySelector('#id_num');
var lapmodal = document.querySelector('#LapModal')
Array.from(resultTable.getElementsByTagName("tr")).forEach(element => {
    element.addEventListener('click', function(event){
        if(activeRow > 0){
            resultTable.rows[activeRow].classList.remove("bg-info");
        }
        if(element.rowIndex == 0 ) {
            activeRow = -1;
            select_entId = -1;
        } else {
            activeRow = element.rowIndex;
            select_entId = element.cells[0].innerText;
            element.classList.add("bg-info");
        }
    })    
});

document.querySelector("#LapModal").addEventListener('show.bs.modal', function(event){
    clean_entrant_data();
    if(select_entId > 0) {
        Array.from(num_selector.getElementsByTagName('option')).forEach(element=>{
            if( element.value == select_entId ){
                element.selected = true;
            }
        })
        get_entrant_info(select_entId, set_entrant_data);
    }
})

num_selector.addEventListener('change', function(event){
    var entrant_id = num_selector.selectedOptions[0].value;
    if ( entrant_id > 0 ) { 
        get_entrant_info(entrant_id, set_entrant_data);
    }
})

function set_entrant_data(ent_data){
    document.querySelector('#entrant_info_team_name').cells[1].innerText = ent_data["team_name"];

    document.querySelector('#entrant_info_team_member').cells[1].innerText = ent_data["member"].join('/');

    var lapTable = document.querySelector('#entrant_laps');
    while(lapTable.rows.length > 1){
        lapTable.rows[lapTable.rows.length-1].remove();
    }

    Object.keys(ent_data["laps"]).sort( (a,b) =>{
        if( Number(a) > Number(b) ) return -1;
        if( Number(a) < Number(b) ) return 1;
        return 0;
    }).forEach( key =>{
        var addRow = lapTable.insertRow();
        var lap = ent_data["laps"][key];
        var countcell = addRow.insertCell()
        countcell.classList.add("text-center")
        countcell.appendChild(document.createTextNode(key));
        addRow.insertCell().appendChild(document.createTextNode(lap["input_time"]));
    })
}

function clean_entrant_data(){
    num_selector.selectedIndex = 0;
    document.querySelector('#entrant_info_team_name').cells[1].innerText = ""
    document.querySelector('#entrant_info_team_member').cells[1].innerText = "";
    var lapTable = document.querySelector('#entrant_laps');
    while(lapTable.rows.length > 1){
        lapTable.rows[lapTable.rows.length-1].remove();
    } 
}

function get_entrant_info(entrant_id, callbackfunc){
    var uri = '/race/entrants/' + entrant_id + '/getinfo';
    fetch(uri)
    .then( response => response.json() 
    )
    .then( data =>{callbackfunc(data);
    }); 
}