
 function show(){
    const container = document.getElementById('notification-container');
    if (container.classList.contains('d-none')){
        container.classList.remove('d-none');
    }else{
        container.classList.add('d-none')
    }
}
function formatTags() {
    var elements = document.getElementsByClassName('body');
    let new_element=""
    for (let i = 0; i < elements.length; i++) {
        let bodyText = elements[i].children[0].innerText;
        let words = bodyText.split(' ');

        for (let j = 0; j < words.length; j++) {
            if (words[j][0] === '#') {
              replaced='<a href=/yakoi/évènement/explorer?query='+words[j].substring(1)+'>'+words[j]+'</a>'
              words[j]=replaced          
              
            }         
            new_element= new_element + " "+words[j]            
        }
        elements[i].innerHTML = new_element             
    }

}

function tagger(){
  
    listes=[]
    liste= document.getElementsByName('tagger');
  
    for(let i=1;i<=liste.length;i++){
        listes[i]= document.getElementById("pp"+i);
    }
    for (let i=1;i<listes.length;i++){
        listes[i].addEventListener('click', function() {
        
        document.getElementById('MyDiv').removeChild(listes[i])
        document.getElementById('MyDiv2').appendChild(listes[i]);

        });
    }
}
tagger()
formatTags();