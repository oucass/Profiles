// Function from https://stackoverflow.com/a/52980440
function getElementsByClassName(className, node = document) {
  var nodeArray = [];

  if (node.classList && node.classList.contains(className)) {
    nodeArray.push(node);
  }
  if (node.children) {
    for (var i = 0; i < node.children.length; i++) {
      nodeArray = nodeArray.concat(getElementsByClassName(className, node.children[i]));
    }
  }
  return nodeArray;
}

var methods = getElementsByClassName("function");
var i;

alert(methods.length)

for (i = 0; i < methods.length; i++) {
  methods[i].addEventListener("click", function() {
    alert("clicked!")
    this.classList.toggle("active");
    var content = this.dd;
    if (content.style.display === "block") {
      content.style.display = "none";
    } else {
      content.style.display = "block";
    }
  });
}