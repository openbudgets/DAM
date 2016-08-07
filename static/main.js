/**
 * 
 */

/*
var dimensionLst = [];
var checkedDimDict1 = {};
var checkedDimDict9 = {};
*/


$(document).ready(function() {

})


function remove_options(selectbox)
{
	while(selectbox.firstChild){
		selectbox.removeChild(selectbox.firstChild);
	 }/*
    var i;
    for(i = selectbox.options.length - 1 ; i >= 0 ; i--)
    {
        selectbox.remove(i);
    }*/
}

function remove_options_of_selectboxId(select_box_Id)
{
	var select_box = document.getElementById(select_box_Id);
    for(var i = select_box.options.length - 1 ; i >= 0 ; i--)
    {
        select_box.remove(i);
    }
}

function add_options_to_selection(select, opLst){
	//dimensionLst = opLst;
	var option = document.createElement("option");
	option.text = "";
	select.appendChild(option);
	for (var i=0; i < opLst.length; i++){

		var op = opLst[i];
		//checkedDimDict1[op] = false;
		//checkedDimDict9[op] = false;
		//console.log('checkedDimDict1',op);
		//console.log('checkedDimDict9',op);
		var option = document.createElement("option");
		option.text = op.split('/').slice(-1)[0];
		select.appendChild(option);
	}
}

function get_all_names_of_options(select_box_ID){
	var select_box = document.getElementById(select_box_ID);
	var rlt = [];
	for (var i = 0; i < select_box.length; i++) {
		var option_text = select_box.options[i].text;
		if (option_text !== ''){
			rlt.push(option_text);
		}
	}
	return rlt
}

function create_dim_checkboxes(idStr) {

    var container = document.getElementById(idStr);
	var dimensionLst = get_all_names_of_options("observe_dimension");
	console.log('create_dim_checkboxes', dimensionLst);
    for (var i = 0; i < dimensionLst.length; i++) {

        var dim1 = dimensionLst[i];
        var checkbox = document.createElement('input');
        checkbox.type = "checkbox";
        checkbox.name = "chk" + dimensionLst[i];
        checkbox.value =  dimensionLst[i];
        checkbox.id = "chk" + dimensionLst[i];

        /*checkbox.onclick = (function(ele) {
            return function () {
                console.log('in create checkboxes', ele);
                console.log(checkboxVar,checkboxVar[ele]);
                checkboxVar[ele] = !checkboxVar[ele];
                console.log(checkboxVar,checkboxVar[ele]);
            };
        }(dim1));
        */

        var label = document.createElement('label');
        label.htmlFor = "chk" + dimensionLst[i];
        label.appendChild(document.createTextNode(dimensionLst[i]));

        container.appendChild(checkbox);
        container.appendChild(label);
        var nline = document.createElement('br');
		container.appendChild(nline);
    }

}

function get_selected_dims(checkboxID){
	var lst = [];
	console.log('in get_selected_dims ', checkboxID);
	var select_box = document.getElementById(checkboxID);
	var rlt = [];
	for (var i = 0; i < select_box.children.length; i++) {
		if (select_box.children[i].type && select_box.children[i].type === 'checkbox') {
			var option_text = select_box.children[i].value;
			if (select_box.children[i].checked) {
				rlt.push(option_text);
			}
		}
	}
	console.log('selected dims: ', rlt);
	return rlt

}


