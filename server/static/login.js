function updateButton(divID, em1, em2, changeID) {
    document.getElementById(divID).innerHTML = '';
    document.getElementById(em1).type = "password";
    document.getElementById(em1).setAttribute("required", "");
    document.getElementById(em2).type = "password";
    document.getElementById(em2).setAttribute("required", "");
    document.getElementById(changeID).name = "change";
}