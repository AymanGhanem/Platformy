var vmix_toggle = document.getElementById("vmix_toggle");
var vmix_connect = document.getElementById("vmix_connect");
var vmix_state = document.getElementById("vmix_state");
var vmix_copy_password = document.getElementById("vmix_copy_password");
var vmix_instance_id = "";
var vmix_instance_password = "";
var vmix_instance_filepath = "";


async function launchEC2(){
    const response = await fetch("http://localhost:8000/api/launch/",{
            method: "POST",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Connection': 'keep-alive'
            },
            body: JSON.stringify({
            region_name: "us-east-2",
            ImageId: "ami-0428fc1ee1bde045a",
            MinCount: 1,
            MaxCount: 1,
            InstanceType: "g4dn.2xlarge",
            KeyName: "key-pair",
            SecurityGroupIds: ['sg-0c9b920bc07a3d138'],
        })
        });
    const data = await response.json();
    return data;
}

async function connectEC2(){
    const response = await fetch("http://localhost:8000/api/connect/",{
            method: "POST",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Connection': 'keep-alive'
            },
            body: JSON.stringify({
            region_name: "us-east-2",
            InstanceId: vmix_instance_id,
            private_key_file: "api/tmp/aws_ec2_key.pem"
        })
    });
    const data = await response.json();
    return data;
}

async function downloadFile(url){
    const file = await fetch("http://localhost:8000/api/download/",{
        method: "POST",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Connection': 'keep-alive'
            },
            body: JSON.stringify({
            filepath: vmix_instance_filepath,
        })
    });

    const fileBlob = await file.blob();
    const file_url = URL.createObjectURL(fileBlob);

    const anchor = document.createElement("a");
    anchor.href = file_url;
    anchor.download = "download.rdp";

    document.body.appendChild(anchor);
    anchor.click();
    document.body.removeChild(anchor);

    URL.revokeObjectURL(file_url);
}


async function stopEC2(){
    const response = await fetch("http://localhost:8000/api/stop/",{
            method: "POST",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Connection': 'keep-alive'
            },
            body: JSON.stringify({
            region_name: "us-east-2",
            InstanceId: vmix_instance_id
        })
        });
    const data = await response.json();
    return data;
}

async function terminateEC2(){
    const response = await fetch("http://localhost:8000/api/terminate/",{
            method: "POST",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Connection': 'keep-alive'
            },
            body: JSON.stringify({
            region_name: "us-east-2",
            InstanceId: vmix_instance_id
        })
        });
    const data = await response.json();
    return data;
}

vmix_toggle.addEventListener("click", async function(event){
    event.preventDefault();
    if(vmix_toggle.innerHTML.trim() === 'Start'){
        vmix_state.innerHTML = "Launching";
        vmix_state.className = "badge rounded-pill bg-dark text-warning";
        vmix_toggle.style.visibility = "hidden";
        const res = await launchEC2();
        data = JSON.stringify(res);
        json_data = JSON.parse(data);
        vmix_instance_id = json_data["InstanceId"];
        const connection_info = await connectEC2();
        connection_data = JSON.stringify(connection_info);
        console.log(connection_data);
        connection_json = JSON.parse(connection_data);
        vmix_instance_password = connection_json["plain_password"];
        vmix_instance_filepath = connection_json["filepath"];
        console.log("Pass ---------> ", vmix_instance_password);
        vmix_state.innerHTML = "Running the instance of id : " + json_data["InstanceId"] ;
        vmix_state.className = "badge rounded-pill bg-dark text-success";
        vmix_toggle.innerHTML = "Stop"
        vmix_toggle.className = "btn btn-danger";
        vmix_toggle.style.visibility = "visible";
        vmix_connect.style.visibility = "visible";
        alert("Your password is : " + vmix_instance_password);
    }else if(vmix_toggle.innerHTML.trim() === 'Stop'){
        vmix_instance_password = "";
        vmix_instance_filepath = "";
        vmix_state.innerHTML = "Stopping";
        vmix_state.className = "badge rounded-pill bg-dark text-danger";
        vmix_toggle.style.visibility = "hidden";
        vmix_connect.style.visibility = "hidden";
        let res = await stopEC2();
        data = JSON.stringify(res);
        json_data = JSON.parse(data);
        vmix_state.innerHTML = "Terminating" ;
        vmix_state.className = "badge rounded-pill bg-dark text-success";
        vmix_toggle.innerHTML = "Start"
        vmix_toggle.className = "btn btn-info";
        vmix_toggle.style.visibility = "visible";
        res = await terminateEC2();
        data = JSON.stringify(res);
        vmix_state.innerHTML = "Terminated" ;
        vmix_state.className = "badge rounded-pill bg-dark text-info";
    }
});

vmix_connect.addEventListener("click", async function(event){
    event.preventDefault();
    if(vmix_connect.innerHTML.trim() === 'Connect'){
        const res = await downloadFile(vmix_instance_filepath);
    }
});