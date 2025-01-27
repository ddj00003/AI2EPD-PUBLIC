autoReloadActive = true;
reload = setTimeout(function(){
    console.log("entra");
    location.reload();
}, 6000);

//Crea una fucnión para activar y desactivar la recarga autómatica mediante tiomeout
//Añade que se cambie el tesxto del botón al activar o desactivar la recarga
function autoReload(){
    if(autoReloadActive){
        clearTimeout(reload);
        autoReloadActive = false;
        document.getElementById("btnAutoReload").innerHTML = "Activar recarga automática";
    }else{
        autoReloadActive = true;
        document.getElementById("btnAutoReload").innerHTML = "Desactivar recarga automática";
        reload = setTimeout(function(){
            location.reload();
        }, 6000);
    }
}