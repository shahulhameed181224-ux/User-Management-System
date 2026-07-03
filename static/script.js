const API = "http://127.0.0.1:8000";

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

        updated_by: ""

    };

    const response = await fetch(API + "/tenants",{

        method:"POST",

        headers:{
            "Content-Type":"application/json"
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

    const response = await fetch(API + "/tenants");

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