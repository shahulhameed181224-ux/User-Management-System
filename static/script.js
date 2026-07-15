const API = "http://127.0.0.1:8000";

const token = localStorage.getItem("access_token");

if(!token){
    window.location.href = "/login";
}

document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("tenantForm");

    if(form){

        form.addEventListener("submit", createTenant);

        loadTenants();

    }

});


async function createTenant(event){

    event.preventDefault();

    const data = {

        tenant_name: document.getElementById("tenant_name").value,

        tenant_type: document.getElementById("tenant_type").value,

        created_by: document.getElementById("created_by").value,

        updated_by: document.getElementById("updated_by").value

    };

    const response = await fetch(API + "/tenants",{

        method:"POST",

        headers:{
            "Content-Type":"application/json",
            "Authorization": "Bearer " + token
        },

        body:JSON.stringify(data)

    });

    if(response.ok){

        alert("Tenant Created Successfully");

        document.getElementById("tenantForm").reset();

        loadTenants();

    }
    else{

        alert("Failed to Create Tenant");

    }

}


async function loadTenants(){

    const response = await fetch(API + "/tenants",{

        headers:{
            "Authorization": "Bearer " + token
        }

    });

    const tenants = await response.json();

    const tbody = document.querySelector("#tenantTable tbody");

    tbody.innerHTML="";

    tenants.forEach(t=>{

        tbody.innerHTML += `

        <tr>

        <td>${t.id}</td>

        <td>${t.tenant_name}</td>

        <td>${t.tenant_type}</td>

        <td>${t.created_by}</td>

        <td>${t.created_at}</td>

        </tr>

        `;

    });

}

// Logout Function
function logout(){

    localStorage.removeItem("access_token");
    window.location.href = "/login";
}