function plot_graph(containerId, matrix, labels, my_title, dim){
	//{'data': X, 'cluster': labels, 'my_title': 'data set name', dim: ['functinalClassification']}
	var clusters = new Set(labels);
	clusters = Array.from(clusters);
	console.log('clusters ', clusters);
	var colors = ['rgb(228,26,28)','rgb(55,126,184)','rgb(77,175,74)',
	              'rgb(228,126,28)','rgb(55,126,84)','rgb(177,175,74)',
	              'rgb(28,126,28)','rgb(155,126,84)','rgb(177,75,74)',
	              'rgb(128,126,28)','rgb(255,126,84)','rgb(277,75,74)'];

	function select_data_in_cluster(rows, cluster){
		rlt = [];
		for (var i=0; i<rows.length; i++){
			if (labels[i] === cluster){
				rlt.push(rows[i])
			}
		}
		return rlt
	}

	function unpack(rows, col) {
        return rows.map(function(row) { return row[col]; });
    }

	var data=[];
	for (var i=0; i < clusters.length; i++ ){
		var clusteredMatrix = select_data_in_cluster(matrix, clusters[i]);
		var trace = {
		        x: unpack(clusteredMatrix, '0'),
		        y: unpack(clusteredMatrix, '1'),
		        z: unpack(clusteredMatrix, '2'),
		        mode: 'markers',
		        type: 'scatter3d',
		        name: 'Cluster '+ i.toString(),
		        marker: {
		          color: colors[i],//'rgb(23, 190, 207)', //depend on labels!
		          size: 2
		        }
		    };
		console.log(trace);
		data.push(trace)
	}
	console.log(data);
	    var layout = {
	    	title: my_title,
	        autosize: true,
	        height: 960,
	        scene: {
	            aspectratio: {
	                x: 1,
	                y: 1,
	                z: 1
	            },
	            camera: {
	                center: {
	                    x: 0,
	                    y: 0,
	                    z: 0
	                },
	                eye: {
	                    x: 1.25,
	                    y: 1.25,
	                    z: 1.25
	                },
	                up: {
	                    x: 0,
	                    y: 0,
	                    z: 1
	                }
	            },
	            xaxis: {
	            	title: dim[0],
	                type: 'linear',
	                zeroline: false
	            },
	            yaxis: {
	            	title: dim[1],
	                type: 'linear',
	                zeroline: false
	            },
	            zaxis: {
	            	title: 'Measure',
	                type: 'linear',
	                zeroline: false
	            }
	        },
	        title: my_title,
	        width: 800
	};

	 Plotly.newPlot(containerId, data, layout);//newPlot(containerId, data, layout);
}

function plot_2Dgraph(containerId, jsonData, dataset_name, dim){
	//{'in_x':inliersLst_x, 'in_y': inliersLst_y, 'out_x':outliersLst_x, 'out_y': outliersLst_y}
	var d3 = Plotly.d3;
	var x_in = jsonData['in_x'];
	var y_in  = jsonData['in_y'];
	var x_out = jsonData['out_x'];
	var y_out = jsonData['out_y'];
	var data= [{
					x: jsonData['in_x'],
					y: jsonData['in_y'],
					name: "Inliers",
					mode: 'markers'
				},
				{
					x: jsonData['out_x'],
					y: jsonData['out_y'],
					name: "Outliers",
					mode: 'markers'
				}];

	var layout = {
			title: dataset_name,
		    shapes: [
		        {
		            type: 'square',
		            xref: 'x',
		            yref: 'y',
		            x0: d3.min(x_in),
		            y0: d3.min(y_in),
		            x1: d3.max(x_in),
		            y1: d3.max(y_in),
		            opacity: 0.2,
		            fillcolor: 'blue',
		            line: {
		                color: 'blue'
		            }
		        },
		        {
		            type: 'square',
		            xref: 'x',
		            yref: 'y',
		            x0: d3.min(x_out),
		            y0: d3.min(y_out),
		            x1: d3.max(x_out),
		            y1: d3.max(y_out),
		            opacity: 0.4,
		            fillcolor: 'red',
		            line: {
		                color: 'red'
		            }
		        }
		    ],
		    height: 800,
		    width: 960,
		    //showlegend: false,
			xaxis: {
					title: dim[0],
					titlefont: {
						family: 'Courier New, monospace',
						size: 18,
						color: '#7f7f7f'
					}
				},

		 	yaxis: {
					title: "Amount",
					titlefont: {
						family: 'Courier New, monospace',
						size: 18,
						color: '#7f7f7f'
				}
			}

		};

	Plotly.newPlot(containerId, data, layout);
}

