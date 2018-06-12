function makeChart(info){
	var metrics = info['metrics'];
	var accuracy = metrics[0];
	var recall = metrics[1]; 
	var precision = metrics[2];
	var f1 = metrics[3];
	var points = info['points'];
	var false_negatives = metrics[4][1][0];
	var false_positives = metrics[4][0][1];
	var true_negatives = metrics[4][0][0];
	var true_positives = metrics[4][1][1];

	accuracy = round(accuracy * 100, 2);
	precision = round(precision * 100, 2);
	recall = round(recall * 100, 2);
	f1 = round(f1 * 100, 2);


	container = document.getElementById("results-container");
	container.style.display = "block";

	var ctx = document.getElementById("barChart");
	var ctx2 = document.getElementById("lineChart");
	var ctx3 = document.getElementById("pieChart");

	if (ctx != null && ctx2 != null && ctx3 != null){
		ctx.parentNode.removeChild(ctx);
		ctx2.parentNode.removeChild(ctx2);
		ctx3.parentNode.removeChild(ctx3);
		ctx = document.createElement('canvas');
		ctx2 = document.createElement('canvas');
		ctx3 = document.createElement('canvas');
		ctx.setAttribute('id', 'barChart');
		ctx2.setAttribute('id', 'lineChart');
		ctx3.setAttribute('id', 'pieChart');
		container.appendChild(ctx3);
		container.appendChild(ctx);
		container.appendChild(ctx2);
	}
	var myChart = new Chart(ctx, {
	    type: 'horizontalBar',
	    data: {
	        labels: ["Accuracy (" + accuracy + "%)", "Recall (" + recall + "%)", "Precision (" + precision + "%)", "F1 Score (" + f1 + "%)"],
	        datasets: [{
	        	label: "Percent of test examples",
	            data: [accuracy, recall, precision, f1],
	            backgroundColor: [
	            	'rgba(35, 150, 102, 0.2)',
	                'rgba(255, 99, 132, 0.2)',
	                'rgba(54, 162, 235, 0.2)',
	                'rgba(255, 206, 86, 0.2)',
	            ],
	            borderColor: [
	            	'rgba(35, 150, 102, 1)',
	                'rgba(255,99,132,1)',
	                'rgba(54, 162, 235, 1)',
	                'rgba(255, 206, 86, 1)',
	            ],
	            borderWidth: 1
	        }]
	    },
	    options: {
	    	animation: {duration: 6000},
	    	title: {text: "Accuracy Metrics", display: true, fontSize: 20, fontColor: '#FFFFFF', padding: 20, fontStyle: 'normal'},
	    	legend: {display: false},
	    	barThickness: 20,
	        scales: {
	            xAxes: [{
	                ticks: {
	                    beginAtZero:true
	                },
	                scaleLabel: {display: true, labelString: "Percent of Test Examples"}
	            }]
	        }
	    }
	});




	
	var myChart2 = new Chart(ctx2, {
	    type: 'line',
	    data: {
	        datasets: [{
	        	label: "Rate of total positives at this false positive rate",
	            data: points,
	            backgroundColor: [
	                'rgba(35, 150, 102, 0.2)'
	            ],
	            borderColor: [
	                'rgba(35, 150, 102, 1)'
	            ],
	            borderWidth: 3,
	            lineTension: 1,
	            pointRadius: 0,
	            spanGaps: true,
	            pointBorderColor: 'rgba(35, 150, 102, 1)',
	            pointBackgroundColor: 'rgba(35, 150, 102, 1)',
	            pointHoverBorderColor: 'rgba(35, 150, 102, 1)',
	            pointHoverBackgroundColor: 'rgba(35, 150, 102, 1)',
	        }]
	    },
	    options: {
	    	animation: {duration: 7000},
	    	title: {text: "ROC Curve (area = " + round(info['roc_auc'], 3) + ")", display: true, fontSize: 20, fontColor: '#FFFFFF', padding: 20, fontStyle: 'normal'},
	    	legend: {display: false},
	    	scales: {
	    	            xAxes: [{
	    	                type: 'linear',
	    	                position: 'bottom',
	    	                scaleLabel: {display: true, labelString: "False Positive Rate"}
	    	            }],
	    	            yAxes: [{
	    	                scaleLabel: {display: true, labelString: "Total Positive Rate"}
	    	            }]
	    	        }
	    }
	});

	var myChart3 = new Chart(ctx3, {
    type: 'doughnut',
    data: {
    	datasets: [{
    		data: [true_positives + true_negatives, false_positives, false_negatives],
    		backgroundColor: [
    			'rgba(92, 184, 92, 1)',
    			'rgba(240, 173, 78, 1)',
    			'rgba(217, 83, 79, 1)',
    		],
    		borderColor: [
    			'rgba(92, 184, 92, .2)',
    			'rgba(240, 173, 78, .2)',
    			'rgba(217, 83, 79, .2)',
    		],
    		borderWidth: [0, 0, 0]

    	}],
    	labels: ["Correctly classified", "False positives: incorrectly classified, benign", "False negatives: incorrectly classified, malignant"]
    },
    options: {
    	"animation": {duration: 3500},
    	title: {text: "Anomaly Detection Results", display: true, fontSize: 20, fontColor: '#FFFFFF', padding: 20, fontStyle: 'normal'},
    }
});
}

