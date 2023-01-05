var HOST_URL = "http://localhost:8000";


async function clickSignup(event){
    event.preventDefault();
    let email = document.getElementById('email').value ;
    let password1 = document.getElementById('pass').value;
    let password2 = document.getElementById('re_pass').value;
    const response = await fetch(HOST_URL + "/api/register/",{
            method: "POST",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Connection': 'keep-alive'
            },
            body: JSON.stringify({
                'email':email,
                'password1':password1,
                'password2':password2
            })
        });
    if((String(response.status)[0] != "4") & (String(response.status)[0] != "5") )
    {
        const data = await response.json();
        console.log(data);
        const anchor = document.createElement("a");
        anchor.href = "https://www.google.com/";

        document.body.appendChild(anchor);
        anchor.click();
        document.body.removeChild(anchor);
    }else{
        const data = await response.json();
        console.log("Error part of clickLogin");
        if(data.non_field_errors != undefined){
            alert(data.non_field_errors)
            if(data.email != undefined)
            {
                alert("email: " + data.email);
            }
            if(data.password1 != undefined)
            {
                alert("password: " + data.password1);
            }
        }else{
            if(data.email != undefined)
            {
                alert("email: " + data.email);
            }
            if(data.password1 != undefined)
            {
                alert("password: " + data.password1);
            }
            alert("Something went wrong!\nCheck the inputed credentials please.");
        }
    }
}

async function clickLogin(event){
    event.preventDefault();
    let email = document.getElementById('email').value ;
    let password = document.getElementById('your_pass').value;
    const response = await fetch(HOST_URL + "/api/login/",{
            method: "POST",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Connection': 'keep-alive'
            },
            body: JSON.stringify({
                'email':email,
                'password':password
            })
        });
    if(response.status == "200")
    {
        const data = await response.json();
        console.log(data)

        const anchor = document.createElement("a");
        anchor.href = HOST_URL + "/api/page/home";

        document.body.appendChild(anchor);
        anchor.click();
        document.body.removeChild(anchor);
    }else
    {
        const data = await response.json();
        console.log("Error part of clickLogin");
        if(data.non_field_errors != undefined){
            alert(data.non_field_errors)
            if(data.email != undefined)
            {
                alert("email: " + data.email);
            }
            if(data.password != undefined)
            {
                alert("password: " + data.password);
            }
        }else{
            if(data.email != undefined)
            {
                alert("email: " + data.email);
            }
            if(data.password != undefined)
            {
                alert("password: " + data.password);
            }
            alert("Something went wrong!\nCheck the inputed credentials please.");
        }
    }
}

async function clickLogout(event){
    event.preventDefault();
    const response = await fetch(HOST_URL + "/api/logout/",{
            method: "POST",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Connection': 'keep-alive'
            },
            body: JSON.stringify({})
        });
    if(response.status == "200"){
        const data = await response.json();
        console.log(data)

        const anchor = document.createElement("a");
        anchor.href = HOST_URL + "/api/page/login";

        document.body.appendChild(anchor);
        anchor.click();
        document.body.removeChild(anchor);
    }else{
        const data = await response.json();
        console.log("Error Part of clickLogout");
        alert(data.non_field_errors);
    }
}


async function start(event){
    // Prevent refreshing the page
    event.preventDefault();

    // Getting the needed elements
    let element = event.path[0];
    let application_id = event.path[0].getAttribute("value");
    let state = document.getElementById("state-" + application_id);
    let connect = document.getElementById("connect-"+application_id);

    // Convert to stop state
    element.setAttribute("class", "btn btn-danger");
    element.text = "Stop";
    element.setAttribute("onclick", "return false;");
    state.setAttribute("class", "badge rounded-pill bg-dark Pending");
    state.innerHTML = "Pending";
    connect.setAttribute('style', 'visibility: display');
    console.log("start - Application id is " + application_id );

    // Start the application
    const response = await fetch(HOST_URL + "/api/start-application/",{
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Connection': 'keep-alive'
        },
        body: JSON.stringify({
            'application_id': application_id
        })
    });

    if(response.status != "200"){
        element.setAttribute("class", "btn btn-primary");
        element.setAttribute("onclick", "start(event)");
        element.text = "Start";
        state.setAttribute("class", "badge rounded-pill bg-dark Available");
        state.innerHTML = "Available";
        connect.setAttribute('style', 'visibility: hidden');
    }

    if(response.status == "200"){
        element.setAttribute("onclick", "stop(event)");
        state.setAttribute("class", "badge rounded-pill bg-dark Running");
        state.innerHTML = "Running";
    }
}

async function stop(event){
    event.preventDefault();
    let element = event.path[0];
    let application_id = event.path[0].getAttribute("value");
    let connect = document.getElementById("connect-"+application_id);
    let state = document.getElementById("state-" + application_id);
    element.setAttribute("class", "btn btn-primary");
    element.setAttribute("onclick", "return false");
    element.text = "Start";
    state.setAttribute("class", "badge rounded-pill bg-dark Stopping");
    state.innerHTML = "Stopping";
    connect.setAttribute('style', 'visibility: hidden');
    console.log("stop - Application id is " + application_id );
    // Stop the application
    const response = await fetch(HOST_URL + "/api/stop-application/",{
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Connection': 'keep-alive'
        },
        body: JSON.stringify({
            'application_id': application_id
        })
    });

    if(response.status != "200"){
        element.setAttribute("class", "btn btn-danger");
        element.setAttribute("onclick", "stop(event)");
        element.text = "Stop";
        state.setAttribute("class", "badge rounded-pill bg-dark Running");
        state.innerHTML = "Running";
        connect.setAttribute('style', 'visibility: display');
    }

    if(response.status == "200"){
        element.setAttribute("onclick", "start(event)");
        state.setAttribute("class", "badge rounded-pill bg-dark Available");
        state.innerHTML = "Available";
    }
}

async function connect(event){
    event.preventDefault();
    let application_id = event.path[0].getAttribute("value");
    const file = await fetch("http://localhost:8000/api/connect-application/",{
        method: "POST",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Connection': 'keep-alive'
            },
            body: JSON.stringify({
            application_id: application_id,
        })
    });


    if(file.status != "200"){
        console.log(response);
    }

    alert("Your Password " +  file.headers.get('password'));
    if(file.status == "200"){
        const fileBlob = await file.blob();
        const file_url = URL.createObjectURL(fileBlob);

        const anchor = document.createElement("a");
        anchor.href = file_url;
        anchor.download = ''+file.headers.get('instance_id')+'.rdp';

        document.body.appendChild(anchor);
        anchor.click();
        document.body.removeChild(anchor);

        URL.revokeObjectURL(file_url);
        console.log("connect - Application id is " + application_id );
    }
}