function plot_2D_trend_graph(containerId, jsonData, dataset_name){
	var trend_data = jsonData['trend'];
	var observed_data = jsonData['observed'];
	var seasonal_data = jsonData['seasonal'];
	var residual_data = jsonData['residual'];

	var trend_xlst = new Array();
	var trend_ylst = new Array();

	var observed_xlst = new Array();
	var observed_ylst = new Array();

	var seasonal_xlst = new Array();
	var seasonal_ylst = new Array();

	var residual_xlst = new Array();
	var residual_ylst = new Array();

	for (var key in trend_data) {
		trend_xlst.push(key);
		trend_ylst.push(trend_data[key]);
	}

	for (var key in observed_data) {
		observed_xlst.push(key);
		observed_ylst.push(observed_data[key]);
	}

	for (var key in seasonal_data) {
		seasonal_xlst.push(key);
		seasonal_ylst.push(seasonal_data[key]);
	}

	for (var key in residual_data) {
		residual_xlst.push(key);
		residual_ylst.push(residual_data[key]);
	}

	var trace_trend = {
		x: trend_xlst,
		y: trend_ylst,
		type: 'scatter',
		name: 'trend'
	};

	var trace_observed = {
		x: observed_xlst,
		y: observed_ylst,
		xaxis: 'x2',
		yaxis: 'y2',
		type: 'scatter',
		name: 'observed'
	};

	var trace_seasonal = {
		x: seasonal_xlst,
		y: seasonal_ylst,
		xaxis: 'x3',
		yaxis: 'y3',
		type: 'scatter',
		name: 'seasonal'
	};

	var trace_residual = {
		x: residual_xlst,
		y: residual_ylst,
		xaxis: 'x4',
		yaxis: 'y4',
		type: 'scatter',
		name: 'residual'
	};


	var data = [trace_trend, trace_observed, trace_seasonal, trace_residual];

	var layout = {
		xaxis: {domain: [0, 0.45]},
		yaxis: {domain: [0, 0.45]},
		xaxis4: {
			domain: [0.55, 1],
			anchor: 'y4'
		},
		xaxis3: {
			domain: [0, 0.45],
			anchor: 'y3'
		},
		xaxis2: {domain: [0.55, 1]},
		yaxis2: {
			domain: [0, 0.45],
			anchor: 'x2'
		},
		yaxis3: {domain: [0.55, 1]},
		yaxis4: {
			domain: [0.55, 1],
			anchor: 'x4'
		}
	};

	Plotly.newPlot(containerId, data, layout)
}

function show_statistics_graph(containerId, jsonData, my_title){
	//jsonData: {'xlst':xlst,'ylst':ylst, 'mean': ymean, 'std':ystd, 'min': ymin, 'max': ymax, 'dimlst': dimlst}
	//containerId
	console.log('jsonData', jsonData);
	var num = jsonData['xlst'].length;
	var ymlst = [];
	for (var i = 0 ; i < num; i++){
		ymlst.push(jsonData['mean'])
	}
	var yminlst = [];
	for (var i = 0 ; i < num; i++){
		yminlst.push(jsonData['min'])
	}
	var ymaxlst = [];
	for (var i = 0 ; i < num; i++){
		ymaxlst.push(jsonData['max'])
	}
	var trace1 = {
			x: jsonData['xlst'],
			y: jsonData['ylst'],
			mode: 'markers',
			name: 'simple value'
			//type: 'scatter'
	};
	var trace2 = {
		x: jsonData['xlst'],
		y: ymlst,
		name: 'mean ' + jsonData['mean'].toString(),
		type: 'scatter'
	};
	var trace3 = {
		x: jsonData['xlst'],
		y: yminlst,
		name: 'minimum ' + jsonData['min'].toString(),
		type: 'scatter'
	};
	var trace4 = {
		x: jsonData['xlst'],
		y: ymaxlst,
		name: 'maximum ' + jsonData['max'].toString(),
		type: 'scatter'
	};
	var data = [trace1, trace2, trace3, trace4];
	var layout = {
		title: my_title,
		xaxis: {
			title: "Total "+num.toString()+" Observation",
			titlefont: {
				family: 'Courier New, monospace',
				size: 18,
				color: '#7f7f7f'
			}
		},

		yaxis: {
			title: "Amount",
			titlefont: {
				family: 'Courier New, monospace',
				size: 18,
				color: '#7f7f7f'
			}
		}
	};

	Plotly.newPlot(containerId, data, layout)

}