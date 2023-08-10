
document.getElementById("player3").style.visibility = "hidden";
document.getElementById("player4").style.visibility = "hidden";
document.getElementById("player5").style.visibility = "hidden";
document.getElementById("player6").style.visibility = "hidden";
document.getElementById("player7").style.visibility = "hidden";
document.getElementById("player8").style.visibility = "hidden";


function player(p1, p2) {
    let pOne = document.getElementById(p1);
    let pTwo = document.getElementById(p2);
    if (pOne.value != "") {
        pTwo.style.visibility = "visible";
    }
    else {
        pTwo.style.visibility = "hidden";
    }
}