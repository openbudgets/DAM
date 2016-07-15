/**
 * 
 */

dimensionLst = [] 
checkedDimDict = {}

function remove_options(selectbox)
{
    var i;
    for(i = selectbox.options.length - 1 ; i >= 0 ; i--)
    {
        selectbox.remove(i);
    }
}

function add_options_to_selection(select, opLst){
	dimensionLst = opLst;
	var option = document.createElement("option");
	option.text = "";
	select.appendChild(option);
	for (var i=0; i < opLst.length; i++){
		
		op = opLst[i];
		checkedDimDict[op] = false;
		console.log('checkedDimDict',op);
		var option = document.createElement("option");
		option.text = op.split('/').slice(-1)[0];
		select.appendChild(option);
	} 
}

function create_dim_checkboxes(idStr) {

    var container = document.getElementById(idStr);
    
    for (var i = 0; i < dimensionLst.length; i++) {

        var dim1 = dimensionLst[i]; 
        var checkbox = document.createElement('input');
        checkbox.type = "checkbox";
        checkbox.name = "chk" + dimensionLst[i];
        checkbox.value = "value";
        checkbox.id = "chk" + dimensionLst[i];

        checkbox.onclick = (function(ele) {
            return function () {
                console.log(ele);
                console.log('checkedDimDict['+ele+']',checkedDimDict[ele])
                checkedDimDict[ele] = !checkedDimDict[ele];
                console.log('checkedDimDict['+ele+']',checkedDimDict[ele]);
            };
        }(dim1))
 

        var label = document.createElement('label')
        label.htmlFor = "chk" + dimensionLst[i];
        label.appendChild(document.createTextNode(dimensionLst[i]));

        container.appendChild(checkbox);
        container.appendChild(label);
        var nline = document.createElement('br')
		container.appendChild(nline);
    }

}
 
function get_selected_dims(){
	var lst = [] 
	for (var key in checkedDimDict){
		var value=checkedDimDict[key]; 
		if (value){ 
			lst.push(key);
		}
	} 
	console.log('selected dims: ', lst);
	return lst
}


function plot_graph(container, data, classes=[]){
	//{'data': X, 'cluster': labels}
	
	
}

function show_statistics_graph(container, data){
	figjson = data;//.result;
	console.log(figjson);
	mpld3.draw_figure(container,figjson) ;
	/*var names = ['centripetal', 'chordal', 'uniform', 'disabled'];
	var items = data.result['d'];
	var ymean = data.result['m'];
	var ystd = data.result['s'];
	console.log(ymean, ystd);
		 
	var groups = new vis.DataSet();
	groups.add({
		  id: 0,
	        content: names[0],
	        options: {
	            drawPoints: false,
	            interpolation: {
	                parametrization: 'centripetal'
	            }
	        }});
	var dataset = new vis.DataSet(items);
	var options = {
			sort: false,
		      sampling:false,
		      style:'points',
		       
		      drawPoints: {
		          enabled: true,
		          size: 6,
		          style: 'circle' // square, circle
		      },
		      defaultGroup: 'Scatterplot',
		      height: '600px',
		      legend: true
		};
		 
	var graph2d = new vis.Graph2d(container, dataset,  options);
	*/
 
}
