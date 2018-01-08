

function getDimmerSettings() {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {

            var data = JSON.parse(xmlHttp.responseText)
            console.log(data)

            for (pid in data['dimmer0']) {
                console.log("PID:" + pid)
                for (component in data['dimmer0'][pid]) {
                    elementName = 'dimmer0.' + pid + "." + component;
                    console.log(elementName, data['dimmer0'][pid][component]);
                    docElement = document.getElementById(elementName);
                    if (docElement != null) {
                        docElement.value = data['dimmer0'][pid][component];
                        docElement.textContent = data['dimmer0'][pid][component];
                    } else {
                        console.log("Couldn't find element "+elementName);
                    }
                }
            }

            // for (x in data) {
            //     element = document.getElementById(x);
            //     if (element != null) {
            //         element.value = data[x];
            //     }
            // }

        }
    }
    xmlHttp.open("GET", "/dimmer/settings", true); // true for asynchronous 
    xmlHttp.send(null);
}


function setDimmerSettings( button ){
    var formData = new FormData();
    for (x in button.parentElement.elements) {
        if (button.parentElement.elements[x].id != null && button.parentElement.elements[x].id != '') {
            formData.append(
                button.parentElement.elements[x].id,
                button.parentElement.elements[x].value);
        }
    }
    console.log(formData)
    var request = new XMLHttpRequest();
    request.open("POST", "/dimmer/settings");
    request.send(formData);
}