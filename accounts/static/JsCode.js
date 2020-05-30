console.log('script at outside');
function close(targetTabClass, switchTabClass){
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName(targetTabClass);
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName(switchTabClass);
  console.log(tablinks.length)
  for (i = 0; i < tablinks.length; i++) {

    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }
}
function openCity(evt, cityName) {
  close()
  document.getElementById(cityName).style.display = "block";
  evt.currentTarget.className += " active";
}

function openTab(buttonId, tabId, targetTabClass, switchTabClass) {
  close(targetTabClass, switchTabClass)
  document.getElementById(tabId).style.display = "block";
  document.getElementById(buttonId).className +=" active";

}

function showDbAb() {
  var x = document.getElementById("barSizeNo").value;
  var array=x.split(",");
  document.getElementById("DbAb").innerHTML ="&nbsp;A<sub>b</sub>="+array[2]+
  "<span class='unit'>&nbsp;cm<sup>2</sup></span>";

}

function changeColor(className,id,currentColor,newColor) {
  var x = document.getElementsByClassName(className);
  for (i = 0; i < x.length; i++) {
  x[i].style.backgroundColor = currentColor;
}

document.getElementById(id).style.backgroundColor =newColor ;
}

function insertAfter(referenceNode, newNode) {
    referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
}
function loadOrder(){
  var y = document.getElementsByClassName('load');
  for (j = 0; j < y.length; j++){
     y[j].id='load'+j;
     y[j].setAttribute("onclick","changeColor(this.className,this.id,'rgb(255,255,255)','rgb(0,120,215)')");
  }
  var z=document.getElementsByClassName('loadNo');
  for (k=0; k < z.length; k++){
  z[k].innerHTML=k+1;
  }

}
function insertLoad()
{
  var x = document.getElementsByClassName('load');

  for (i = 0; i < x.length; i++)
  {
   if (x[i].style.backgroundColor=="rgb(0, 120, 215)")
   {
      var el = document.createElement("div");
      el.className='load';
      var loadNo=i+1;
      var loadPu=document.getElementById('Pu').value;
      var loadMux=document.getElementById('Mux').value;
      var loadMuy=document.getElementById('Muy').value;
      var str='<table style="width:100%"><tr><th><p  class="english-content loadNo" style="margin:0px;">'+loadNo+'</p></th><th><p class="english-content" style="margin:0px;">'+loadPu+'</p></th><th><p class="english-content" style="margin:0px;">'+loadMux+'</p></th><th><p class="english-content" style="margin:0px;">'+loadMuy+'</p></th></tr></table>';
       el.innerHTML =str;
       insertAfter(x[i],el);
       break;


    }
  }
  loadOrder();
  document.getElementById('load'+loadNo).click();
}
function deleteLoad()
{

var x = document.getElementsByClassName('load');
var len =x.length-1;
 for (i = 1; i < x.length; i++)
  {
   if (x[i].style.backgroundColor=="rgb(0, 120, 215)")
   {
      x[i].parentNode.removeChild(x[i]);
      loadOrder();
      if (i==len){
      var clickedLoad=i-1;}else{
      var clickedLoad=i;
      }

      document.getElementById('load'+clickedLoad).click();
      break;
   }
  }

}
function modifyLoad(){

var x = document.getElementsByClassName('load');
var len =x.length-1;
 for (i = 1; i < x.length; i++)
  {
   if (x[i].style.backgroundColor=="rgb(0, 120, 215)")
   {
      var el = document.createElement("div");
      el.className='load';
      var loadNo=i;
      var loadPu=document.getElementById('Pu').value;
      var loadMux=document.getElementById('Mux').value;
      var loadMuy=document.getElementById('Muy').value;
      var str='<table style="width:100%"><tr><th><p  class="english-content loadNo" style="margin:0px;">'+loadNo+'</p></th><th><p class="english-content" style="margin:0px;">'+loadPu+'</p></th><th><p class="english-content" style="margin:0px;">'+loadMux+'</p></th><th><p class="english-content" style="margin:0px;">'+loadMuy+'</p></th></tr></table>';
       el.innerHTML =str;
       x[i].parentNode.removeChild(x[i]);
       insertAfter(x[i-1],el);
       break;
   }
  }
  loadOrder();
  document.getElementById('load'+loadNo).click();
}

