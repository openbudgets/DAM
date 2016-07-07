var app = angular.module('damTask', ['angularModalService']);

app.controller('taskController', ["$scope", "ModalService",
				  function($scope, ModalService) {
				      
				      $scope.configTA = function() {
					  ModalService.showModal({
					      templateUrl: 'modal.html',
					      controller: "ModalController",
					      inputs:{
						  name: "Fry",
						  year: 3001
					      }
					  }).then(function(modal) {
					  //    modal.element.modal();
					      modal.close.then(function(result) {
						  $scope.message = "You said " + result;
					      });
					  });
				      };
				      
				  }]);

app.controller('ModalController', function($scope, close) {
    $scope.close = function(result) {
 	close(result,500); // close, but give 500ms for bootstrap to animate
    };
});

/*
(function () {
    'use strict';
    angular.module('damTask', ['angularModalService'])
	.controller('taskController',
		    ['$scope', '$log', '$http', '$timeout', 

		     function($scope, ModalService) {
			 $scope.configTA = function() {
			     ModalService.showModal({
				 templateUrl: 'modal.html',
				 controller: "ModalController"
			     }).then(function(modal) {
				 modal.element.modal();
				 modal.close.then(function(result) {
				     $scope.message = "You said ";
				 });
			     });
			 };	 
		     },
		     
		     function($scope, $log, $http, $timeout) {
			 $scope.trendAnalysis = function() {
			     $log.log('in controller, trendAnalysis');
			     // get the URL from the input
			     var userInput = $scope.startYear;
			     // fire the API request
			     $log.log(userInput);
			     $http.post('/trend_analysis', {"taJson": startYear}).
				 success(function(results) {
				     $log.log(results);
				 }).
				 error(function(error) {
				     $log.log(error);
				 });
			 };
		  
		     }
		    ]);
}());

*/
