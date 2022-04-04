function formatTags() {
    var elements = document.getElementsByClassName('body');
    //let replacedText = bodyText.replace(/\s\#(.*?)(\s|$)/g, ` <a href="/social/explore?query=${words[j].substring(1)}">${words[j]}</a>`);
    for (let i = 0; i < elements.length; i++) {
      let bodyText = elements[i].children[0].innerText;
      let words = bodyText.split(' ');
      for (let j = 0; j < words.length; j++) {
        if (words[j][0] === '#') {
          replacedText = bodyText.replace(/\s\#(.*?)(\s|$)/g, ` <a href="#">${words[j]}</a>`);
          elements[i].innerHTML = replacedText
        }
      }
    }
  }
  formatTags();