function sectionDrawing(){
//混凝土斷面繪製
console.log('sectionDrawing');
var Dx=document.getElementById('Dx');
var Dy=document.getElementById('Dy');
var svgElement=document.getElementById('sectionSvg');
var k=1.1;
var Vx=k*Math.max(Dx.value,Dy.value);
var Vy=k*Math.max(Dx.value,Dy.value);
var x0=(Vx/2-Dx.value/2);
var y0=(Vy/2-Dy.value/2);
svgElement.setAttribute("viewBox","0 0 " + Vx + " " + Vy);
svgElement.innerHTML='<rect x='+x0+' y='+y0+' width='+Dx.value+' height='+Dy.value+' style="fill:rgb(200,200,200);stroke-width:0.2;stroke:rgb(50,50,50)" />';

//鋼筋繪製
var nxElement=document.getElementById('nx');
var nyElement=document.getElementById('ny');
var barSizeNoElement=document.getElementById('barSizeNo');
var coverElement=document.getElementById('cc');
var nx = parseInt(nxElement.value);
var ny = parseInt(nyElement.value);
var barInformation = barSizeNoElement.value.split(",");
var db = parseFloat(barInformation[1]);
var As = parseFloat(barInformation[2]);
var cover = parseFloat(coverElement.value);
if ( nxElement.value>=2 && nyElement.value>=2 && Dx.value>0 && Dy.value>0 && cover > 0) {
    barCoord=barCoordinate(Dx.value,Dy.value,nx,ny,db,cover);
    for (i=0;i<barCoord.x.length;i++){
        var xv=barCoord.x[i]+Vx/2;
        var yv=Vy/2-barCoord.y[i];
        svgElement.innerHTML+= '<circle cx='+xv+' cy='+yv+' r='+db/2+' fill="black" />';
    }
}



}

function barCoordinate(Dx, Dy, nx, ny, db, cover) {
  var nTotal = 2 * nx + (ny - 2) * 2;
  var Sxt = Dx - 2 * cover - db;
  var Syt = Dy - 2 * cover - db;
  var Sx = Sxt / (nx - 1);
  var Sy = Syt / (ny - 1);
  var xBar = new Array();
  var yBar = new Array();
  xBar[0] = Sxt / 2;
  yBar[0] = Syt / 2;
  for (i = 1; i < nTotal; i++) {
    xBar[i] = xBar[i - 1];
    yBar[i] = yBar[i - 1];
    if (i < nx) {
      xBar[i] = xBar[i - 1] - Sx;
    } else if (i >= nx && i < nx + ny - 1) {
      yBar[i] = yBar[i - 1] - Sy;
    } else if (i >= nx + ny - 1 && i < 2 * nx + ny - 2) {
      xBar[i] = xBar[i - 1] + Sx;
    } else {
      yBar[i] = yBar[i - 1] + Sy;
    }
  }

  return { "x":xBar, "y":yBar };
}

function writingInputToText (event)
{
  var textAreaElem = document.getElementById('inputTextarea');
  var inputDataElem = document.getElementsByClassName('inputData');
  var inputLoadElem= document.getElementsByClassName('load');
  textAreaElem.value ="";
  for (i=0;i<=3;i++)
  {
    if ( inputDataElem.value === "undefined" )
    {

    } else {
        textAreaElem.value += inputDataElem[i].value + '\n';
    };
  }
  var nxElement=document.getElementById('nx');
  var nyElement=document.getElementById('ny');
  var barSizeNoElement=document.getElementById('barSizeNo');
  var coverElement=document.getElementById('cc');
  var nx = parseInt(nxElement.value);
  var ny = parseInt(nyElement.value);
  var barInformation = barSizeNoElement.value.split(",");
  var db = parseFloat(barInformation[1]);
  var As = parseFloat(barInformation[2]);
  var cover = parseFloat(coverElement.value);
  var Dx=document.getElementById('Dx');
  var Dy=document.getElementById('Dy');
  if (nxElement.value>=2 && nyElement.value>=2 && Dx.value>0 && Dy.value>0 && cover > 0)
  {
    barCoord=barCoordinate(Dx.value,Dy.value,nx,ny,db,cover);
    for (k=0;k<barCoord.x.length;k++)
    {
      barCoord.x[k] = Math.round(parseFloat(barCoord.x[k])*100)/100 ;
      barCoord.y[k] = Math.round(parseFloat(barCoord.y[k])*100)/100 ;
    }

    textAreaElem.value += db + '\n';
    textAreaElem.value += As + '\n';
    textAreaElem.value +=  barCoord.x + '\n';
    textAreaElem.value +=  barCoord.y + '\n';
  }
  for (j=1;j<inputLoadElem.length;j++)
  {
    var loadJ = inputLoadElem[j].getElementsByTagName("p");
    for (k=0;k<loadJ.length;k++)
    {
      textAreaElem.value += loadJ[k].innerHTML+";";
    }
    textAreaElem.value += '\n';
  }

}

function alphaBetaCalculate()
{
  var fc =parseFloat(document.getElementById('fc').value);
  var alpha = 0.85-0.00022*(fc -560);
  var beta = 0.85-0.00071*(fc -280);
  if (alpha > 0.85){alpha =0.85};
  if (alpha < 0.7){alpha =0.7};
  if (beta > 0.85){beta =0.85};
  if (beta < 0.65){beta =0.65};
  document.getElementById('alphaValue').innerHTML =Math.round(alpha*1000)/1000;
  document.getElementById('betaValue').innerHTML =Math.round(beta*1000)/1000;

}


function yieldStrainCalculate()
{
var fy =parseFloat(document.getElementById('fy').value);
var yieldStrain = fy/(2.04 *Math.pow(10,6));
document.getElementById('yieldStrainValue').innerHTML =Math.round(yieldStrain*100000)/100000;
}
