function populateBoxes(info){
	console.log(info);
	left = document.getElementById("left");
	mid = document.getElementById("mid");
	right = document.getElementById("right");

	auc = round(info['roc_auc'], 3).toString()
	if (auc.length > 1 && auc[0] == '0')
		auc = auc.substring(1);
	tpp = round(info['time'], 3).toString();
	if (tpp.length > 1 && tpp[0] == '0')
		tpp = tpp.substring(1);
	kpi = round(info['roc_auc'] / info['time'], 2).toString();
	if (kpi.length > 1 && kpi[0] == '0')
		kpi = kpi.substring(1);

	left.innerText = auc;
	mid.innerText = tpp;
	right.innerText = kpi;
}



function sendRequest(){
	model = document.getElementById("model").value;
	dataset = document.getElementById("dataset").value;
	var http = new XMLHttpRequest();
	var url = "/predict";
	dict = {'model': model, 'dataset': dataset}
	var params = JSON.stringify(dict);
	http.open("POST", url, true);

	//Send the proper header information along with the request
	http.setRequestHeader("Content-type", "application/json");

	removeProgress();
	initializeProgress();

	message = document.getElementById("message");
	message.innerText = "Simulating packets";
	var loadingDots = document.getElementById("loading-dots");
	loadingDots.style.display = "inline";
	container = document.getElementById("results-container");
	container.style.display = "none";
	var button = document.getElementById("simulate-button");
	button.style.display = "none";
	// http.onreadystatechange = function() {//Call a function when the state changes.
	//     if(http.readyState == 4 && http.status == 200) {
	    	
	//     }
	// }
	http.send(params);
	var position = 1;

	var totalLength = -1;

	function handleNewData() {
	    // the response text include the entire response so far
	    // split the messages, then take the messages that haven't been handled yet
	    // position tracks how many messages have been handled
	    // messages end with a newline, so split will always show one extra empty message at the end
	    var messages = http.responseText.split('\n');
	    if (totalLength == -1 && messages.length > 0 && messages[0] != "") {
	    	var info = JSON.parse(messages[0]);
	    	totalLength = info['length'];
	    }
	    messages.slice(position, -1).forEach(function(value) {
	    	addToProgress(JSON.parse(value), totalLength);
	    });
	    position = Math.max(messages.length - 1, 1);
	}

	var timer;
    timer = setInterval(function() {
    	handleNewData();
        if (http.readyState == XMLHttpRequest.DONE) {
            clearInterval(timer);
            var responses = http.responseText.split('\n');

            response = JSON.parse(responses[responses.length - 1]);
            response.totalLength = totalLength;
        	loadingDots.style.display = "none";
        	message.innerHTML = "";
        	button.style.display = "inline-block";
        	populateBoxes(response);
            makeChart(response);
        }
    }, 300);
}

function updateDes(){
	var modelSelect = document.getElementById('model');
	var dataSelect = document.getElementById('dataset');

	var modelDes = document.getElementById('model-des');
	var dataDes = document.getElementById('dataset-des');
	modelDes.innerHTML = "<b>" + modelSelect.options[modelSelect.selectedIndex].text + ":</b> " + modelSelect.options[modelSelect.selectedIndex].title;
	dataDes.innerHTML = "<b>" + dataSelect.options[dataSelect.selectedIndex].text + ":</b> " + dataSelect.options[dataSelect.selectedIndex].title;

}


function clearDes(){
	var modelDes = document.getElementById('model-des');
	var dataDes = document.getElementById('dataset-des');
	modelDes.innerText = "";
	dataDes.innerText = "";
}

function addToProgress(update, totalLength){
	var wrapper = document.getElementById('bar-wrapper');
	var node = document.createElement("div");
	if (update["label"] == update["output"]){
		node.className = "progress-bar progress-bar-success";
	} else if (update['label'] == 0 && update['output'] == 1) {
		node.className = "progress-bar progress-bar-warning";
	} else {
		node.className = "progress-bar progress-bar-danger";
	}
	node.style.width = 103.0 / totalLength + "%";
	wrapper.appendChild(node);
}

function removeProgress(){
	var wrapper = document.getElementById('bar-wrapper');
	while (wrapper.firstChild) {
	    wrapper.removeChild(wrapper.firstChild);
	}	
}

function initializeProgress(){
	var section = document.getElementById('progress-section');
	section.style.display = "block";
}


function round(number, precision) {
  var shift = function (number, precision, reverseShift) {
    if (reverseShift) {
      precision = -precision;
    }  
    var numArray = ("" + number).split("e");
    return +(numArray[0] + "e" + (numArray[1] ? (+numArray[1] + precision) : precision));
  };
  return shift(Math.round(shift(number, precision, false)), precision, true);
}