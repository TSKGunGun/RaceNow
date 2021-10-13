var frm_memberadd = new bootstrap.Modal(document.getElementById('MemberAddModal'));
var btn_showModal = document.querySelector("#btn_showmemberaddModal");
document.querySelector('#MemberAddModal').addEventListener("show.bs.modal", function(event){
    if (!(canAddMember())) {
        alert("メンバー数の上限を超えて追加することはできません。");
        event.preventDefault();
    }
})

document.querySelector('#MemberAddModal').addEventListener("submit", function(event){
    var membername = document.querySelector('#addmember_name').value;

    var targettable = document.querySelector('#members_info');
    var addrow = targettable.insertRow();
    addrow.insertCell().appendChild(document.createTextNode(membername));
    addrow.insertCell().appendChild(document.createTextNode(""));

    var ele_input_members = document.querySelector('#id_members');
    var memberdata = {};
    if ( ele_input_members.value != "") { 
        memberdata = JSON.parse(ele_input_members.value); 
    }

    memberdata[Object.keys(memberdata).length] = {"name":membername };
    ele_input_members.value = JSON.stringify(memberdata);

    document.querySelector('#addmember_name').value = "";

    frm_memberadd.hide();

    if(!(canAddMember())){
        btn_showModal.disabled = true;
    }
})

window.addEventListener('load', function(event){
    var ele_input_members = document.querySelector('#id_members');
    if ( ele_input_members.value != "") { 
        memberdata = JSON.parse(ele_input_members.value); 

        var targettable = document.querySelector('#members_info');
        Object.values(memberdata).map(
            val => {
                var addrow = targettable.insertRow();
                addrow.insertCell().appendChild(document.createTextNode(val["name"]));
                addrow.insertCell().appendChild(document.createTextNode(""));
            }
        )
        
        if(!(canAddMember())){btn_showModal.disabled = true;}
    }
})

function canAddMember(){
    var targettable = document.querySelector('#members_info');
    var count = targettable.rows.length - 1;
    return member_max > count ;
}