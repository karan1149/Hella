function makeChart(info){
	var metrics = info['metrics'];
	var accuracy = metrics[0];
	var recall = metrics[1]; 
	var precision = metrics[2];
	var points = info['points'];

	container = document.getElementById("results-container");
	container.style.display = "block";

	var ctx = document.getElementById("barChart");
	var ctx2 = document.getElementById("lineChart");

	if (ctx != null && ctx2 != null){
		ctx.parentNode.removeChild(ctx);
		ctx2.parentNode.removeChild(ctx2);
		ctx = document.createElement('canvas');
		ctx2 = document.createElement('canvas');
		ctx.setAttribute('id', 'barChart');
		ctx2.setAttribute('id', 'lineChart');
		container.appendChild(ctx);
		container.appendChild(ctx2);
	}
	var myChart = new Chart(ctx, {
	    type: 'horizontalBar',
	    data: {
	        labels: ["Accuracy", "Recall", "Precision"],
	        datasets: [{
	        	label: "Fraction of test examples",
	            data: [accuracy, recall, precision],
	            backgroundColor: [
	                'rgba(255, 99, 132, 0.2)',
	                'rgba(54, 162, 235, 0.2)',
	                'rgba(255, 206, 86, 0.2)',
	            ],
	            borderColor: [
	                'rgba(255,99,132,1)',
	                'rgba(54, 162, 235, 1)',
	                'rgba(255, 206, 86, 1)',
	            ],
	            borderWidth: 1
	        }]
	    },
	    options: {
	    	animation: {duration: 2000},
	    	title: {text: "Accuracy Metrics", display: true, fontSize: 20, fontColor: '#FFFFFF', padding: 20, fontStyle: 'normal'},
	    	legend: {display: false},
	    	barThickness: 20,
	        scales: {
	            xAxes: [{
	                ticks: {
	                    beginAtZero:true
	                },
	                scaleLabel: {display: true, labelString: "Fraction of Test Examples"}
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
	            pointRadius: 0
	        }]
	    },
	    options: {
	    	animation: {duration: 2000},
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
}

function populateBoxes(info){
	left = document.getElementById("left");
	mid = document.getElementById("mid");
	right = document.getElementById("right");

	auc = round(info['roc_auc'], 3).toString()
	auc = auc[0] == '0' ? auc.substring(1) : auc;
	tpp = round(info['time'], 3).toString();
	tpp = tpp[0] == '0' ? tpp.substring(1) : tpp;
	kpi = round(info['roc_auc'] / info['time'], 2).toString();
	kpi = kpi[0] == '0' ? kpi.substring(1) : kpi;

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
	message = document.getElementById("message");
	message.innerText = "Simulating packets";
	var loadingDots = document.getElementById("loading-dots");
	loadingDots.style.display = "inline";
	container = document.getElementById("results-container");
	container.style.display = "none";
	http.onreadystatechange = function() {//Call a function when the state changes.
	    if(http.readyState == 4 && http.status == 200) {
	    	response = JSON.parse(http.response);
	    	console.log(response);
	    	loadingDots.style.display = "none";
	    	message.innerHTML = "";
	    	populateBoxes(response);
	        makeChart(response);
	    }
	}
	http.send(params);
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