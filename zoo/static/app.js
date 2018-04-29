function makeChart(accuracy, recall, precision){
	container = document.getElementById("chart-container");
	container.style.display = "block";

	var ctx = document.getElementById("myChart");
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
	    	legend: {display: false},
	    	barThickness: 20,
	        scales: {
	            xAxes: [{
	                ticks: {
	                    beginAtZero:true
	                }
	            }]
	        }
	    }
	});
}



function sendRequest(){
	model = document.getElementById("model").value
	dataset = document.getElementById("dataset").value
	var http = new XMLHttpRequest();
	var url = "/predict";
	dict = {'model': model, 'dataset': dataset}
	var params = JSON.stringify(dict);
	http.open("POST", url, true);

	//Send the proper header information along with the request
	http.setRequestHeader("Content-type", "application/json");
	message = document.getElementById("message");
	message.innerText = "Running packet simulation...";
	container = document.getElementById("chart-container");
	container.style.display = "none";
	http.onreadystatechange = function() {//Call a function when the state changes.
	    if(http.readyState == 4 && http.status == 200) {
	    	response = JSON.parse(http.response);
	    	console.log(response)
	    	metrics = response['metrics'];
	    	message.innerHTML = "Simulation complete in " + response.time + " seconds! ROC_AUC = " + response.roc_auc;
	        makeChart(metrics[0], metrics[1], metrics[2]);
	    }
	}
	http.send(params);
}