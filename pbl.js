const table = document.getElementById("table");
const td_status = document.getElementById("td_status");
const socket = io();

function socket_to_table(){
    let xhr = new XMLHttpRequest();
    xhr.open("GET", "./output.json");
    xhr.send();
    xhr.onreadystatechange = function(){
        if(xhr.readyState == 4 && xhr.status == 200){
            let json = JSON.parse(xhr.responseText);
            td_status.innerHTML = json.status;
            switch (json.status){
                case "running":
                    td_status.style.backgroundColor = "#00FF00";
                    break;

                case "stopped":
                    td_status.style.color = "#ff0000";
                    break;
            }
            table.innerHTML = ``;
            for(i = 0; i < json.details.length; i++){
                let td_data = document.createElement("td");
                td_data.style.width = "100px";
                td_data.innerHTML = "Data " + (i + 1);

                let td_value = document.createElement("td");
                td_value.innerHTML = json.details[i].value;

                let td_data_status = document.createElement("td");
                td_data_status.innerHTML = json.details[i].status;

                switch (json.details[i].status){
                    case "Defective":
                        let color = "#FF0033";
                        td_data.style.backgroundColor = color;
                        td_value.style.backgroundColor = color;
                        td_data_status.style.backgroundColor = color;
                        break;
                }

                let tr = document.createElement("tr");
                tr.appendChild(td_data);
                tr.appendChild(td_value);
                tr.appendChild(td_data_status);
                table.prepend(tr);
            }
        }
    }
}

socket.on("first_send", function(){
    socket_to_table();
});

socket.on("send_json", function(){
    socket_to_table();
});