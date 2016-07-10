/**
 * 
 */

function remove_options(selectbox)
{
    var i;
    for(i = selectbox.options.length - 1 ; i >= 0 ; i--)
    {
        selectbox.remove(i);
    }
}

function add_options_to_selection(select, opLst){
	var option = document.createElement("option");
	option.text = "";
	select.appendChild(option);
	for (var i=0; i < opLst.length; i++){
		op = opLst[i];
		console.log(op);
		var option = document.createElement("option");
		option.text = op.split('/').slice(-1)[0];
		select.appendChild(option);
	} 
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
