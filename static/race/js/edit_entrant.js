var frm_memberadd = new bootstrap.Modal(document.getElementById('MemberAddModal'));
var btn_showModal = document.querySelector("#btn_showmemberaddModal");
var membersTable = document.querySelector('#members_info');
var membersTable_Default = membersTable.innerHTML;

document.querySelector('#MemberAddModal').addEventListener("show.bs.modal", function(event){
    if (!(canAddMember())) {
        alert("メンバー数の上限を超えて追加することはできません。");
        event.preventDefault();
    }
})

document.querySelector('#MemberAddModal').addEventListener("submit", function(event){
    var membername = document.querySelector('#addmember_name').value;
    add_member(membername)
    document.querySelector('#addmember_name').value = "";
    draw_members();

    frm_memberadd.hide();
})

window.addEventListener('load', function(event){
    draw_members();
})

function draw_members(){
    clear_members();

    var ele_input_members = document.querySelector('#id_members');
    if ( ele_input_members.value != "") { 
        memberdata = JSON.parse(ele_input_members.value); 

        Object.keys(memberdata).map(
            key => {
                var addrow = membersTable.insertRow();
                
                var tdname = addrow.insertCell()
                tdname.classList.add("text-center");
                tdname.appendChild(document.createTextNode(memberdata[key]["name"]));
                addrow.insertCell().appendChild(document.createTextNode(""));
                
                var actionNode = document.createElement("div");
                actionNode.classList.add("d-flex", "justify-content-center");
                
                var btn_deleteMember = document.createElement("button");
                btn_deleteMember.classList.add("btn", "btn-danger")
                btn_deleteMember.innerText="削除";
                btn_deleteMember.setAttribute("type", "button");
                btn_deleteMember.setAttribute("onclick", "onclick_DeleteMemberBtn(event)")
                btn_deleteMember.setAttribute("data-id", key)

                actionNode.appendChild(btn_deleteMember);
                
                addrow.insertCell().appendChild(actionNode);
            }
        )
        btn_showModal.disabled = !(canAddMember());
    }
}

function clear_members(){
    membersTable.innerHTML = membersTable_Default;
}

function add_member(member_name){
    var ele_input_members = document.querySelector('#id_members');
    var memberdata = {};
    if ( ele_input_members.value != "") { 
        memberdata = JSON.parse(ele_input_members.value); 
    }
    
    memberdata[Object.keys(memberdata).length] = {"name":member_name };
    ele_input_members.value = JSON.stringify(memberdata);
}

function delete_member(id){
    var ele_input_members = document.querySelector('#id_members');
    var memberdata = {};
    if ( ele_input_members.value == "") { 
        alert("メンバー管理でエラーが発生しました。");
        return 0;
    }
    
    memberdata = JSON.parse(ele_input_members.value); 

    var newMemberData = {};
    Object.keys(memberdata).map ( 
        key => {
            if(key != id) {
                newMemberData[Object.keys(newMemberData).length] = {"name":memberdata[key]["name"] };                  
            }
    })
    ele_input_members.value = JSON.stringify(newMemberData);
}

function canAddMember(){
    var targettable = document.querySelector('#members_info');
    var count = targettable.rows.length - 1;
    return member_max > count ;
}

function onclick_DeleteMemberBtn(event){
    var id = event.target.dataset.id;
    delete_member(id);
    draw_members();
}